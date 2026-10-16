#!/usr/bin/env python3
"""CRAN cohort analysis for niche software usage.

Builds creation cohorts from CRAN DB and measures equal-age cranlogs downloads
in days 31-180 after first publication. Network responses are cached under
./cache and all derived tables are written to ./data.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
DATA = ROOT / "data"
CACHE.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
UA = "where-is-the-software cran cohort research (polite cached; contact: seangoedecke)"
CRANDB_ALLALL = "https://crandb.r-pkg.org/-/allall"
CRANLOGS = "https://cranlogs.r-pkg.org/downloads"
START_DATE = dt.date(2021, 1, 1)
END_SUPPLY = dt.date(2026, 9, 30)  # Q4 2026 is partial at analysis date.
THRESHOLDS = (500, 2000, 20000)
RECENT_START = dt.date(2025, 7, 1)


def request_json(url: str, cache_path: Path | None = None, min_wait: float = 0.08):
    if cache_path and cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    last_err = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read()
            if cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                with cache_path.open("wb") as f:
                    f.write(data)
            time.sleep(min_wait)
            return json.loads(data.decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def parse_iso_date(s: str) -> dt.date | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def quarter(d: dt.date) -> str:
    return f"{d.year}Q{((d.month - 1) // 3) + 1}"


def half(d: dt.date) -> str:
    return f"{d.year}H{1 if d.month <= 6 else 2}"


def date_range_sum(prefix: dict[dt.date, int], start: dt.date, end: dt.date) -> int:
    return prefix.get(end, 0) - prefix.get(start - dt.timedelta(days=1), 0)


def latest_cranlogs_date() -> dt.date:
    data = request_json(f"{CRANLOGS}/total/last-day", CACHE / "cranlogs_last_day.json")
    return dt.date.fromisoformat(data[0]["end"])


def load_crandb() -> dict:
    path = CACHE / "crandb_allall.json"
    if not path.exists() and (ROOT / "crandb_allall.json").exists():
        # Reuse a manually fetched copy if present, then keep all future cache reads under ./cache.
        path.write_bytes((ROOT / "crandb_allall.json").read_bytes())
    return request_json(CRANDB_ALLALL, path, min_wait=0.0)


def extract_packages(allall: dict) -> list[dict]:
    rows = []
    for pkg, rec in allall.items():
        tl = rec.get("timeline") or {}
        dated_versions = [(ver, parse_iso_date(ts)) for ver, ts in tl.items() if ver != "archived"]
        dated_versions = [(v, d) for v, d in dated_versions if d]
        if not dated_versions:
            continue
        first_version, first_date = min(dated_versions, key=lambda x: x[1])
        if first_date < START_DATE or first_date > END_SUPPLY:
            continue
        versions = rec.get("versions") or {}
        first_meta = versions.get(first_version) or {}
        latest = rec.get("latest")
        latest_meta = versions.get(latest) or first_meta
        rows.append({
            "package": pkg,
            "first_version": first_version,
            "first_publication_date": first_date.isoformat(),
            "cohort_quarter": quarter(first_date),
            "cohort_half": half(first_date),
            "archived": bool(rec.get("archived", False)),
            "latest_version": latest or "",
            "title": (latest_meta.get("Title") or rec.get("title") or "").replace("\n", " "),
            "description": (latest_meta.get("Description") or first_meta.get("Description") or "").replace("\n", " "),
            "url": str(latest_meta.get("URL") or first_meta.get("URL") or ""),
            "bugreports": str(latest_meta.get("BugReports") or first_meta.get("BugReports") or ""),
        })
    rows.sort(key=lambda r: (r["first_publication_date"], r["package"].lower()))
    return rows


def write_csv(path: Path, rows: list[dict], fields: list[str]):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def load_download_rows(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {r["package"]: r for r in csv.DictReader(f)}


def fetch_daily_totals(start: dt.date, end: dt.date) -> dict[dt.date, int]:
    cache = CACHE / f"cranlogs_daily_total_{start}_{end}.json"
    data = request_json(f"{CRANLOGS}/daily/{start.isoformat()}:{end.isoformat()}", cache)
    totals = {}
    for item in data[0]["downloads"]:
        totals[dt.date.fromisoformat(item["day"])] = int(item["downloads"])
    return totals


def prefix_sums(daily: dict[dt.date, int]) -> dict[dt.date, int]:
    out = {}
    running = 0
    d = min(daily)
    end = max(daily)
    while d <= end:
        running += int(daily.get(d, 0))
        out[d] = running
        d += dt.timedelta(days=1)
    return out


def chunks_for_url(pkgs: list[str], max_url_len: int = 7000):
    chunk = []
    base_len = len(f"{CRANLOGS}/total/2000-01-01:2000-01-02/")
    cur_len = base_len
    for p in pkgs:
        add = len(urllib.parse.quote(p)) + (1 if chunk else 0)
        if chunk and cur_len + add > max_url_len:
            yield chunk
            chunk = [p]
            cur_len = base_len + len(urllib.parse.quote(p))
        else:
            chunk.append(p)
            cur_len += add
    if chunk:
        yield chunk


def fetch_package_totals(eligible: list[dict], latest: dt.date, mirror_prefix: dict[dt.date, int]) -> list[dict]:
    out_path = DATA / "package_download_windows.csv"
    existing = load_download_rows(out_path)
    rows_by_pkg = dict(existing)
    groups = defaultdict(list)
    for r in eligible:
        if r["package"] in rows_by_pkg:
            continue
        fd = dt.date.fromisoformat(r["first_publication_date"])
        start = fd + dt.timedelta(days=31)
        end = fd + dt.timedelta(days=180)
        if end <= latest:
            groups[(start, end)].append(r["package"])

    total_calls = sum(1 for pkgs in groups.values() for _ in chunks_for_url(sorted(pkgs)))
    done_calls = 0
    for (start, end), pkgs in sorted(groups.items()):
        for chunk in chunks_for_url(sorted(pkgs)):
            done_calls += 1
            key = hashlib.sha1((start.isoformat()+":"+end.isoformat()+":"+",".join(chunk)).encode()).hexdigest()[:16]
            cache = CACHE / "cranlogs_pkg_totals" / f"{start}_{end}_{key}.json"
            url = f"{CRANLOGS}/total/{start.isoformat()}:{end.isoformat()}/" + ",".join(urllib.parse.quote(p) for p in chunk)
            data = request_json(url, cache)
            for item in data:
                pkg = item.get("package")
                if not pkg:
                    continue
                total_mirror = date_range_sum(mirror_prefix, start, end)
                rows_by_pkg[pkg] = {
                    "package": pkg,
                    "window_start": start.isoformat(),
                    "window_end": end.isoformat(),
                    "downloads_31_180": int(item.get("downloads", 0)),
                    "mirror_downloads_31_180": total_mirror,
                }
            if done_calls % 100 == 0 or done_calls == total_calls:
                print(f"cranlogs package calls {done_calls}/{total_calls}; rows={len(rows_by_pkg)}", file=sys.stderr, flush=True)
                fields = ["package", "window_start", "window_end", "downloads_31_180", "mirror_downloads_31_180"]
                write_csv(out_path, list(rows_by_pkg.values()), fields)
    fields = ["package", "window_start", "window_end", "downloads_31_180", "mirror_downloads_31_180"]
    write_csv(out_path, list(rows_by_pkg.values()), fields)
    return list(rows_by_pkg.values())


def summarize(rows: list[dict], downloads: dict[str, dict], latest: dt.date):
    # Baseline is the median mirror total for mature 2022-2024 package windows.
    baseline_totals = []
    for r in rows:
        fd = dt.date.fromisoformat(r["first_publication_date"])
        d = downloads.get(r["package"])
        if d and 2022 <= fd.year <= 2024:
            baseline_totals.append(int(d["mirror_downloads_31_180"]))
    baseline_mirror = int(median(baseline_totals)) if baseline_totals else 1

    pkg_rows = []
    by_pkg = {r["package"]: r for r in rows}
    for pkg, d in downloads.items():
        if pkg not in by_pkg:
            continue
        r = by_pkg[pkg]
        mirror = int(d["mirror_downloads_31_180"])
        raw = int(d["downloads_31_180"])
        scaled = raw * baseline_mirror / mirror if mirror else 0.0
        pkg_rows.append({**r, **d, "downloads_scaled_to_2022_2024_mirror": round(scaled, 3)})

    pkg_fields = ["package", "first_publication_date", "cohort_quarter", "cohort_half", "archived", "first_version", "latest_version", "downloads_31_180", "mirror_downloads_31_180", "downloads_scaled_to_2022_2024_mirror", "window_start", "window_end", "title", "description", "url", "bugreports"]
    write_csv(DATA / "package_windows_enriched.csv", pkg_rows, pkg_fields)

    def cohort_table(period_key: str):
        groups = defaultdict(list)
        for r in rows:
            groups[r[period_key]].append(r)
        matured = defaultdict(list)
        pkg_row_by_name = {p["package"]: p for p in pkg_rows}
        for p in pkg_rows:
            matured[p[period_key]].append(p)
        table = []
        for c in sorted(groups):
            if c > "2026Q3" if period_key == "cohort_quarter" else c > "2026H2":
                pass
            created = len(groups[c])
            archived = sum(1 for r in groups[c] if r["archived"])
            m = matured.get(c, [])
            row = {
                "cohort": c,
                "created": created,
                "archived_as_of_2026_10_15": archived,
                "eligible_with_full_31_180_window": len(m),
                "baseline_mirror_downloads_150d": baseline_mirror,
            }
            for t in THRESHOLDS:
                raw_count = sum(1 for p in m if int(p["downloads_31_180"]) >= t)
                scaled_count = sum(1 for p in m if float(p["downloads_scaled_to_2022_2024_mirror"]) >= t)
                row[f"raw_ge_{t}"] = raw_count
                row[f"raw_share_ge_{t}"] = round(raw_count / len(m), 4) if m else ""
                row[f"scaled_ge_{t}"] = scaled_count
                row[f"scaled_share_ge_{t}"] = round(scaled_count / len(m), 4) if m else ""
            table.append(row)
        return table

    q = cohort_table("cohort_quarter")
    h = cohort_table("cohort_half")
    q_fields = list(q[0].keys()) if q else []
    h_fields = list(h[0].keys()) if h else []
    write_csv(DATA / "cohorts_quarter.csv", q, q_fields)
    write_csv(DATA / "cohorts_half.csv", h, h_fields)

    recent = [p for p in pkg_rows if dt.date.fromisoformat(p["first_publication_date"]) >= RECENT_START]
    recent.sort(key=lambda p: int(p["downloads_31_180"]), reverse=True)
    write_csv(DATA / "top_recent_packages.csv", recent[:50], pkg_fields)

    supply = []
    all_groups = defaultdict(list)
    for r in rows:
        all_groups[r["cohort_quarter"]].append(r)
    for c in sorted(all_groups):
        supply.append({
            "quarter": c,
            "created": len(all_groups[c]),
            "still_listed_current_or_archived_recoverable": len(all_groups[c]),
            "archived_as_of_2026_10_15": sum(1 for r in all_groups[c] if r["archived"]),
        })
    write_csv(DATA / "new_packages_per_quarter.csv", supply, list(supply[0].keys()))

    meta = {
        "latest_cranlogs_date": latest.isoformat(),
        "baseline_mirror_downloads_150d_median_2022_2024": baseline_mirror,
        "thresholds_downloads_31_180": THRESHOLDS,
        "eligible_latest_first_publication_date": (latest - dt.timedelta(days=180)).isoformat(),
        "created_packages_2021_to_2026q3": len(rows),
        "matured_packages_with_download_windows": len(pkg_rows),
    }
    (DATA / "analysis_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main():
    latest = latest_cranlogs_date()
    allall = load_crandb()
    rows = extract_packages(allall)
    fields = ["package", "first_publication_date", "cohort_quarter", "cohort_half", "archived", "first_version", "latest_version", "title", "description", "url", "bugreports"]
    write_csv(DATA / "packages_2021_2026q3.csv", rows, fields)

    daily_start = START_DATE + dt.timedelta(days=31)
    daily = fetch_daily_totals(daily_start, latest)
    mirror_prefix = prefix_sums(daily)
    eligible = [r for r in rows if dt.date.fromisoformat(r["first_publication_date"]) + dt.timedelta(days=180) <= latest]
    download_rows = fetch_package_totals(eligible, latest, mirror_prefix)
    meta = summarize(rows, {r["package"]: r for r in download_rows}, latest)
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
