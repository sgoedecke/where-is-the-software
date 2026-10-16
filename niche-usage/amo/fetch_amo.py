#!/usr/bin/env python3
"""Fetch AMO Firefox extension cohorts via the public v5 search API.

Caches raw page JSON under ./cache/amo_search/ and writes a flattened CSV.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache" / "amo_search"
CACHE.mkdir(parents=True, exist_ok=True)
USER_AGENT = "niche-usage-study/1.0 (research; polite cached AMO API client)"
BASE = "https://addons.mozilla.org/api/v5/addons/search/"
PAGE_SIZE = 50
SLEEP_SECONDS = float(os.environ.get("AMO_SLEEP", "0.08"))
TODAY = date(2026, 10, 15)

COHORTS = []
for year in range(2021, 2027):
    halves = [
        (f"{year}H1", date(year, 1, 1), date(year, 6, 30)),
        (f"{year}H2", date(year, 7, 1), date(year, 12, 31)),
    ]
    for label, start, end in halves:
        if start > TODAY:
            continue
        if end > TODAY:
            end = TODAY
        COHORTS.append((label, start, end))


def cache_path(url: str) -> Path:
    return CACHE / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")


def fetch_json(url: str) -> dict:
    path = cache_path(url)
    if path.exists():
        return json.loads(path.read_text())
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    data = json.loads(raw.decode("utf-8"))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    time.sleep(SLEEP_SECONDS)
    return data


def localized(d, preferred="en-US") -> str:
    if not isinstance(d, dict):
        return "" if d is None else str(d)
    if preferred in d and d[preferred]:
        return str(d[preferred])
    for v in d.values():
        if isinstance(v, str) and v:
            return v
    return ""


def page_url(start: date, end: date, page: int) -> str:
    params = {
        "type": "extension",
        "sort": "created",
        "page_size": str(PAGE_SIZE),
        "app": "firefox",
        "created__gte": start.isoformat(),
        "created__lte": end.isoformat(),
        "page": str(page),
    }
    return BASE + "?" + urllib.parse.urlencode(params)


def flatten(addon: dict, cohort: str, cohort_start: date, cohort_end: date) -> dict:
    ratings = addon.get("ratings") or {}
    authors = addon.get("authors") or []
    current_version = addon.get("current_version") or {}
    file_info = current_version.get("file") or {}
    return {
        "cohort": cohort,
        "cohort_start": cohort_start.isoformat(),
        "cohort_end": cohort_end.isoformat(),
        "id": addon.get("id"),
        "slug": addon.get("slug"),
        "guid": addon.get("guid"),
        "name": localized(addon.get("name")),
        "created": addon.get("created"),
        "last_updated": addon.get("last_updated"),
        "average_daily_users": addon.get("average_daily_users") or 0,
        "weekly_downloads": addon.get("weekly_downloads") or 0,
        "ratings_count": ratings.get("count") or 0,
        "ratings_average": ratings.get("average") or 0,
        "summary": localized(addon.get("summary")),
        "description": localized(addon.get("description")),
        "tags": ";".join(addon.get("tags") or []),
        "categories": ";".join(addon.get("categories") or []),
        "status": addon.get("status"),
        "is_disabled": addon.get("is_disabled"),
        "is_experimental": addon.get("is_experimental"),
        "requires_payment": addon.get("requires_payment"),
        "url": addon.get("url"),
        "homepage_url": localized((addon.get("homepage") or {}).get("url")),
        "support_url": localized((addon.get("support_url") or {}).get("url")),
        "authors": ";".join(a.get("name", "") for a in authors),
        "version_created": file_info.get("created"),
        "version_download_url": file_info.get("url"),
    }


def main() -> int:
    out_csv = ROOT / "addons_firefox_extensions_current.csv"
    manifest = []
    fieldnames = None
    rows_written = 0
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = None
        seen_ids = set()
        for cohort, start, end in COHORTS:
            first = fetch_json(page_url(start, end, 1))
            count = int(first.get("count") or 0)
            page_count = int(first.get("page_count") or 0)
            manifest.append({"cohort": cohort, "start": start.isoformat(), "end": end.isoformat(), "count": count, "page_count": page_count})
            print(f"{cohort}: {count} listed, {page_count} pages", flush=True)
            if page_count > 600:
                raise RuntimeError(f"{cohort} exceeds API page cap: {page_count} pages")
            for page in range(1, page_count + 1):
                data = first if page == 1 else fetch_json(page_url(start, end, page))
                for addon in data.get("results", []):
                    row = flatten(addon, cohort, start, end)
                    # The date filters are inclusive by day; retain only the intended interval.
                    created = datetime.fromisoformat(row["created"].replace("Z", "+00:00")).date()
                    if not (start <= created <= end):
                        continue
                    key = row["id"]
                    if key in seen_ids:
                        continue
                    seen_ids.add(key)
                    if writer is None:
                        fieldnames = list(row.keys())
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                    writer.writerow(row)
                    rows_written += 1
    (ROOT / "fetch_manifest.json").write_text(json.dumps({
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "AMO public API v5 search, Firefox extensions",
        "base_url": BASE,
        "user_agent": USER_AGENT,
        "cohorts": manifest,
        "rows_written": rows_written,
        "note": "Search API lists currently public/listed add-ons; removed, disabled, and unlisted creations may be missing.",
    }, ensure_ascii=False, indent=2))
    print(f"wrote {rows_written} rows to {out_csv}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
