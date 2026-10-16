#!/usr/bin/env python3
"""Best-effort equal-age AMO ADU probe using Wayback detail-page snapshots.

For the top 10 current-ADU 2024H1 add-ons, look for detail-page captures in
2025H2 (roughly 13-24 months after creation, centered on +18 months) and parse
average_daily_users from the embedded AMO JSON. This is not enough for full
cohort counts; it documents coverage and a small comparison sample.
"""
from __future__ import annotations

import csv, gzip, hashlib, json, re, time, urllib.parse, urllib.request
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache" / "wayback"
CACHE.mkdir(parents=True, exist_ok=True)
UA = "niche-usage-study/1.0 (Wayback equal-age AMO probe; cached)"
N = 10
SLEEP = 0.45
ADU_RE = re.compile(r'"average_daily_users"\s*:\s*(\d+)')


def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    dim = [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1]
    return date(y, m, min(d.day, dim))


def get(url: str, binary=False):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + (".bin" if binary else ".json"))
    if path.exists():
        raw = path.read_bytes()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        path.write_bytes(raw)
        time.sleep(SLEEP)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    if binary:
        return raw
    return json.loads(raw.decode("utf-8"))


def cdx(url: str):
    q = urllib.parse.urlencode({
        "url": url,
        "output": "json",
        "from": "202507",
        "to": "202512",
        "filter": "statuscode:200",
        "limit": "30",
    })
    try:
        data = get("https://web.archive.org/cdx/search/cdx?" + q)
    except Exception as e:
        return [], str(e)
    if not data or len(data) <= 1:
        return [], ""
    header = data[0]
    return [dict(zip(header, row)) for row in data[1:]], ""


def fetch_snapshot(ts, original):
    url = f"https://web.archive.org/web/{ts}id_/{original}"
    try:
        raw = get(url, binary=True)
    except Exception as e:
        return None, str(e)
    text = raw.decode("utf-8", "ignore")
    m = ADU_RE.search(text)
    return int(m.group(1)) if m else None, "no average_daily_users in snapshot" if not m else ""

rows = list(csv.DictReader((ROOT / "addons_firefox_extensions_current.csv").open(encoding="utf-8")))
for r in rows:
    r["adu"] = int(float(r.get("average_daily_users") or 0))
sel = sorted([r for r in rows if r["cohort"] == "2024H1"], key=lambda r: r["adu"], reverse=True)[:N]
out=[]
for i, r in enumerate(sel, 1):
    created = datetime.fromisoformat(r["created"].replace("Z", "+00:00")).date()
    target = add_months(created, 18)
    captures, err = cdx(r["url"])
    best = None
    if captures:
        def dist(c):
            ts = c["timestamp"][:8]
            d = date(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))
            return abs((d - target).days)
        best = min(captures, key=dist)
    snap_adu = None; snap_err = err
    if best:
        snap_adu, snap_err = fetch_snapshot(best["timestamp"], best["original"])
    out.append({
        "rank_current_2024H1": i,
        "slug": r["slug"],
        "name": r["name"],
        "created": r["created"],
        "target_created_plus_18mo": target.isoformat(),
        "current_adu_2026_10_15": r["adu"],
        "snapshot_timestamp": best["timestamp"] if best else "",
        "snapshot_adu": snap_adu if snap_adu is not None else "",
        "cdx_captures_2025H2": len(captures),
        "error": snap_err,
        "url": r["url"],
    })
    print(i, r["slug"], "caps", len(captures), "snap", snap_adu, snap_err, flush=True)

with (ROOT / "wayback_equal_age_probe_2024H1_top10.csv").open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)
covered=[r for r in out if r["snapshot_adu"] != ""]
summary={
    "attempted_top_current_adu_2024H1": N,
    "with_any_2025H2_detail_page_capture": sum(1 for r in out if int(r["cdx_captures_2025H2"])>0),
    "with_parsed_snapshot_adu": len(covered),
    "snapshot_counts_thresholds": {str(t): sum(1 for r in covered if int(r["snapshot_adu"]) >= t) for t in [10,100,1000,10000]},
    "note": "Coverage is a biased top-current-ADU sample, not a full cohort estimate.",
}
(ROOT / "wayback_equal_age_probe_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
