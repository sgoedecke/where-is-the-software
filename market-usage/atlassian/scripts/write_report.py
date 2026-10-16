#!/usr/bin/env python3
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'

def read_csv(name):
    return list(csv.DictReader(open(DATA/name, encoding='utf-8')))

def md_table(rows, cols, headers=None):
    headers=headers or cols
    out=['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(cols))+'|']
    for r in rows:
        vals=[]
        for c in cols:
            v=str(r.get(c,''))
            v=v.replace('|','\\|').replace('\n',' ')
            vals.append(v)
        out.append('|'+'|'.join(vals)+'|')
    return '\n'.join(out)

totals=read_csv('cohorts_by_segment_totals.csv')
split=read_csv('cohorts_by_segment_payment.csv')
top=read_csv('top_recent_since_2025H2.csv')
meta=json.load(open(DATA/'analysis_metadata.json', encoding='utf-8'))

# full totals but compact column names
for r in totals:
    r['>=10']=r['installs_ge_10']; r['>=100']=r['installs_ge_100_modest']; r['>=1k']=r['installs_ge_1000_high']; r['dl>=100']=r['downloads_ge_100']; r['AI']=r['ai_flag_count']
for r in split:
    r['apps']=r['apps_listed_current_survivors']; r['>=100']=r['installs_ge_100_modest']; r['>=1k']=r['installs_ge_1000_high']; r['share>=100']=r['share_ge_100']; r['est.vendor']=r['established_vendor_proxy_count']
for r in top:
    r['est_vendor_proxy']='yes' if r['vendor_established_proxy']=='True' else 'no/new-to-Marketplace'
    r['AI']='yes' if r['ai_flag']=='True' else ''
    r['item']=r['name'][:64]
    r['vendor']=r['vendor_name'][:30]

period_rows=[]
for seg in ['cloud','dc_server']:
    for label,pred in [('2021-24 avg/half', lambda c: '2021H1'<=c<='2024H2'),('2025H1', lambda c:c=='2025H1'),('2025H2-26H2 avg/half', lambda c:c>='2025H2')]:
        ss=[r for r in totals if r['segment']==seg and pred(r['cohort'])]
        if not ss: continue
        n=len(ss)
        period_rows.append({
            'segment':seg,'period':label,
            'apps':f"{sum(int(r['apps']) for r in ss)/n:.1f}",
            '>=100':f"{sum(int(r['installs_ge_100_modest']) for r in ss)/n:.1f}",
            '>=1k':f"{sum(int(r['installs_ge_1000_high']) for r in ss)/n:.1f}",
        })

report=f"""# Atlassian Marketplace usage cohort analysis

Generated 2026-10-15. Output files: `scripts/fetch_analyze_atlassian.py`, `scripts/write_report.py`, raw API caches in `cache/`, and derived CSVs in `data/`.

## Source and method

- Source: Atlassian Marketplace public REST API: `/rest/2/addons?limit=50&offset=N&hosting=cloud|dataCenter|server` and `/rest/2/addons/<key>/versions?hosting=...`.
- Scope: current public listings returned by the API: {meta['current_listing_counts_by_hosting_filter'].get('cloud',0)} Cloud rows, {meta['current_listing_counts_by_hosting_filter'].get('dataCenter',0)} Data Center rows, {meta['current_listing_counts_by_hosting_filter'].get('server',0)} Server rows, {meta['unique_addons_observed']} unique add-ons. I collapsed Data Center and Server into one self-managed segment.
- Cohort date: earliest public version date returned by the version endpoint for that hosting. This is a hosting-specific first-version date, not guaranteed to be the vendor's original product launch date; Atlassian's own Marketplace guidance says a cloud app with the same essential functionality as an existing server app should share the same listing, so cloud/DC migrations can look like new hosted cohorts.
- Usage metric: current `distribution.totalInstalls`, with thresholds low ≥10, modest ≥100, high ≥1,000 active installs. `downloads ≥100` is included as a supplementary self-managed signal because Server/Data Center downloads are more visible historically than live installs.
- Equal-age usage: not available at registry scale. I checked Wayback CDX for representative API listing URLs and found no API snapshots; app pages have snapshots, but the install counters are page/dynamic content and not practical for a full equal-age scrape in this pass. Current installs favor old cohorts, so recent cohorts beating older cohorts is strong evidence; recent cohorts trailing older cohorts is weak evidence.
- Payment split: latest public version `paymentModel` per hosting; `atlassian`/`vendor` are paid, other or blank values are treated as free.
- AI flag: regex over name/tagline/summary/categories (`AI`, Rovo, agent, GPT/LLM, Copilot, Claude, Cursor, etc.). Established-vendor proxy: the vendor has another current Marketplace app first seen before 2025 or at least 3 current apps with first-seen before 2025H2; this undercounts established companies new to Marketplace such as GitHub/Microsoft.

## High-level comparison

Average current-survivor listings and install-threshold counts per half-year:

{md_table(period_rows, ['segment','period','apps','>=100','>=1k'], ['segment','period','apps/half','≥100 installs/half','≥1k installs/half'])}

Interpretation: Cloud supply jumps sharply after 2025, but post-2025H1 modest/high install counts do not scale with supply. The anomalous 2025H1 Cloud and DC/Server spike is dominated by established vendors and likely includes migrations/relistings or first visible hosted versions, not only genuinely new projects.

## Cohort table: totals

`apps` are current survivors listed in that half-year; install thresholds are current installs.

{md_table(totals, ['segment','cohort','apps','paid_apps','free_apps','>=10','>=100','>=1k','dl>=100','AI'], ['segment','cohort','apps','paid','free','≥10','≥100','≥1k','downloads≥100','AI flags'])}

## Cohort table: free/paid split

{md_table(split, ['segment','payment','cohort','apps','>=100','>=1k','share>=100','est.vendor'], ['segment','payment','cohort','apps','≥100','≥1k','%≥100','est. vendor proxy'])}

## Top recent items check

Top current installs among apps whose hosting-specific first version is 2025-07-01 or later:

{md_table(top[:25], ['segment','first_release_date','total_installs','downloads','payment_bucket','AI','item','vendor','est_vendor_proxy'], ['segment','first date','installs','downloads','pay','AI','item','vendor','vendor proxy'])}

Top-recent summary: among the top 50 post-2025H1 items, {meta['recent_top50_ai_flags']} are AI/agent-flagged and {meta['recent_top50_established_vendors']} are from established Marketplace vendors by the proxy. The visible new-high-install AI apps are mostly direct developer/agent integrations: Atlassian's Claude Agent for Jira (9,105 installs), Cursor (3,612), and GitHub Copilot for Jira (3,445). Most non-AI recent leaders are established Marketplace vendors repackaging or extending familiar Jira/Confluence workflows (BI connectors, checklists, agile reports, calendars, sync/export utilities).

## Confounders and data caveats

- **Current survivors only:** removed, delisted, archived, private, or policy-rejected apps are absent. This biases supply downward for old cohorts and can make recent supply look cleaner than actual submission volume.
- **Server end of support and cloud migration:** Atlassian announced Server product support ended February 15, 2024; this likely pushed customers and vendors toward Cloud/Data Center offerings and can create demand for migration, admin, connector, and companion apps. Current Atlassian migration pages also emphasize Data Center moving toward end of life in 2029 and cloud migration.
- **Connect → Forge transition:** the API data show a strong cloud framework shift: 2026 cloud cohorts are almost entirely `latest_connect=false` (Forge-like by this API field). Atlassian's Connect-to-Forge docs say Marketplace apps can keep listings, reviews, and installations while adopting Forge, so first Forge/cloud versions can be product-transition events rather than wholly new tools; I did not verify a public hard cutoff saying all new Marketplace listings became Forge-only in 2025.
- **Rovo/AI agents:** Atlassian's Rovo pages describe Search, Chat, Agents, and Studio as Cloud AI features; top recent apps include several agent/coding integrations, especially Claude Agent for Jira, Cursor, and GitHub Copilot for Jira. These are the clearest recent big hits.
- **Marketplace review/policy:** Atlassian's app approval guidelines require performance, no UI breakage, docs, privacy/security requirements, no duplicate cloud/server listings for the same functionality, and Marketplace Partner Agreement acceptance. Review or policy changes can affect listing counts independent of builder supply.
- **Usage age bias:** because usage is current rather than equal-age, 2026H2 has only a partial half-year and far less time to accumulate installs. The absence of many ≥1k hits after 2025H1 is still notable because high-reach professional tools often inherit established-vendor distribution, but it is not a strict equal-age comparison.

## Three-sentence verdict

Atlassian Marketplace shows **much more supply**, especially Cloud: current-survivor Cloud listings average 826 per half-year in 2025H2-2026H2 versus 287 per half-year in 2021-2024, with a separate 2025H1 spike to 919. It does **not** show a proportional rise in modestly used non-AI tools after the AI-coding inflection: Cloud modest-install apps average 30 per half-year in 2025H2-2026H2 versus 70.5 in 2021-2024, although 2025H1 is a migration/relisting-heavy exception at 274. It shows **few new big hits** after 2025H1, and the standout recent big hits are AI/agent integrations or established-vendor workflow apps rather than a broad wave of newly used professional software.
"""
(ROOT/'REPORT.md').write_text(report, encoding='utf-8')
print(ROOT/'REPORT.md')
