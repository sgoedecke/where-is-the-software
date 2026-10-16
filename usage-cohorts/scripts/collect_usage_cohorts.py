#!/usr/bin/env python3
"""Collect creation/usage cohorts for Homebrew, crates.io, and VS Code Marketplace.

All large inputs are streamed or kept in a caller-supplied scratch directory; no
raw registry dumps are written by this script.
"""
from __future__ import annotations

import argparse
import csv
import codecs
import datetime as dt
import gzip
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

UA = "usage-cohort-research/1.0 (+https://github.com/)"
START = dt.date(2021, 1, 1)
END_EXCLUSIVE = dt.date(2026, 7, 1)
QUARTERS = []
y, q = 2021, 1
while (y, q) <= (2026, 2):
    m = 3 * (q - 1) + 1
    s = dt.date(y, m, 1)
    if q == 4:
        e = dt.date(y + 1, 1, 1)
    else:
        e = dt.date(y, m + 3, 1)
    QUARTERS.append((f"{y}Q{q}", s, e))
    q += 1
    if q == 5:
        y += 1
        q = 1


def request_json(url: str, data=None, headers=None, timeout=120, retries=4):
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        hdrs.setdefault("Content-Type", "application/json")
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def request_bytes(url: str, timeout=120, retries=4) -> bytes:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def quarter_for_date(d: dt.date) -> str | None:
    if d < START or d >= END_EXCLUSIVE:
        return None
    return f"{d.year}Q{(d.month - 1)//3 + 1}"


def parse_date(s: str) -> dt.date:
    # Handles ISO timestamps and crates dump timestamps.
    s = s.strip().replace("Z", "+00:00")
    if " " in s and "T" not in s:
        s = s.replace(" ", "T", 1)
    return dt.datetime.fromisoformat(s).date()


def write_rows(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def count_thresholds(items, count_lookup, thresholds):
    rows = []
    byq = defaultdict(list)
    for name, q in items.items():
        if q:
            byq[q].append(name)
    for q, _, _ in QUARTERS:
        names = byq.get(q, [])
        row = {"cohort": q, "created": len(names)}
        for t in thresholds:
            row[f"ge_{t}"] = sum(1 for n in names if count_lookup.get(n, 0) >= t)
        rows.append(row)
    return rows


# ---------------- Homebrew ----------------

def git(cmd, cwd: Path, timeout=None) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True, timeout=timeout)


def ensure_homebrew_clone(url: str, dest: Path):
    if (dest / ".git").exists():
        git(["fetch", "--filter=blob:none", "--quiet", "origin", "HEAD"], dest, timeout=900)
        # Keep the default branch ref fresh where possible, without checking out files.
        try:
            git(["remote", "set-head", "origin", "-a"], dest, timeout=120)
        except subprocess.CalledProcessError:
            pass
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["git", "clone", "--filter=blob:none", "--no-checkout", url, str(dest)])


def homebrew_created(repo: Path, topdir: str) -> dict[str, str]:
    """Map token basename to first quarter in which the file was added.

    Uses rename detection so sharding moves such as Formula/a/foo.rb or
    Casks/f/foo.rb do not create thousands of false 2023/2024 additions.
    """
    # Blobless clone is important: path history over a treeless clone is very slow.
    out = git(["--no-pager", "log", "--reverse", "-M", "--diff-filter=AR", "--format=DATE %aI", "--name-status", "--", topdir], repo, timeout=1800)
    first: dict[str, dt.date] = {}
    curdate = None

    def token(path: str) -> str | None:
        if not path.endswith(".rb"):
            return None
        parts = path.split("/")
        if not parts or parts[0] != topdir:
            return None
        return Path(path).stem

    for line in out.splitlines():
        if line.startswith("DATE "):
            curdate = parse_date(line[5:])
            continue
        if not line or curdate is None:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status == "A" and len(parts) >= 2:
            name = token(parts[1])
            if name and (name not in first or curdate < first[name]):
                first[name] = curdate
        elif status.startswith("R") and len(parts) >= 3:
            old = token(parts[1])
            new = token(parts[2])
            if new:
                inherited = first.get(old) if old else None
                if inherited is None:
                    inherited = curdate
                if new not in first or inherited < first[new]:
                    first[new] = inherited
    return {name: quarter_for_date(d) for name, d in first.items() if quarter_for_date(d)}


def parse_brew_counts(obj: dict, key: str) -> dict[str, int]:
    counts = {}
    for it in obj.get("items", []):
        name = it.get(key)
        if not name:
            continue
        counts[name] = int(str(it.get("count", "0")).replace(",", ""))
    return counts


def target_equal_age_date(qstart: dt.date, qend: dt.date) -> dt.date:
    # Snapshot six months after the cohort closes: items are 6-9 months old.
    m = qend.month + 6
    y = qend.year + (m - 1) // 12
    m = ((m - 1) % 12) + 1
    return dt.date(y, m, min(qend.day, 28))


def cdx_nearest(original_url: str, target: dt.date, cache_dir: Path) -> str | None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    target_s = target.strftime("%Y%m%d")
    key = re.sub(r"[^A-Za-z0-9_.-]+", "_", original_url) + "_" + target_s + ".json"
    cfile = cache_dir / key
    if cfile.exists():
        rows = json.loads(cfile.read_text())
    else:
        frm = (target - dt.timedelta(days=60)).strftime("%Y%m%d")
        to = (target + dt.timedelta(days=60)).strftime("%Y%m%d")
        params = urllib.parse.urlencode({
            "url": original_url,
            "output": "json",
            "filter": "statuscode:200",
            "from": frm,
            "to": to,
            "fl": "timestamp,original,statuscode,length",
            "collapse": "digest",
        })
        rows = request_json("https://web.archive.org/cdx/search/cdx?" + params, timeout=90)
        cfile.write_text(json.dumps(rows))
        time.sleep(0.5)
    if not rows or len(rows) < 2:
        return None
    best_ts, best_delta = None, 10**9
    target_dt = dt.datetime.combine(target, dt.time())
    for r in rows[1:]:
        ts = r[0]
        snap_dt = dt.datetime.strptime(ts[:8], "%Y%m%d")
        delta = abs((snap_dt - target_dt).days)
        if delta < best_delta:
            best_delta, best_ts = delta, ts
    return best_ts


def _gunzip_repeated(data: bytes) -> bytes:
    while data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    return data


def wayback_json(original_url: str, ts: str, cache_dir: Path):
    cache_dir.mkdir(parents=True, exist_ok=True)
    fname = re.sub(r"[^A-Za-z0-9_.-]+", "_", original_url) + "_" + ts + ".json.gz"
    f = cache_dir / fname
    if f.exists():
        data = _gunzip_repeated(f.read_bytes())
        return json.loads(data.decode())
    url = f"https://web.archive.org/web/{ts}id_/{original_url}"
    data = _gunzip_repeated(request_bytes(url, timeout=180))
    f.write_bytes(gzip.compress(data))
    time.sleep(0.75)
    return json.loads(data.decode())


def collect_homebrew(out: Path, scratch: Path):
    hb = scratch / "homebrew"
    core = hb / "homebrew-core"
    cask = hb / "homebrew-cask"
    ensure_homebrew_clone("https://github.com/Homebrew/homebrew-core.git", core)
    ensure_homebrew_clone("https://github.com/Homebrew/homebrew-cask.git", cask)
    created_formula = homebrew_created(core, "Formula")
    created_cask = homebrew_created(cask, "Casks")

    endpoints = [
        ("formula", "https://formulae.brew.sh/api/analytics/install/30d.json", "formula", created_formula),
        ("cask", "https://formulae.brew.sh/api/analytics/cask-install/30d.json", "cask", created_cask),
    ]
    thresholds = [100, 1000, 10000]
    meta_rows = []
    for kind, url, key, created in endpoints:
        live = request_json(url, timeout=180)
        live_counts = parse_brew_counts(live, key)
        rows = count_thresholds(created, live_counts, thresholds)
        for row in rows:
            row["analytics_end_date"] = live.get("end_date")
        write_rows(out / "data" / f"homebrew_{kind}_current_30d.csv", ["cohort", "created", "ge_100", "ge_1000", "ge_10000", "analytics_end_date"], rows)
        meta_rows.append({"kind": kind, "current_items_with_creation_quarter": len(created), "live_analytics_items": len(live_counts), "live_start_date": live.get("start_date"), "live_end_date": live.get("end_date")})

        equal_rows = []
        for q, qs, qe in QUARTERS:
            target = target_equal_age_date(qs, qe)
            ts = cdx_nearest(url, target, scratch / "wayback-cdx")
            counts = None
            start_date = end_date = None
            if ts:
                obj = wayback_json(url, ts, scratch / "wayback-json")
                counts = parse_brew_counts(obj, key)
                start_date, end_date = obj.get("start_date"), obj.get("end_date")
            names = [name for name, cq in created.items() if cq == q]
            row = {
                "cohort": q,
                "created": len(names),
                "target_snapshot_date": target.isoformat(),
                "snapshot_timestamp": ts or "",
                "analytics_start_date": start_date or "",
                "analytics_end_date": end_date or "",
                "days_from_target": "" if not ts else (dt.datetime.strptime(ts[:8], "%Y%m%d").date() - target).days,
            }
            for t in thresholds:
                row[f"ge_{t}"] = "" if counts is None else sum(1 for n in names if counts.get(n, 0) >= t)
            equal_rows.append(row)
        write_rows(out / "data" / f"homebrew_{kind}_equal_age_30d.csv", ["cohort", "created", "ge_100", "ge_1000", "ge_10000", "target_snapshot_date", "snapshot_timestamp", "analytics_start_date", "analytics_end_date", "days_from_target"], equal_rows)
    write_rows(out / "data" / "homebrew_meta.csv", ["kind", "current_items_with_creation_quarter", "live_analytics_items", "live_start_date", "live_end_date"], meta_rows)


# ---------------- crates.io ----------------

def collect_crates(out: Path, scratch: Path):
    csv.field_size_limit(2**31 - 1)
    url = "https://static.crates.io/db-dump.tar.gz"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    crate_downloads: dict[int, int] = {}
    crates: dict[int, dict] = {}
    version_to_crate: dict[int, int] = {}
    non_yanked_versions = defaultdict(int)
    recent_downloads = defaultdict(int)
    max_vd_date = None
    min_vd_date = None
    with urllib.request.urlopen(req, timeout=3600) as resp:
        tf = tarfile.open(fileobj=resp, mode="r|gz")
        for member in tf:
            if not member.isfile():
                continue
            rel = "/".join(member.name.split("/")[-2:])
            if rel not in {"data/crate_downloads.csv", "data/crates.csv", "data/versions.csv", "data/version_downloads.csv"}:
                continue
            f = tf.extractfile(member)
            assert f is not None
            text = codecs.getreader("utf-8")(f)
            r = csv.DictReader(text)
            if rel == "data/crate_downloads.csv":
                for row in r:
                    crate_downloads[int(row["crate_id"])] = int(row["downloads"])
            elif rel == "data/crates.csv":
                for row in r:
                    try:
                        created = parse_date(row["created_at"])
                    except Exception:
                        continue
                    q = quarter_for_date(created)
                    if q:
                        cid = int(row["id"])
                        crates[cid] = {"name": row["name"], "created": created, "quarter": q}
            elif rel == "data/versions.csv":
                for row in r:
                    cid = int(row["crate_id"])
                    vid = int(row["id"])
                    version_to_crate[vid] = cid
                    if row.get("yanked") == "f":
                        non_yanked_versions[cid] += 1
            elif rel == "data/version_downloads.csv":
                for row in r:
                    d = dt.date.fromisoformat(row["date"])
                    if max_vd_date is None or d > max_vd_date:
                        max_vd_date = d
                    if min_vd_date is None or d < min_vd_date:
                        min_vd_date = d
                    # The dump currently retains recent daily rows only; keep <=90d if older rows appear.
                    vid = int(row["version_id"])
                    cid = version_to_crate.get(vid)
                    if cid is not None:
                        recent_downloads[cid] += int(row["downloads"])

    thresholds_total = [1000, 10000, 100000]
    thresholds_recent = [100, 1000, 10000]
    rows = []
    kept_ids = [cid for cid in crates if non_yanked_versions.get(cid, 0) > 0]
    byq = defaultdict(list)
    for cid in kept_ids:
        byq[crates[cid]["quarter"]].append(cid)
    for q, _, _ in QUARTERS:
        ids = byq.get(q, [])
        row = {"cohort": q, "created_non_yanked": len(ids)}
        for t in thresholds_total:
            row[f"total_ge_{t}"] = sum(1 for cid in ids if crate_downloads.get(cid, 0) >= t)
        for t in thresholds_recent:
            row[f"recent_ge_{t}"] = sum(1 for cid in ids if recent_downloads.get(cid, 0) >= t)
        rows.append(row)
    write_rows(out / "data" / "crates_cohorts.csv", ["cohort", "created_non_yanked", "total_ge_1000", "total_ge_10000", "total_ge_100000", "recent_ge_100", "recent_ge_1000", "recent_ge_10000"], rows)
    meta = [{
        "dump_url": url,
        "crates_in_window": len(crates),
        "crates_non_yanked_in_window": len(kept_ids),
        "version_downloads_min_date": min_vd_date.isoformat() if min_vd_date else "",
        "version_downloads_max_date": max_vd_date.isoformat() if max_vd_date else "",
    }]
    write_rows(out / "data" / "crates_meta.csv", list(meta[0].keys()), meta)


# ---------------- VS Code Marketplace ----------------

def marketplace_page(page: int, page_size: int):
    body = {
        "filters": [{
            "criteria": [{"filterType": 8, "value": "Microsoft.VisualStudio.Code"}],
            "pageNumber": page,
            "pageSize": page_size,
            "sortBy": 10,          # publishedDate
            "sortOrder": 2,       # descending
        }],
        "flags": 256,             # include statistics, enough for install/rating counts
    }
    return request_json(
        "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery?api-version=7.2-preview.1",
        data=body,
        headers={"Accept": "application/json;api-version=7.2-preview.1"},
        timeout=120,
    )


def stat(e: dict, name: str) -> float:
    for s in e.get("statistics", []) or []:
        if s.get("statisticName") == name:
            return float(s.get("value", 0) or 0)
    return 0.0


def collect_vscode(out: Path, scratch: Path):
    page_size = 1000
    page = 1
    rows_by_q = defaultdict(list)
    total_count = None
    scanned = 0
    seen_ids = set()
    oldest_seen = None
    while True:
        d = marketplace_page(page, page_size)
        result = d["results"][0]
        exts = result.get("extensions", [])
        if page == 1:
            for m in result.get("resultMetadata", []) or []:
                if m.get("metadataType") == "ResultCount":
                    total_count = m.get("metadataItems", [{}])[0].get("count")
        if not exts:
            break
        stop = False
        for e in exts:
            eid = e.get("extensionId") or f"{e.get('publisher',{}).get('publisherName','')}.{e.get('extensionName','')}"
            if eid in seen_ids:
                continue
            seen_ids.add(eid)
            pub = parse_date(e.get("publishedDate") or e.get("releaseDate") or e.get("lastUpdated"))
            oldest_seen = pub
            if pub < START:
                stop = True
                continue
            q = quarter_for_date(pub)
            if not q:
                continue
            rows_by_q[q].append({
                "id": e.get("extensionId"),
                "name": f"{e.get('publisher',{}).get('publisherName','')}.{e.get('extensionName','')}",
                "installs": int(stat(e, "install")),
                "rating_count": int(stat(e, "ratingcount")),
                "rating": stat(e, "averagerating"),
            })
        scanned += len(exts)
        if stop:
            break
        page += 1
        time.sleep(0.2)
    thresholds = [1000, 10000, 100000]
    out_rows = []
    for q, _, _ in QUARTERS:
        xs = rows_by_q.get(q, [])
        row = {"cohort": q, "published": len(xs)}
        for t in thresholds:
            row[f"installs_ge_{t}"] = sum(1 for x in xs if x["installs"] >= t)
        row["rating_count_ge_10"] = sum(1 for x in xs if x["rating_count"] >= 10)
        out_rows.append(row)
    write_rows(out / "data" / "vscode_cohorts.csv", ["cohort", "published", "installs_ge_1000", "installs_ge_10000", "installs_ge_100000", "rating_count_ge_10"], out_rows)
    meta = [{"marketplace_total_count": total_count or "", "extensions_scanned_until_2021": scanned, "unique_extensions_scanned_until_2021": len(seen_ids), "oldest_seen": oldest_seen.isoformat() if oldest_seen else ""}]
    write_rows(out / "data" / "vscode_meta.csv", list(meta[0].keys()), meta)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path.home() / "Code/where-is-the-software/usage-cohorts"))
    p.add_argument("--scratch", default=str(Path.home() / ".cache/usage-cohorts"))
    p.add_argument("--only", choices=["all", "homebrew", "crates", "vscode"], default="all")
    args = p.parse_args()
    out = Path(args.out).expanduser()
    scratch = Path(args.scratch).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    if args.only in {"all", "homebrew"}:
        collect_homebrew(out, scratch)
    if args.only in {"all", "crates"}:
        collect_crates(out, scratch)
    if args.only in {"all", "vscode"}:
        collect_vscode(out, scratch)

if __name__ == "__main__":
    main()
