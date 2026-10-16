#!/usr/bin/env python3
import csv
from pathlib import Path

TODAY = '2026-10-15'
OUT = Path(__file__).resolve().parent

def read_csv(name):
    with (OUT / name).open(encoding='utf-8') as f:
        return list(csv.DictReader(f))

def md_table(rows, cols):
    lines = ['| ' + ' | '.join(cols) + ' |', '| ' + ' | '.join(['---'] * len(cols)) + ' |']
    for r in rows:
        lines.append('| ' + ' | '.join(str(r.get(c, '')) for c in cols) + ' |')
    return '\n'.join(lines)

def avg(rows, key):
    return sum(int(r[key]) for r in rows) / len(rows)

cohorts = read_csv('cohorts.csv')
top = read_csv('top_recent_plugins.csv')
wayback = read_csv('wayback_sample.csv')
base = [r for r in cohorts if r['cohort'] in ['2022H1','2022H2','2023H1','2023H2','2024H1','2024H2']]
api_total = '75,808'
since_total = '35,207'
cohort_cols = ['cohort','still_listed_created','active_ge_100','share_active_ge_100','active_ge_1000','share_active_ge_1000','active_ge_10000','share_active_ge_10000','dl_per_day_ge_10','share_dl_per_day_ge_10','dl_per_day_ge_50','share_dl_per_day_ge_50']
top_cols = ['rank','name','slug','added','active_installs','downloaded','downloads_per_day','ai_theme','explicit_ai_built','judgment']
wayback_cols = ['slug','added','current_active_installs','snapshot_date','age_days','archived_active_installs','note']
verdict = (
    f"The WordPress directory supports the 'more small/lightly used tools' half of the hypothesis mainly through supply: still-listed creations rose from a 2022–24 half-year average of {avg(base,'still_listed_created'):.0f} to 3,449 in 2025H2, 7,533 in 2026H1, and a partial 9,899 in 2026H2. "
    f"It does not show a matching boom in current active-use hits: the 2022–24 averages were {avg(base,'active_ge_100'):.0f} plugins at ≥100 installs, {avg(base,'active_ge_1000'):.0f} at ≥1,000, and {avg(base,'active_ge_10000'):.0f} at ≥10,000, versus 409/79/14 in 2025H2, 358/54/22 in 2026H1, and 136/13/4 so far in 2026H2. "
    "Wayback spot checks and download-per-day rates show that a few recent platform-backed, connector, and AI-feature plugins grew very fast, but the cohort-level result is a flood of new listings with sharply lower shares clearing install buckets, not clear evidence of more new broadly adopted software."
)
report = f"""# WordPress.org plugin directory niche-usage cohorts

Source: WordPress.org Plugins API (`query_plugins`, `browse=new`) fetched on {TODAY} with `per_page=250`. The API reported {api_total} currently listed plugins; this analysis uses the {since_total} still-listed plugins whose `added` date is >= 2021-01-01.

## Cohort table

Usage thresholds are current active-install buckets, not equal-age measurements. `downloads_per_day` is cumulative `downloaded` divided by days since `added`, included as a rough age-normalized velocity proxy.

{md_table(cohorts, cohort_cols)}

## Method

I enumerated all newest-first API pages until the results crossed below 2021-01-01, using a User-Agent and short sleeps between requests. For each still-listed plugin I retained `slug`, `name`, `added`, `active_installs`, `downloaded`, `rating`, `num_ratings`, `last_updated`, homepage, and short description, then grouped plugins into half-year creation cohorts. Active-install thresholds are the requested WordPress buckets (≥100, ≥1,000, ≥10,000); because the API gives current bucketed installs rather than historical equal-age installs, older cohorts have more time to accumulate usage. As an equal-age-ish alternative, I report `downloaded / age_days` velocity columns; it is still imperfect because downloads include updates, bots, CI, and release cadence.

I also sampled Wayback CDX snapshots for top recent plugins and parsed archived `Active installations` where available. This sample is useful as a sanity check on fast early growth, but it is deliberately not used for the full cohort table because snapshots are sparse, plugin-page markup changes, and the sample is top-heavy.

I did not recover removed or closed plugins. WordPress.org's public API drops closed/removed plugins, so `still_listed_created` is a survivorship count, not the true number submitted, approved, or initially listed.

## Wayback equal-age spot checks

{md_table(wayback, wayback_cols)}

## Top current-use plugins added in 2025H2–2026

{md_table(top, top_cols)}

Spot-check notes: the top recent plugins are mostly AI-feature products, hosting/vendor-backed plugins, WooCommerce ad-network connectors, or narrow site-management/form utilities. Rows marked `ai_theme=yes` describe AI functionality; none of the top ten stated in its WordPress.org description that the plugin itself was AI-built/generated.

## Confounders and ecosystem events

- **Survivorship:** closed, delisted, rejected, and removed plugins disappear from the query API. Counts here are "created and still listed".
- **Current-use/age confounding:** `active_installs` is current and bucketed. Old plugins had more time to acquire installs; strong recent performance is robust, but weak recent performance can be inconclusive.
- **Download-rate noise:** `downloaded / age_days` partly controls age, but WordPress downloads include updates/reinstalls and can be inflated by bots, CI, and release cadence. Very young 2026H2 plugins can look high on downloads/day after launch bursts.
- **Review queue and AI submissions:** the Plugins Team said submissions doubled in 2025, 2025 reviews reached 12,713 (+40.6% vs 2024), approvals were 5,415 (+66.2%), and AI affected both plugin submissions and review tooling. Source: https://make.wordpress.org/plugins/2026/01/07/a-year-in-the-plugins-team-2025/
- **2025 queue stats:** by Aug. 31, 2025 the team reported 60,187 published plugins, 7,670 new submissions YTD (+87.3% YoY), an average of 235 submissions/week vs 124 the year before, and 85.3% of first reviews initiated by an automated AI/algorithmic system. Source: https://make.wordpress.org/plugins/2025/08/31/stats-of-plugins-team-after-wordcamp-us/
- **2026 submission surge/backlog:** in Mar. 2026 the team reported weekly submissions had quadrupled vs 2024 and exceeded 500/week; in Jun. 2026 they reported the queue peaked near 1,050 in mid-April, fell near zero, and May hit ~700 submissions/week and nearly 3,000 initial reviews. Sources: https://make.wordpress.org/plugins/2026/03/13/contribute-to-the-plugins-team/ and https://make.wordpress.org/plugins/2026/06/13/update-on-the-status-of-the-team-june-2026/
- **Security/release policy:** WordPress.org announced Protect the Shire in Jun. 2026, temporarily delaying plugin/theme release auto-updates up to 24 hours amid AI-era supply-chain risk. Source: https://wordpress.org/news/2026/06/pts/
- **WP Engine dispute:** 2024–25 WordPress.org governance/distribution disputes may have affected developer behavior and trust, but I did not find a Plugins Team post quantifying its plugin-directory submission effect.

## 3-sentence verdict

{verdict}
"""
(OUT / 'REPORT.md').write_text(report, encoding='utf-8')
print('wrote REPORT.md')
