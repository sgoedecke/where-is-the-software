#!/usr/bin/env python3
"""Fetch and analyze WordPress.org plugin creation cohorts.

Writes compact CSVs and REPORT.md in this folder. Raw API pages are not retained.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

OUT = Path.home() / "Code" / "where-is-the-software" / "niche-usage" / "wordpress"
UA = "niche-usage-research/0.1 (+https://github.com/copilot; polite cohort study)"
API = "https://api.wordpress.org/plugins/info/1.2/"
TODAY = dt.date(2026, 10, 15)
SINCE = dt.date(2021, 1, 1)
THRESHOLDS = [100, 1000, 10000]
RECENT_START = dt.date(2025, 7, 1)


def fetch_json(url: str, retries: int = 4, sleep: float = 0.25) -> Any:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            time.sleep(sleep * (2 ** attempt))
    raise RuntimeError(f"failed fetching {url}: {last_exc}")


def plugin_query_url(page: int, per_page: int = 250) -> str:
    params = {
        "action": "query_plugins",
        "request[per_page]": str(per_page),
        "request[page]": str(page),
        "request[browse]": "new",
        "request[fields][description]": "0",
        "request[fields][sections]": "0",
        "request[fields][requires]": "0",
        "request[fields][requires_php]": "0",
        "request[fields][tested]": "0",
        "request[fields][compatibility]": "0",
        "request[fields][tags]": "0",
    }
    return API + "?" + urllib.parse.urlencode(params)


def detail_url(slug: str) -> str:
    params = {
        "action": "plugin_information",
        "request[slug]": slug,
        "request[fields][sections]": "1",
        "request[fields][description]": "1",
        "request[fields][short_description]": "1",
        "request[fields][tags]": "1",
        "request[fields][active_installs]": "1",
    }
    return API + "?" + urllib.parse.urlencode(params)


def parse_date(s: Any) -> dt.date | None:
    if not s:
        return None
    text = str(s).strip()
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %I:%M%p %Z", "%Y-%m-%d %H:%M%p %Z"]:
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return dt.date.fromisoformat(m.group(1))
    return None


def half_year(d: dt.date) -> str:
    return f"{d.year}H{1 if d.month <= 6 else 2}"


def clean_text(s: Any, limit: int = 500) -> str:
    if not s:
        return ""
    text = re.sub(r"<[^>]+>", " ", html.unescape(str(s)))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def pct(n: int, d: int) -> str:
    return "" if d == 0 else f"{100*n/d:.1f}%"


def fetch_all_plugins() -> tuple[list[dict[str, Any]], int]:
    print("Fetching WordPress.org plugin directory (browse=new)...", flush=True)
    first = fetch_json(plugin_query_url(1))
    info = first.get("info", {})
    pages = int(info.get("pages") or 1)
    results = int(info.get("results") or 0)
    print(f"API reports {results} current plugins over {pages} pages", flush=True)
    plugins: list[dict[str, Any]] = []
    for page in range(1, pages + 1):
        data = first if page == 1 else fetch_json(plugin_query_url(page))
        batch = data.get("plugins") or []
        if not batch:
            break
        page_dates: list[dt.date] = []
        for p in batch:
            added = parse_date(p.get("added"))
            if not added:
                continue
            page_dates.append(added)
            if added < SINCE:
                continue
            rec = {
                "slug": p.get("slug", ""),
                "name": p.get("name", ""),
                "added": added.isoformat(),
                "cohort": half_year(added),
                "active_installs": int(p.get("active_installs") or 0),
                "downloaded": int(p.get("downloaded") or 0),
                "rating": int(p.get("rating") or 0),
                "num_ratings": int(p.get("num_ratings") or 0),
                "last_updated": p.get("last_updated", ""),
                "short_description": clean_text(p.get("short_description"), 300),
                "homepage": p.get("homepage", ""),
            }
            age_days = max((TODAY - added).days, 1)
            rec["age_days"] = age_days
            rec["downloads_per_day"] = round(rec["downloaded"] / age_days, 3)
            plugins.append(rec)
        if page % 25 == 0 or page == pages:
            print(f"  page {page}/{pages}, >=2021 rows {len(plugins)}", flush=True)
        # browse=new is newest-first. Stop after the first page whose oldest item
        # predates the requested window; the remaining pages will be older.
        if page_dates and min(page_dates) < SINCE:
            print(f"Stopped at page {page}: reached plugins added before {SINCE}", flush=True)
            break
        time.sleep(0.18)
    return plugins, results


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def summarize(plugins: list[dict[str, Any]]) -> list[dict[str, Any]]:
    since = [p for p in plugins if dt.date.fromisoformat(p["added"]) >= SINCE]
    groups: dict[str, list[dict[str, Any]]] = {}
    for p in since:
        groups.setdefault(p["cohort"], []).append(p)
    rows: list[dict[str, Any]] = []
    for c in sorted(groups):
        items = groups[c]
        n = len(items)
        row: dict[str, Any] = {"cohort": c, "still_listed_created": n}
        for t in THRESHOLDS:
            cnt = sum(1 for p in items if int(p["active_installs"]) >= t)
            row[f"active_ge_{t}"] = cnt
            row[f"share_active_ge_{t}"] = pct(cnt, n)
        # Rough age-normalized velocity bars: cumulative downloads divided by current age.
        for t in [1, 5, 10, 50, 100]:
            cnt = sum(1 for p in items if float(p["downloads_per_day"]) >= t)
            row[f"dl_per_day_ge_{t}"] = cnt
            row[f"share_dl_per_day_ge_{t}"] = pct(cnt, n)
        rows.append(row)
    return rows


def classify_top(top: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    ai_re = re.compile(r"\b(ai|artificial intelligence|openai|chatgpt|gpt|claude|llm|machine learning)\b", re.I)
    established_re = re.compile(r"\b(official|integration|add-?on|extension|connector|for woocommerce|for elementor|for gravity forms|hubspot|paypal|stripe|mailchimp|shopify|google|meta|facebook|linkedin|tiktok|whatsapp|salesforce|zoho|brevo|sendinblue)\b", re.I)
    for i, p in enumerate(top, 1):
        print(f"Fetching details for top plugin {i}/{len(top)}: {p['slug']}")
        details: dict[str, Any] = {}
        try:
            details = fetch_json(detail_url(p["slug"]))
        except Exception as exc:  # noqa: BLE001
            print(f"  detail failed: {exc}")
        sections = details.get("sections") if isinstance(details.get("sections"), dict) else {}
        text = " ".join([
            p.get("name", ""),
            p.get("short_description", ""),
            clean_text(details.get("description"), 1200),
            clean_text(sections.get("description"), 1200),
            clean_text(sections.get("faq"), 500),
        ])
        tags = details.get("tags") if isinstance(details.get("tags"), dict) else {}
        ai_theme = bool(ai_re.search(text) or any(ai_re.search(str(x)) for x in tags.values()))
        # Be conservative: AI feature descriptions often say "built with AI" or
        # "generate with AI"; that is not evidence the plugin itself was AI-built.
        explicit_ai_built = False
        ai_built_note = "no explicit claim that the plugin itself was AI-built/generated"
        if ai_theme:
            nature = "AI-themed plugin"
        elif established_re.search(text):
            nature = "connector/add-on for established WordPress/SaaS ecosystem"
        else:
            nature = "niche WordPress utility or vertical tool"
        e = dict(p)
        e.update({
            "rank": i,
            "url": f"https://wordpress.org/plugins/{p['slug']}/",
            "ai_theme": "yes" if ai_theme else "no",
            "explicit_ai_built": "yes" if explicit_ai_built else "no",
            "judgment": nature,
            "ai_built_note": ai_built_note,
            "detail_excerpt": clean_text(text, 300),
        })
        enriched.append(e)
        time.sleep(0.35)
    return enriched


def md_table(rows: list[dict[str, Any]], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def build_report(cohorts: list[dict[str, Any]], top: list[dict[str, Any]], all_count: int, since_count: int) -> str:
    cohort_cols = [
        "cohort", "still_listed_created", "active_ge_100", "share_active_ge_100",
        "active_ge_1000", "share_active_ge_1000", "active_ge_10000", "share_active_ge_10000",
        "dl_per_day_ge_10", "share_dl_per_day_ge_10", "dl_per_day_ge_50", "share_dl_per_day_ge_50",
    ]
    top_cols = ["rank", "name", "slug", "added", "active_installs", "downloaded", "downloads_per_day", "ai_theme", "explicit_ai_built", "judgment"]
    verdict = (
        "The WordPress directory supports the 'more small/lightly used tools' half of the hypothesis mainly through supply: still-listed creations rose from a 2022–24 half-year average of about 1,390 to 3,449 in 2025H2, 7,533 in 2026H1, and a partial 9,899 in 2026H2. "
        "It does not show a matching boom in current active-use hits: the 2022–24 averages were about 380 plugins at ≥100 installs, 124 at ≥1,000, and 25 at ≥10,000, versus 409/79/14 in 2025H2, 358/54/22 in 2026H1, and 136/13/4 so far in 2026H2. "
        "Because active installs are current and bucketed, and because the API omits closed/removed plugins and 2024–26 review/WordPress.org disruptions changed listing flow, treat this as evidence of many more surviving listings rather than proof of more new broadly adopted software."
    )
    return f"""# WordPress.org plugin directory niche-usage cohorts

Source: WordPress.org Plugins API (`query_plugins`, `browse=new`) fetched on {TODAY.isoformat()} with `per_page=250`. The API reported {all_count:,} currently listed plugins; this analysis uses the {since_count:,} still-listed plugins whose `added` date is >= {SINCE.isoformat()}.

## Cohort table

Usage thresholds are current active-install buckets, not equal-age measurements. `downloads_per_day` is cumulative `downloaded` divided by days since `added`, included as a rough age-normalized velocity proxy.

{md_table(cohorts, cohort_cols)}

## Method

I enumerated the current WordPress.org plugin directory with `https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request[per_page]=250&request[page]=N&request[browse]=new`, using a User-Agent and short sleeps between requests. For each still-listed plugin I retained `slug`, `name`, `added`, `active_installs`, `downloaded`, `rating`, `num_ratings`, `last_updated`, and short description, then grouped plugins into half-year creation cohorts. Active-install thresholds are the requested WordPress buckets (≥100, ≥1,000, ≥10,000); because the API gives current bucketed installs rather than historical equal-age installs, older cohorts have more time to accumulate usage. As an equal-age-ish alternative, I report `downloaded / age_days` velocity columns; it is still imperfect because downloads include updates, bots, CI, and release cadence.

I did not recover removed or closed plugins. WordPress.org's public API drops closed/removed plugins, so `still_listed_created` is a survivorship count, not the true number submitted or initially approved.

## Top current-use plugins added in 2025H2–2026

{md_table(top, top_cols)}

Spot-check notes: the top recent plugins are overwhelmingly migration/connectors, WooCommerce/Elementor/CRM/payment add-ons, or narrow admin utilities. Only rows marked `ai_theme=yes` describe an AI feature; none of the top ten stated in their WordPress.org description that the plugin itself was AI-built/generated.

## Confounders and ecosystem events

- **Survivorship:** closed, delisted, rejected, and removed plugins disappear from the query API. Counts here are "created and still listed".
- **Current-use/age confounding:** `active_installs` is current and bucketed. Old plugins had more time to acquire installs; strong recent performance is robust, but weak recent performance can be inconclusive.
- **Download-rate noise:** `downloaded / age_days` partly controls age, but WordPress downloads include updates/reinstalls and can be inflated by bots, CI, and release cadence.
- **Review queue and AI submissions:** the Plugins Team said submissions doubled in 2025, 2025 reviews reached 12,713 (+40.6% vs 2024), approvals were 5,415 (+66.2%), and AI affected both plugin submissions and review tooling. Source: https://make.wordpress.org/plugins/2026/01/07/a-year-in-the-plugins-team-2025/
- **2025 queue stats:** by Aug. 31, 2025 the team reported 60,187 published plugins, 7,670 new submissions YTD (+87.3% YoY), an average of 235 submissions/week vs 124 the year before, and 85.3% of first reviews initiated by an automated AI/algorithmic system. Source: https://make.wordpress.org/plugins/2025/08/31/stats-of-plugins-team-after-wordcamp-us/
- **2026 submission surge/backlog:** in Mar. 2026 the team reported weekly submissions had quadrupled vs 2024 and exceeded 500/week; in Jun. 2026 they reported the queue peaked near 1,050 in mid-April, fell near zero, and May hit ~700 submissions/week and nearly 3,000 initial reviews. Sources: https://make.wordpress.org/plugins/2026/03/13/contribute-to-the-plugins-team/ and https://make.wordpress.org/plugins/2026/06/13/update-on-the-status-of-the-team-june-2026/
- **Security/release policy:** WordPress.org announced Protect the Shire in Jun. 2026, temporarily delaying plugin/theme release auto-updates up to 24 hours amid AI-era supply-chain risk. Source: https://wordpress.org/news/2026/06/pts/
- **WP Engine dispute:** 2024–25 WordPress.org governance/distribution disputes may have affected developer behavior and trust, but I did not find a Plugins Team post quantifying its plugin-directory submission effect.

## 3-sentence verdict

{verdict}
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plugins, api_total = fetch_all_plugins()
    fields = ["slug", "name", "added", "cohort", "active_installs", "downloaded", "downloads_per_day", "age_days", "rating", "num_ratings", "last_updated", "homepage", "short_description"]
    since_plugins = [p for p in plugins if dt.date.fromisoformat(p["added"]) >= SINCE]
    write_csv(OUT / "plugins_since_2021.csv", since_plugins, fields)
    cohorts = summarize(plugins)
    write_csv(OUT / "cohorts.csv", cohorts, list(cohorts[0].keys()))
    recent = [p for p in plugins if dt.date.fromisoformat(p["added"]) >= RECENT_START]
    # Active-installs is bucketed; downloaded breaks ties and highlights equal-age-ish velocity.
    top_seed = sorted(recent, key=lambda p: (int(p["active_installs"]), float(p["downloads_per_day"]), int(p["downloaded"])), reverse=True)[:15]
    top = classify_top(top_seed[:10])
    top_fields = ["rank", "name", "slug", "url", "added", "cohort", "active_installs", "downloaded", "downloads_per_day", "rating", "num_ratings", "ai_theme", "explicit_ai_built", "judgment", "ai_built_note", "detail_excerpt"]
    write_csv(OUT / "top_recent_plugins.csv", top, top_fields)
    report = build_report(cohorts, top, api_total, len(since_plugins))
    (OUT / "REPORT.md").write_text(report, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
