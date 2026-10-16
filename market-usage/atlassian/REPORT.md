# Atlassian Marketplace usage cohort analysis

Generated 2026-10-15. Output files: `scripts/fetch_analyze_atlassian.py`, `scripts/write_report.py`, raw API caches in `cache/`, and derived CSVs in `data/`.

## Source and method

- Source: Atlassian Marketplace public REST API: `/rest/2/addons?limit=50&offset=N&hosting=cloud|dataCenter|server` and `/rest/2/addons/<key>/versions?hosting=...`.
- Scope: current public listings returned by the API: 6687 Cloud rows, 1589 Data Center rows, 2262 Server rows, 8295 unique add-ons. I collapsed Data Center and Server into one self-managed segment.
- Cohort date: earliest public version date returned by the version endpoint for that hosting. This is a hosting-specific first-version date, not guaranteed to be the vendor's original product launch date; Atlassian's own Marketplace guidance says a cloud app with the same essential functionality as an existing server app should share the same listing, so cloud/DC migrations can look like new hosted cohorts.
- Usage metric: current `distribution.totalInstalls`, with thresholds low ≥10, modest ≥100, high ≥1,000 active installs. `downloads ≥100` is included as a supplementary self-managed signal because Server/Data Center downloads are more visible historically than live installs.
- Equal-age usage: not available at registry scale. I checked Wayback CDX for representative API listing URLs and found no API snapshots; app pages have snapshots, but the install counters are page/dynamic content and not practical for a full equal-age scrape in this pass. Current installs favor old cohorts, so recent cohorts beating older cohorts is strong evidence; recent cohorts trailing older cohorts is weak evidence.
- Payment split: latest public version `paymentModel` per hosting; `atlassian`/`vendor` are paid, other or blank values are treated as free.
- AI flag: regex over name/tagline/summary/categories (`AI`, Rovo, agent, GPT/LLM, Copilot, Claude, Cursor, etc.). Established-vendor proxy: the vendor has another current Marketplace app first seen before 2025 or at least 3 current apps with first-seen before 2025H2; this undercounts established companies new to Marketplace such as GitHub/Microsoft.

## High-level comparison

Average current-survivor listings and install-threshold counts per half-year:

|segment|period|apps/half|≥100 installs/half|≥1k installs/half|
|---|---|---|---|---|
|cloud|2021-24 avg/half|287.2|70.5|9.1|
|cloud|2025H1|919.0|274.0|69.0|
|cloud|2025H2-26H2 avg/half|825.7|30.0|2.3|
|dc_server|2021-24 avg/half|55.6|17.8|4.8|
|dc_server|2025H1|265.0|81.0|12.0|
|dc_server|2025H2-26H2 avg/half|39.7|6.3|1.3|

Interpretation: Cloud supply jumps sharply after 2025, but post-2025H1 modest/high install counts do not scale with supply. The anomalous 2025H1 Cloud and DC/Server spike is dominated by established vendors and likely includes migrations/relistings or first visible hosted versions, not only genuinely new projects.

## Cohort table: totals

`apps` are current survivors listed in that half-year; install thresholds are current installs.

|segment|cohort|apps|paid|free|≥10|≥100|≥1k|downloads≥100|AI flags|
|---|---|---|---|---|---|---|---|---|---|
|cloud|2021H1|173|117|56|131|86|15|55|13|
|cloud|2021H2|578|477|101|428|119|15|68|16|
|cloud|2022H1|237|124|113|152|69|8|55|34|
|cloud|2022H2|241|141|100|144|71|9|51|20|
|cloud|2023H1|313|193|120|207|77|13|60|50|
|cloud|2023H2|268|152|116|153|69|7|46|37|
|cloud|2024H1|328|184|144|173|53|6|52|42|
|cloud|2024H2|160|87|73|80|20|0|19|22|
|cloud|2025H1|919|634|285|564|274|69|174|130|
|cloud|2025H2|433|311|122|144|30|3|21|93|
|cloud|2026H1|1060|757|303|223|53|3|29|201|
|cloud|2026H2|984|778|206|60|7|1|17|109|
|dc_server|2021H1|130|100|30|68|29|4|127|6|
|dc_server|2021H2|57|42|15|39|17|4|54|1|
|dc_server|2022H1|39|24|15|22|13|3|34|2|
|dc_server|2022H2|43|31|12|30|16|7|40|1|
|dc_server|2023H1|61|41|20|41|25|8|61|4|
|dc_server|2023H2|44|31|13|31|19|7|43|2|
|dc_server|2024H1|40|22|18|24|15|3|38|5|
|dc_server|2024H2|31|24|7|17|8|2|31|4|
|dc_server|2025H1|265|176|89|172|81|12|246|19|
|dc_server|2025H2|68|51|17|27|9|2|52|3|
|dc_server|2026H1|26|17|9|8|6|0|18|2|
|dc_server|2026H2|25|13|12|9|4|2|19|3|

## Cohort table: free/paid split

|segment|payment|cohort|apps|≥100|≥1k|%≥100|est. vendor proxy|
|---|---|---|---|---|---|---|---|
|cloud|free|2021H1|56|23|4|41.1%|56|
|cloud|free|2021H2|101|29|4|28.7%|101|
|cloud|free|2022H1|113|29|4|25.7%|113|
|cloud|free|2022H2|100|24|0|24.0%|100|
|cloud|free|2023H1|120|23|4|19.2%|120|
|cloud|free|2023H2|116|24|3|20.7%|116|
|cloud|free|2024H1|144|23|4|16.0%|144|
|cloud|free|2024H2|73|8|0|11.0%|73|
|cloud|free|2025H1|285|63|12|22.1%|161|
|cloud|free|2025H2|122|11|1|9.0%|66|
|cloud|free|2026H1|303|19|3|6.3%|107|
|cloud|free|2026H2|206|4|1|1.9%|49|
|cloud|paid|2021H1|117|63|11|53.8%|117|
|cloud|paid|2021H2|477|90|11|18.9%|477|
|cloud|paid|2022H1|124|40|4|32.3%|124|
|cloud|paid|2022H2|141|47|9|33.3%|141|
|cloud|paid|2023H1|193|54|9|28.0%|193|
|cloud|paid|2023H2|152|45|4|29.6%|152|
|cloud|paid|2024H1|184|30|2|16.3%|184|
|cloud|paid|2024H2|87|12|0|13.8%|87|
|cloud|paid|2025H1|634|211|57|33.3%|525|
|cloud|paid|2025H2|311|19|2|6.1%|208|
|cloud|paid|2026H1|757|34|0|4.5%|304|
|cloud|paid|2026H2|778|3|0|0.4%|140|
|dc_server|free|2021H1|30|5|1|16.7%|30|
|dc_server|free|2021H2|15|3|0|20.0%|15|
|dc_server|free|2022H1|15|3|2|20.0%|15|
|dc_server|free|2022H2|12|3|1|25.0%|12|
|dc_server|free|2023H1|20|7|3|35.0%|20|
|dc_server|free|2023H2|13|5|3|38.5%|13|
|dc_server|free|2024H1|18|4|2|22.2%|18|
|dc_server|free|2024H2|7|1|0|14.3%|7|
|dc_server|free|2025H1|89|25|3|28.1%|67|
|dc_server|free|2025H2|17|3|1|17.6%|12|
|dc_server|free|2026H1|9|3|0|33.3%|8|
|dc_server|free|2026H2|12|2|1|16.7%|12|
|dc_server|paid|2021H1|100|24|3|24.0%|100|
|dc_server|paid|2021H2|42|14|4|33.3%|42|
|dc_server|paid|2022H1|24|10|1|41.7%|24|
|dc_server|paid|2022H2|31|13|6|41.9%|31|
|dc_server|paid|2023H1|41|18|5|43.9%|41|
|dc_server|paid|2023H2|31|14|4|45.2%|31|
|dc_server|paid|2024H1|22|11|1|50.0%|22|
|dc_server|paid|2024H2|24|7|2|29.2%|24|
|dc_server|paid|2025H1|176|56|9|31.8%|159|
|dc_server|paid|2025H2|51|6|1|11.8%|44|
|dc_server|paid|2026H1|17|3|0|17.6%|12|
|dc_server|paid|2026H2|13|2|1|15.4%|10|

## Top recent items check

Top current installs among apps whose hosting-specific first version is 2025-07-01 or later:

|segment|first date|installs|downloads|pay|AI|item|vendor|vendor proxy|
|---|---|---|---|---|---|---|---|---|
|cloud|2026-06-05|9105|0|free|yes|Claude Agent for Jira|Atlassian|yes|
|dc_server|2025-09-04|8640|54698|paid||Power BI Connector for Jira|Tempo Software|yes|
|dc_server|2025-09-03|6761|11138|free||Cloud companion|Atlassian|yes|
|cloud|2025-10-16|4620|90723|paid||Smart Checklists for Jira|TitanApps|yes|
|cloud|2026-05-14|3612|0|free|yes|Cursor|Cursor|no/new-to-Marketplace|
|cloud|2026-05-11|3445|0|free|yes|GitHub Copilot for Jira|GitHub|no/new-to-Marketplace|
|cloud|2025-11-06|3328|79111|paid|yes|Easy Agile TeamRhythm: Story Map, Insights & Retrospectives|Easy Agile|yes|
|dc_server|2026-09-03|2118|397|paid||Event Calendar for Jira|ALDEVA DIGITAL|yes|
|cloud|2026-08-03|1090|381|free||Clockify: Time Tracking & Timesheet 2-Way Sync|CAKE.com Inc|yes|
|dc_server|2026-08-03|1090|381|free||Clockify: Time Tracking & Timesheet 2-Way Sync|CAKE.com Inc|yes|
|cloud|2025-09-17|1005|0|free||SprintRetro – Free Retrospective & Metrics Suite|Agile Pulse|yes|
|dc_server|2026-06-10|988|27|paid||Kanban Analytics: Improve Your Delivery Process|Nave|no/new-to-Marketplace|
|dc_server|2025-10-31|984|1014|free||Sum Up Reports for Jira & Confluence|Bloompeak|yes|
|cloud|2026-01-21|848|0|paid||Monte Carlo Simulations & Capacity Planning for Scrum/Kanban|Broken Build|yes|
|cloud|2025-10-27|842|0|paid||Cumulative Flow Diagrams/CFD for Jira (Agile Charts Gadgets)|Broken Build|yes|
|cloud|2026-02-10|829|0|paid||Throughput Charts for Scrum, Kanban, SAFe (Gadgets Reports)|Broken Build|yes|
|cloud|2026-03-17|813|0|paid||Created vs Resolved charts for Scrum, Kanban (Agile Reports)|Broken Build|yes|
|cloud|2026-01-22|800|25834|paid||User/Group Export & License Optimizer for Jira|Aety admin apps|yes|
|cloud|2026-03-23|797|0|paid||WIP Aging Reports & Run Charts: Kanban, Scrum, SAFe in Jira|Broken Build|yes|
|dc_server|2025-07-01|774|1136|paid||Agile Planning Poker, Retrospectives, Daily Standup for Jira|DevSamurai|yes|
|dc_server|2025-12-30|766|560|paid||Space Sync for Confluence (Copy & Publish Pages over Sites)|Ricksoft, Inc.|yes|
|cloud|2026-02-11|666|0|paid|yes|SprintPoker – Planning Poker & Async Estimation|Agile Pulse|yes|
|cloud|2025-07-24|650|4|paid||Google Sheets|ikuTeam (File Automation & Wor|yes|
|cloud|2026-05-22|623|0|free|yes|SprintPoker – Free Planning Poker & Async Estimation|Agile Pulse|yes|
|cloud|2026-04-28|591|0|paid||SprintRetro Pro – Retrospective & Metrics Suite|Agile Pulse|yes|

Top-recent summary: among the top 50 post-2025H1 items, 8 are AI/agent-flagged and 45 are from established Marketplace vendors by the proxy. The visible new-high-install AI apps are mostly direct developer/agent integrations: Atlassian's Claude Agent for Jira (9,105 installs), Cursor (3,612), and GitHub Copilot for Jira (3,445). Most non-AI recent leaders are established Marketplace vendors repackaging or extending familiar Jira/Confluence workflows (BI connectors, checklists, agile reports, calendars, sync/export utilities).

## Confounders and data caveats

- **Current survivors only:** removed, delisted, archived, private, or policy-rejected apps are absent. This biases supply downward for old cohorts and can make recent supply look cleaner than actual submission volume.
- **Server end of support and cloud migration:** Atlassian announced Server product support ended February 15, 2024; this likely pushed customers and vendors toward Cloud/Data Center offerings and can create demand for migration, admin, connector, and companion apps. Current Atlassian migration pages also emphasize Data Center moving toward end of life in 2029 and cloud migration.
- **Connect → Forge transition:** the API data show a strong cloud framework shift: 2026 cloud cohorts are almost entirely `latest_connect=false` (Forge-like by this API field). Atlassian's Connect-to-Forge docs say Marketplace apps can keep listings, reviews, and installations while adopting Forge, so first Forge/cloud versions can be product-transition events rather than wholly new tools; I did not verify a public hard cutoff saying all new Marketplace listings became Forge-only in 2025.
- **Rovo/AI agents:** Atlassian's Rovo pages describe Search, Chat, Agents, and Studio as Cloud AI features; top recent apps include several agent/coding integrations, especially Claude Agent for Jira, Cursor, and GitHub Copilot for Jira. These are the clearest recent big hits.
- **Marketplace review/policy:** Atlassian's app approval guidelines require performance, no UI breakage, docs, privacy/security requirements, no duplicate cloud/server listings for the same functionality, and Marketplace Partner Agreement acceptance. Review or policy changes can affect listing counts independent of builder supply.
- **Usage age bias:** because usage is current rather than equal-age, 2026H2 has only a partial half-year and far less time to accumulate installs. The absence of many ≥1k hits after 2025H1 is still notable because high-reach professional tools often inherit established-vendor distribution, but it is not a strict equal-age comparison.

## References checked

- Atlassian Marketplace API: `https://marketplace.atlassian.com/rest/2/addons?...` and `/rest/2/addons/<key>/versions?...`.
- Server/cloud migration: https://www.atlassian.com/blog/company-news/journey-to-cloud and https://www.atlassian.com/migration
- Connect-to-Forge: https://developer.atlassian.com/platform/adopting-forge-from-connect/
- Rovo: https://www.atlassian.com/software/rovo
- Marketplace approval/listing rules: https://developer.atlassian.com/platform/marketplace/app-approval-guidelines/ and https://developer.atlassian.com/platform/marketplace/listing-connect-apps/

## Three-sentence verdict

Atlassian Marketplace shows **much more supply**, especially Cloud: current-survivor Cloud listings average 826 per half-year in 2025H2-2026H2 versus 287 per half-year in 2021-2024, with a separate 2025H1 spike to 919. It does **not** show a proportional rise in modestly used non-AI tools after the AI-coding inflection: Cloud modest-install apps average 30 per half-year in 2025H2-2026H2 versus 70.5 in 2021-2024, although 2025H1 is a migration/relisting-heavy exception at 274. It shows **few new big hits** after 2025H1, and the standout recent big hits are AI/agent integrations or established-vendor workflow apps rather than a broad wave of newly used professional software.
