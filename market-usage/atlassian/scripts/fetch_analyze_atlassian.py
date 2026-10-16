#!/usr/bin/env python3
"""Fetch Atlassian Marketplace listings and build usage cohort tables.

All outputs stay under this analysis directory.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path

BASE = "https://marketplace.atlassian.com"
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "cache"
DATA = ROOT / "data"
TODAY = date(2026, 10, 15)
HOSTINGS = ["cloud", "dataCenter", "server"]
PAGE_LIMIT = 50
MAX_WORKERS = int(os.environ.get("ATLASSIAN_WORKERS", "16"))

AI_RE = re.compile(r"\b(ai|artificial intelligence|agent|agents|rovo|chatgpt|gpt|llm|large language model|copilot|openai|anthropic|claude|gemini|summari[sz]e|prompt)\b", re.I)
PAID_MODELS = {"atlassian", "vendor"}


def ensure_dirs() -> None:
    for p in [CACHE / "listings", CACHE / "versions", DATA]:
        p.mkdir(parents=True, exist_ok=True)


def cache_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.=-]+", "_", text)[:220]


def get_json(path: str, cache_path: Path, tries: int = 4) -> dict:
    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    url = BASE + path
    last_err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cohort-analysis/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = r.read()
            obj = json.loads(data.decode("utf-8"))
            tmp = cache_path.with_suffix(cache_path.suffix + ".partial")
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False)
            tmp.replace(cache_path)
            return obj
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed {url}: {last_err}")


def href_id(href: str) -> str:
    return href.rstrip("/").split("/")[-1]


def parse_addon(a: dict, hosting: str) -> dict:
    emb = a.get("_embedded", {})
    dist = emb.get("distribution", {}) or {}
    reviews = emb.get("reviews", {}) or {}
    vendor = emb.get("vendor", {}) or {}
    vhref = vendor.get("_links", {}).get("self", {}).get("href", "")
    cats = [c.get("name", "") for c in emb.get("categories", [])]
    return {
        "hosting_query": hosting,
        "key": a.get("key", ""),
        "id": a.get("id", ""),
        "name": a.get("name", ""),
        "tagline": a.get("tagLine", ""),
        "summary": a.get("summary", ""),
        "status": a.get("status", ""),
        "vendor_id": href_id(vhref) if vhref else "",
        "vendor_name": vendor.get("name", ""),
        "categories": "; ".join(cats),
        "reviews_count": reviews.get("count", 0) or 0,
        "reviews_average": reviews.get("averageStars", ""),
        "total_installs": dist.get("totalInstalls", 0) or 0,
        "downloads": dist.get("downloads", 0) or 0,
        "total_users": dist.get("totalUsers", ""),
        "alternate_href": a.get("_links", {}).get("alternate", {}).get("href", ""),
    }


def fetch_listing_pages(hosting: str) -> list[dict]:
    first_path = f"/rest/2/addons?limit={PAGE_LIMIT}&offset=0&hosting={urllib.parse.quote(hosting)}"
    first = get_json(first_path, CACHE / "listings" / f"addons_{hosting}_000000.json")
    count = int(first.get("count", 0))
    offsets = list(range(0, count, PAGE_LIMIT))
    pages = {0: first}
    print(f"{hosting}: {count} listings across {len(offsets)} pages", flush=True)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {}
        for off in offsets[1:]:
            path = f"/rest/2/addons?limit={PAGE_LIMIT}&offset={off}&hosting={urllib.parse.quote(hosting)}"
            cp = CACHE / "listings" / f"addons_{hosting}_{off:06d}.json"
            futs[ex.submit(get_json, path, cp)] = off
        for i, fut in enumerate(as_completed(futs), 1):
            off = futs[fut]
            pages[off] = fut.result()
            if i % 50 == 0:
                print(f"  {hosting}: fetched {i}/{len(futs)} remaining pages", flush=True)
    rows = []
    for off in offsets:
        for a in pages[off].get("_embedded", {}).get("addons", []):
            rows.append(parse_addon(a, hosting))
    return rows


def release_date(v: dict) -> str:
    return (v.get("release") or {}).get("date", "") or ""


def version_summary(key: str, hosting: str) -> dict:
    qkey = urllib.parse.quote(key, safe="")
    qh = urllib.parse.quote(hosting)
    latest_path = f"/rest/2/addons/{qkey}/versions?limit=1&offset=0&hosting={qh}"
    safe = cache_name(key)
    latest = get_json(latest_path, CACHE / "versions" / f"{safe}__{hosting}__latest.json")
    count = int(latest.get("count", 0) or 0)
    if count <= 0:
        return {"key": key, "hosting": hosting, "version_count": 0}
    latest_v = latest.get("_embedded", {}).get("versions", [{}])[0]
    if count == 1:
        oldest_v = latest_v
    else:
        oldest_path = f"/rest/2/addons/{qkey}/versions?limit=1&offset={count-1}&hosting={qh}"
        oldest = get_json(oldest_path, CACHE / "versions" / f"{safe}__{hosting}__oldest_{count-1}.json")
        oldest_v = oldest.get("_embedded", {}).get("versions", [{}])[0]
    dep = latest_v.get("deployment") or {}
    apps = []
    for c in latest_v.get("compatibilities") or []:
        app = c.get("application")
        if app:
            apps.append(app)
    return {
        "key": key,
        "hosting": hosting,
        "version_count": count,
        "first_release_date": release_date(oldest_v),
        "latest_release_date": release_date(latest_v),
        "latest_version": latest_v.get("name", ""),
        "payment_model": latest_v.get("paymentModel", ""),
        "latest_connect": dep.get("connect", ""),
        "latest_cloud": dep.get("cloud", ""),
        "latest_server": dep.get("server", ""),
        "latest_data_center": dep.get("dataCenter", ""),
        "applications": "; ".join(sorted(set(apps))),
    }


def valid_date(s: str) -> date | None:
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def half_year(d: str) -> str:
    dt = valid_date(d)
    if not dt:
        return "unknown"
    return f"{dt.year}H{1 if dt.month <= 6 else 2}"


def years_old(d: str) -> float:
    dt = valid_date(d)
    if not dt:
        return math.nan
    return (TODAY - dt).days / 365.25


def is_paid(model: str) -> bool:
    return (model or "").lower() in PAID_MODELS


def payment_bucket(model: str, paid_any: bool | None = None) -> str:
    if paid_any is not None:
        return "paid" if paid_any else "free"
    return "paid" if is_paid(model) else "free"


def cohort_sort_key(c: str) -> tuple[int, int]:
    m = re.match(r"(\d{4})H([12])", c)
    if not m:
        return (9999, 9)
    return (int(m.group(1)), int(m.group(2)))


def pct(n: int, d: int) -> str:
    return "" if not d else f"{100*n/d:.1f}%"


def main() -> int:
    ensure_dirs()

    all_listing_rows = []
    for h in HOSTINGS:
        all_listing_rows.extend(fetch_listing_pages(h))
    listing_csv = DATA / "listing_rows_by_hosting.csv"
    with listing_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_listing_rows[0].keys()))
        w.writeheader(); w.writerows(all_listing_rows)
    print(f"wrote {listing_csv}", flush=True)

    by_host_key = {(r["hosting_query"], r["key"]): r for r in all_listing_rows if r["key"]}
    version_jobs = sorted(by_host_key.keys())
    print(f"fetching version summaries for {len(version_jobs)} host/key pairs", flush=True)
    version_rows = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(version_summary, key, h): (h, key) for h, key in version_jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                version_rows.append(fut.result())
            except Exception as e:
                h, key = futs[fut]
                print(f"ERROR {h} {key}: {e}", file=sys.stderr, flush=True)
                version_rows.append({"key": key, "hosting": h, "version_count": 0, "error": str(e)})
            if i % 500 == 0:
                print(f"  version summaries {i}/{len(futs)}", flush=True)
    vfields = sorted({k for r in version_rows for k in r.keys()})
    with (DATA / "version_summaries_by_hosting.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vfields)
        w.writeheader(); w.writerows(version_rows)

    version_by = {(r.get("hosting"), r.get("key")): r for r in version_rows}

    # One row per analysis segment (cloud, dc_server). Distribution is listing-wide current telemetry.
    app_rows = []
    for key in sorted({r["key"] for r in all_listing_rows if r["key"]}):
        cloud_listing = by_host_key.get(("cloud", key))
        if cloud_listing:
            v = version_by.get(("cloud", key), {})
            row = {**cloud_listing}
            row.update({
                "segment": "cloud",
                "hostings": "cloud",
                "first_release_date": v.get("first_release_date", ""),
                "latest_release_date": v.get("latest_release_date", ""),
                "payment_model": v.get("payment_model", ""),
                "payment_bucket": payment_bucket(v.get("payment_model", "")),
                "version_count": v.get("version_count", 0),
                "applications": v.get("applications", ""),
                "latest_connect": v.get("latest_connect", ""),
                "cohort": half_year(v.get("first_release_date", "")),
                "age_years_current": years_old(v.get("first_release_date", "")),
            })
            text = " ".join([row.get("name", ""), row.get("tagline", ""), row.get("summary", ""), row.get("categories", "")])
            row["ai_flag"] = bool(AI_RE.search(text))
            app_rows.append(row)

        dc_listings = [by_host_key.get((h, key)) for h in ["dataCenter", "server"] if by_host_key.get((h, key))]
        if dc_listings:
            # Prefer the dataCenter listing if present; distribution fields are the same listing-level counters.
            base = by_host_key.get(("dataCenter", key)) or by_host_key.get(("server", key))
            vs = [version_by.get((h, key), {}) for h in ["dataCenter", "server"] if version_by.get((h, key), {}).get("version_count", 0)]
            dates = [v.get("first_release_date", "") for v in vs if valid_date(v.get("first_release_date", ""))]
            first = min(dates) if dates else ""
            latest_dates = [v.get("latest_release_date", "") for v in vs if valid_date(v.get("latest_release_date", ""))]
            latest = max(latest_dates) if latest_dates else ""
            paid_any = any(is_paid(v.get("payment_model", "")) for v in vs)
            apps = "; ".join(sorted(set(a for v in vs for a in (v.get("applications", "") or "").split("; ") if a)))
            row = {**base}
            row.update({
                "segment": "dc_server",
                "hostings": ";".join(h for h in ["dataCenter", "server"] if by_host_key.get((h, key))),
                "first_release_date": first,
                "latest_release_date": latest,
                "payment_model": ";".join(sorted(set(v.get("payment_model", "") for v in vs if v.get("payment_model", "")))),
                "payment_bucket": payment_bucket("", paid_any=paid_any),
                "version_count": sum(int(v.get("version_count", 0) or 0) for v in vs),
                "applications": apps,
                "latest_connect": "",
                "cohort": half_year(first),
                "age_years_current": years_old(first),
            })
            text = " ".join([row.get("name", ""), row.get("tagline", ""), row.get("summary", ""), row.get("categories", "")])
            row["ai_flag"] = bool(AI_RE.search(text))
            app_rows.append(row)

    # Vendor age proxy across observed current listings/hostings.
    vendor_first = {}
    vendor_apps = defaultdict(set)
    vendor_pre_2025_apps = defaultdict(set)
    for r in app_rows:
        vid = r.get("vendor_id") or r.get("vendor_name")
        if not vid:
            continue
        vendor_apps[vid].add(r["key"])
        d = r.get("first_release_date", "")
        if valid_date(d):
            if vid not in vendor_first or d < vendor_first[vid]:
                vendor_first[vid] = d
            if d < "2025-01-01":
                vendor_pre_2025_apps[vid].add(r["key"])
    for r in app_rows:
        vid = r.get("vendor_id") or r.get("vendor_name")
        r["vendor_first_seen_date"] = vendor_first.get(vid, "")
        r["vendor_current_app_count"] = len(vendor_apps.get(vid, set()))
        r["vendor_pre_2025_current_app_count"] = len(vendor_pre_2025_apps.get(vid, set()))
        r["vendor_established_proxy"] = bool(r["vendor_pre_2025_current_app_count"] or (r["vendor_current_app_count"] >= 3 and (r["vendor_first_seen_date"] or "9999") < "2025-07-01"))

    afields = [
        "segment", "hostings", "cohort", "first_release_date", "latest_release_date", "age_years_current",
        "payment_bucket", "payment_model", "total_installs", "downloads", "reviews_count", "reviews_average",
        "key", "id", "name", "vendor_id", "vendor_name", "vendor_first_seen_date", "vendor_current_app_count", "vendor_pre_2025_current_app_count", "vendor_established_proxy",
        "applications", "categories", "ai_flag", "latest_connect", "version_count", "tagline", "summary", "alternate_href", "status", "total_users"
    ]
    with (DATA / "apps_enriched.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=afields, extrasaction="ignore")
        w.writeheader(); w.writerows(app_rows)

    cohorts = []
    grouped = defaultdict(list)
    for r in app_rows:
        c = r.get("cohort", "unknown")
        if not re.match(r"20\d\dH[12]", c):
            continue
        if cohort_sort_key(c) < (2021, 1):
            continue
        grouped[(r["segment"], r["payment_bucket"], c)].append(r)
    for (segment, pay, c), rows in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1], cohort_sort_key(x[0][2]))):
        n = len(rows)
        i10 = sum(int(r.get("total_installs") or 0) >= 10 for r in rows)
        i100 = sum(int(r.get("total_installs") or 0) >= 100 for r in rows)
        i1000 = sum(int(r.get("total_installs") or 0) >= 1000 for r in rows)
        d100 = sum(int(r.get("downloads") or 0) >= 100 for r in rows)
        ai = sum(bool(r.get("ai_flag")) for r in rows)
        established = sum(bool(r.get("vendor_established_proxy")) for r in rows)
        forge_like = sum(str(r.get("latest_connect", "")).lower() == "false" for r in rows if segment == "cloud")
        connect_like = sum(str(r.get("latest_connect", "")).lower() == "true" for r in rows if segment == "cloud")
        cohorts.append({
            "segment": segment, "payment": pay, "cohort": c, "apps_listed_current_survivors": n,
            "installs_ge_10": i10, "installs_ge_100_modest": i100, "installs_ge_1000_high": i1000,
            "downloads_ge_100": d100,
            "share_ge_100": pct(i100, n), "share_ge_1000": pct(i1000, n),
            "ai_flag_count": ai, "established_vendor_proxy_count": established,
            "cloud_latest_connect_true": connect_like, "cloud_latest_connect_false_forge_like": forge_like,
        })
    cfields = list(cohorts[0].keys()) if cohorts else []
    with (DATA / "cohorts_by_segment_payment.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cfields)
        w.writeheader(); w.writerows(cohorts)

    # Totals by segment (free+paid) for the report.
    totals = []
    grouped2 = defaultdict(list)
    for r in app_rows:
        c = r.get("cohort", "unknown")
        if re.match(r"20\d\dH[12]", c) and cohort_sort_key(c) >= (2021, 1):
            grouped2[(r["segment"], c)].append(r)
    for (segment, c), rows in sorted(grouped2.items(), key=lambda x: (x[0][0], cohort_sort_key(x[0][1]))):
        n = len(rows)
        totals.append({
            "segment": segment, "cohort": c, "apps": n,
            "paid_apps": sum(r["payment_bucket"] == "paid" for r in rows),
            "free_apps": sum(r["payment_bucket"] == "free" for r in rows),
            "installs_ge_10": sum(int(r.get("total_installs") or 0) >= 10 for r in rows),
            "installs_ge_100_modest": sum(int(r.get("total_installs") or 0) >= 100 for r in rows),
            "installs_ge_1000_high": sum(int(r.get("total_installs") or 0) >= 1000 for r in rows),
            "downloads_ge_100": sum(int(r.get("downloads") or 0) >= 100 for r in rows),
            "ai_flag_count": sum(bool(r.get("ai_flag")) for r in rows),
        })
    with (DATA / "cohorts_by_segment_totals.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(totals[0].keys()))
        w.writeheader(); w.writerows(totals)

    recent = [r for r in app_rows if (r.get("first_release_date") or "") >= "2025-07-01"]
    recent.sort(key=lambda r: (int(r.get("total_installs") or 0), int(r.get("downloads") or 0)), reverse=True)
    top = recent[:50]
    tfields = ["segment", "first_release_date", "cohort", "total_installs", "downloads", "reviews_count", "payment_bucket", "ai_flag", "name", "vendor_name", "vendor_established_proxy", "vendor_first_seen_date", "vendor_current_app_count", "applications", "categories", "key", "alternate_href", "tagline"]
    with (DATA / "top_recent_since_2025H2.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tfields, extrasaction="ignore")
        w.writeheader(); w.writerows(top)

    # Lightweight metadata summary for report drafting.
    meta = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "today_assumed": TODAY.isoformat(),
        "listing_rows": len(all_listing_rows),
        "unique_addons_observed": len({r["key"] for r in all_listing_rows}),
        "segment_rows": Counter(r["segment"] for r in app_rows),
        "current_listing_counts_by_hosting_filter": Counter(r["hosting_query"] for r in all_listing_rows),
        "cohort_rows": len(cohorts),
        "recent_since_2025_07_01": len(recent),
        "recent_top50_ai_flags": sum(bool(r.get("ai_flag")) for r in top),
        "recent_top50_established_vendors": sum(bool(r.get("vendor_established_proxy")) for r in top),
    }
    with (DATA / "analysis_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)
    print(json.dumps(meta, indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
