#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IN = ROOT / "addons_firefox_extensions_current.csv"
THRESHOLDS = [10, 100, 1000, 10000]
RECENT = {"2025H2", "2026H1", "2026H2"}
AI_WORDS = re.compile(r"\b(ai|artificial intelligence|chatgpt|gpt|llm|claude|copilot|gemini|openai|ollama|prompt|summari[sz]e|translator|translate)\b", re.I)
AI_BUILT_WORDS = re.compile(r"\b(built|made|created|generated|coded|vibecoded|vibe-coded|developed)\b.{0,80}\b(ai|chatgpt|gpt|claude|copilot|llm)\b|\b(ai|chatgpt|gpt|claude|copilot|llm)\b.{0,80}\b(built|made|created|generated|coded|vibecoded|vibe-coded|developed)\b", re.I | re.S)
ESTABLISHED_WORDS = re.compile(r"\b(official|companion|browser extension|extension for|integrates with|from|by)\b", re.I)


def num(x):
    try:
        return int(float(x or 0))
    except Exception:
        return 0

rows = list(csv.DictReader(IN.open(encoding="utf-8")))
for r in rows:
    r["adu"] = num(r["average_daily_users"])
    r["weekly"] = num(r["weekly_downloads"])
    r["ratings_n"] = num(r["ratings_count"])

by = defaultdict(list)
for r in rows:
    by[r["cohort"]].append(r)

cohort_rows = []
for cohort in sorted(by):
    items = by[cohort]
    n = len(items)
    out = {
        "cohort": cohort,
        "start": items[0]["cohort_start"],
        "end": items[0]["cohort_end"],
        "n_still_listed": n,
    }
    for t in THRESHOLDS:
        c = sum(1 for r in items if r["adu"] >= t)
        out[f"adu_ge_{t}"] = c
        out[f"share_ge_{t}"] = f"{(c/n if n else 0):.5f}"
    cohort_rows.append(out)

with (ROOT / "cohorts_current_adu.csv").open("w", newline="", encoding="utf-8") as f:
    fieldnames = ["cohort", "start", "end", "n_still_listed"] + sum(([f"adu_ge_{t}", f"share_ge_{t}"] for t in THRESHOLDS), [])
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows(cohort_rows)

recent = [r for r in rows if r["cohort"] in RECENT]
top = sorted(recent, key=lambda r: (r["adu"], r["weekly"], r["ratings_n"]), reverse=True)[:30]
# Keep top 15 in CSV/report source to allow spot checks beyond the requested ~10.
top_rows = []
for i, r in enumerate(top, 1):
    text = " ".join([r.get("name", ""), r.get("summary", ""), r.get("description", ""), r.get("tags", "")])
    ai_themed = bool(AI_WORDS.search(text))
    explicitly_ai_built = bool(AI_BUILT_WORDS.search(text))
    # Conservative heuristic; the report manually refines this field for the top 10.
    likely_established = bool(ESTABLISHED_WORDS.search(text)) or r["homepage_url"] or r["support_url"]
    top_rows.append({
        "rank": i,
        "cohort": r["cohort"],
        "name": r["name"],
        "slug": r["slug"],
        "created": r["created"],
        "average_daily_users": r["adu"],
        "weekly_downloads": r["weekly"],
        "ratings_count": r["ratings_n"],
        "ai_themed_from_text": ai_themed,
        "explicitly_ai_built_from_text": explicitly_ai_built,
        "likely_established_or_companion_heuristic": likely_established,
        "summary": r["summary"],
        "url": r["url"],
        "homepage_url": r["homepage_url"],
        "support_url": r["support_url"],
        "authors": r["authors"],
    })
with (ROOT / "top_recent_current_adu.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(top_rows[0].keys()))
    w.writeheader(); w.writerows(top_rows)

# Helpful aggregate for qualitative AI-themed counts in recent cohorts.
ai_counts = []
for cohort in sorted(RECENT):
    items = by.get(cohort, [])
    n = len(items)
    ai = 0; ai10 = 0; built = 0
    for r in items:
        text = " ".join([r.get("name", ""), r.get("summary", ""), r.get("description", ""), r.get("tags", "")])
        if AI_WORDS.search(text):
            ai += 1
            if r["adu"] >= 10: ai10 += 1
        if AI_BUILT_WORDS.search(text):
            built += 1
    ai_counts.append({"cohort": cohort, "n": n, "ai_themed_text_hits": ai, "ai_themed_adu_ge_10": ai10, "explicit_ai_built_text_hits": built})
(ROOT / "ai_text_counts_recent.json").write_text(json.dumps(ai_counts, indent=2))
print(json.dumps({"rows": len(rows), "cohorts": len(cohort_rows), "top_recent_written": len(top_rows), "ai_counts": ai_counts}, indent=2))
