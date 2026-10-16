# Blender Extensions usage-cohort analysis

Date run: 2026-10-15. Scope: `extensions.blender.org` official extensions, with add-ons as the main population and themes reported separately.

## Sources and method

- Pulled `https://extensions.blender.org/api/v1/extensions/` and de-duplicated entries by `(type, website)`. The API had repeated rows for some extensions; final population is **1,389 unique extensions**: **1,112 add-ons**, **276 themes**, and 1 asset library.
- For each extension, fetched its `/versions/` page and used the earliest version date as first listed date. Current usage is the sum of per-version download counts on the version-history page, which matched/was more complete than the headline page count in spot checks. Thresholds: **low ≥100 downloads**, **modest ≥1,000**, **high ≥10,000**.
- Fetched every add-on detail page to extract GitHub links where present. For GitHub-linked add-ons, `gh api repos/{owner}/{repo}` supplied repo creation dates. A project is treated as “old/migrated” if its repo predated registry listing by ≥180 days. This is imperfect: some source links are missing, some projects moved repos, and non-GitHub originals are not dated.
- Equal-age usage: Wayback coverage exists but is not dense/reliable enough for full cohort counts. I sampled several page snapshots at 90/180 days; examples: VRM format had ~285k downloads at ~90 days, Modern Primitive ~56k at ~90 days and ~66k at ~180 days, Easy Tree ~39k at ~180 days. Main cohort table therefore uses current cumulative downloads, which favours older cohorts; recent cohorts clearing thresholds are still meaningful, while recent misses are weak evidence.
- Review queue: fetched live `/approval-queue/` pages and sampled Wayback copies. Current live queue table parsed 2,105 rows; the page reports ~2,189 results. Current open statuses: 22 awaiting review, 387 awaiting changes. First-page Wayback result counts grew from ~725 in Apr 2025 to ~1,045 in Oct 2025, ~1,761 in Jul 2026, and ~2,168 near Oct 2026.
- Supplement: GitHub Search for repos with topic `blender-addon` or `blender-addons`, created per half-year from 2021H1 onward. Stars are current stars only, a weak usage proxy.

Derived files: `data/extensions_current.csv`, `data/versions_current.csv`, `data/extensions_with_github_repos.csv`, `data/addon_cohort_quarter_summary.csv`, `data/addon_github_new_project_quarter_summary.csv`, `data/top_recent_addons_enriched.csv`, `data/github_topic_blender_addon_counts.csv`, `data/approval_queue_current.csv`, `data/wayback_equal_age_sample.csv`, `data/wayback_queue_sample.csv`.

## Add-on cohort table

Current cumulative downloads, grouped by first listed quarter. 2026Q4 is partial through Oct 15 and should not be compared as a full quarter.

| Listed cohort | Add-ons | Median age days | Median downloads | ≥100 | ≥1k | ≥10k | Top downloads |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024Q1 | 20 | 940 | 23,040 | 20 | 20 | 17 | 72,854 |
| 2024Q2 | 126 | 884 | 33,896 | 126 | 126 | 123 | 2,252,934 |
| 2024Q3 | 93 | 792 | 16,683 | 93 | 93 | 72 | 183,783 |
| 2024Q4 | 72 | 694 | 13,018 | 72 | 72 | 46 | 646,841 |
| 2025Q1 | 64 | 611 | 14,114 | 64 | 64 | 43 | 208,059 |
| 2025Q2 | 88 | 508 | 8,591 | 88 | 87 | 33 | 264,154 |
| 2025Q3 | 88 | 428 | 6,488 | 88 | 88 | 22 | 593,438 |
| 2025Q4 | 108 | 332 | 5,017 | 108 | 106 | 18 | 80,971 |
| 2026Q1 | 118 | 238 | 2,586 | 118 | 102 | 14 | 112,140 |
| 2026Q2 | 132 | 147 | 2,573 | 132 | 94 | 14 | 313,866 |
| 2026Q3 | 174 | 60 | 612 | 168 | 71 | 1 | 14,032 |
| 2026Q4 partial | 29 | 9 | 88 | 13 | 0 | 0 | 435 |

Interpretation:

- Supply rises clearly in the AI-agent era: 2025H1 had 152 add-ons, 2025H2 196, 2026H1 250, and 2026Q3 alone 174.
- Modest usage also rises in absolute terms despite recency: 2026H1 has 196 add-ons already at ≥1k downloads, above 2025H1's 151 and roughly matching 2025H2's 194. 2026Q3 has 71 ≥1k add-ons with median age only 60 days.
- Big hits do **not** rise. High-download counts are dominated by launch/backfill cohorts and older migrated tools; 2026Q1/Q2 have 14 high-download add-ons each, below most 2024/2025 quarters.

## Migration/new-project check

GitHub source coverage is high enough for a directional check: 858 unique GitHub repos were extracted across all extensions. “New project” means repo creation was within 180 days before listing, or after listing; “old” means created ≥180 days before listing.

| Cohort | Add-on supply | GitHub repos | Repo dates known | New projects | Old/migrated | New share of known |
|---|---:|---:|---:|---:|---:|---:|
| 2024Q3 | 93 | 63 | 54 | 24 | 30 | 44% |
| 2024Q4 | 72 | 53 | 47 | 34 | 13 | 72% |
| 2025Q1 | 64 | 51 | 46 | 32 | 14 | 70% |
| 2025Q2 | 88 | 67 | 59 | 40 | 19 | 68% |
| 2025Q3 | 88 | 70 | 62 | 46 | 16 | 74% |
| 2025Q4 | 108 | 86 | 73 | 54 | 19 | 74% |
| 2026Q1 | 118 | 99 | 91 | 80 | 11 | 88% |
| 2026Q2 | 132 | 111 | 102 | 91 | 11 | 89% |
| 2026Q3 | 174 | 152 | 132 | 123 | 9 | 93% |

This weakens the “just a migration wave” explanation after launch: 2024Q3 still contains many old projects, but by 2026 most GitHub-linked listed add-ons look genuinely new by repo creation date.

## Top recent items / backlog check

Top recent add-ons listed 2025H2–2026Q3 by current downloads:

| Downloads | Listed | Add-on | GitHub repo age check |
|---:|---|---|---|
| 593,438 | 2025-09-02 | MMD Tools | old repo, created 2021 |
| 313,866 | 2026-06-07 | VRM format | old repo, created 2019 |
| 259,629 | 2026-04-26 | Import Autodesk MAX (.max) | old repo, created 2024-05 |
| 175,223 | 2025-07-10 | Autodesk 3D Studio (.3ds) | old repo, created 2024-05 |
| 112,140 | 2026-02-23 | CloudRig | no GitHub repo found |
| 105,015 | 2026-03-29 | 3MF Import/Export | new-ish repo, created 2025-10 |
| 83,921 | 2026-04-07 | MustardUI | old repo, created 2020 |
| 80,971 | 2025-12-18 | Modern Primitive | old-ish repo, created 2024-12 |
| 80,260 | 2025-11-14 | Mixamo Rig | old repo, created 2024-08 |
| 68,537 | 2025-07-15 | Easy Tree | new repo, created 2025-07 |
| 56,508 | 2025-09-12 | Molecular Nodes | old repo, created 2022 |
| 51,913 | 2025-11-20 | Quick Studio Light | no GitHub repo found |
| 49,788 | 2026-01-24 | Paint System | old-ish repo, created 2024-12 |
| 43,333 | 2025-10-31 | Rigi-All | old repo, created 2024-02 |
| 42,854 | 2026-02-27 | Home Builder 5 | no GitHub repo found |

Among the top 60 recent add-ons, 51 had GitHub source links: 18 were clearly old/migrated, 30 looked new by repo creation date, and 12 were unknown/no date. The biggest recent hits are mostly migrated/pre-existing ecosystem tools, not brand-new projects.

AI/agent tooling: no approved/listed top recent add-ons matched MCP/LLM/GPT/OpenAI/Claude/ComfyUI keywords. The public approval queue did show AI/agent submissions, mostly not accepted/listed: BuddyCodeGPT awaiting changes, and Claude Bridge, DCC MCP Blender, BlenderGPT, bMCP, and MCP-Link declined.

## Themes

Themes are smaller and show the same age-bias in current downloads.

| Half-year | Themes | ≥100 | ≥1k | ≥10k | Top downloads |
|---|---:|---:|---:|---:|---:|
| 2024H1 | 39 | 39 | 39 | 31 | 73,230 |
| 2024H2 | 49 | 49 | 49 | 21 | 44,042 |
| 2025H1 | 26 | 26 | 26 | 8 | 28,267 |
| 2025H2 | 54 | 54 | 54 | 5 | 26,374 |
| 2026H1 | 68 | 68 | 50 | 1 | 12,000 |
| 2026H2 partial | 40 | 36 | 10 | 0 | 2,688 |

## GitHub topic baseline

Repos tagged `blender-addon` or `blender-addons` on GitHub also show supply growth, but current stars do not show a proportional rise in hits.

| Cohort | Repos created | ≥10 stars now | ≥100 stars now |
|---|---:|---:|---:|
| 2021H1 | 92 | 39 | 9 |
| 2021H2 | 96 | 30 | 7 |
| 2022H1 | 127 | 50 | 11 |
| 2022H2 | 105 | 36 | 10 |
| 2023H1 | 105 | 35 | 8 |
| 2023H2 | 98 | 26 | 6 |
| 2024H1 | 92 | 29 | 1 |
| 2024H2 | 116 | 36 | 8 |
| 2025H1 | 123 | 30 | 7 |
| 2025H2 | 136 | 12 | 1 |
| 2026H1 | 262 | 36 | 1 |
| 2026H2 partial | 401 | 22 | 4 |

## Confounders

- **Launch/migration wave.** Blender Extensions became the official in-Blender platform with Blender 4.2 LTS. The 2024Q1/Q2 dates in version history include platform pre-launch/backfill entries; many high-download add-ons are formerly bundled or long-standing community tools.
- **Registry review backlog.** The approval queue is large. Current open items are 22 awaiting review and 387 awaiting changes; awaiting-review median visible age is about 2 days, but awaiting-changes median is about 1 year. Queue result counts rose strongly in Wayback samples, so supply may be constrained/delayed by review and maintainer changes.
- **Current-download age bias.** Older add-ons have had more time and more Blender release cycles to accumulate downloads. Recent cohorts that already exceed thresholds are meaningful; recent cohorts with fewer high-download items may simply be too young.
- **Blender release/user growth.** Blender 4.2, 4.5, and 5.0 release cycles and general Blender user growth can raise downloads independent of AI-assisted development.
- **External markets.** Paid/closed-source Blender add-ons often live on Superhive (formerly Blender Market), Gumroad, or vendor sites, not on the GPL-only official platform. This analysis misses those.
- **Survivorship/removals.** The API covers currently listed extensions. Removed items are absent except when visible in queue history or Wayback.

## Three-sentence verdict

Blender Extensions shows **more supply** in the AI-agent era, especially after separating the 2024 migration wave: add-on listings rise from 152 in 2025H1 to 250 in 2026H1, and GitHub-linked genuinely new projects rise from 40 in 2025Q2 to 91 in 2026Q2 and 123 in 2026Q3. It also shows **more modestly used new tools**: 2026H1 already has 196 add-ons over 1k downloads, and 2026Q3 has 71 over 1k despite a median age of only 60 days. It does **not** show more big hits: high-download counts are flat/down after the migration wave, and the largest recent successes are mostly old/migrated Blender tools rather than new AI-era projects or AI/agent add-ons.
