# Raycast Store usage cohorts (2026-10-15)

Threshold revision: 2026-10-17; the underlying 2026-10-15 snapshot is unchanged.

## Source and method

- **Listing date / supply.** I cloned `github.com/raycast/extensions` bloblessly into `cache/extensions-repo` and treated the first git add of `extensions/<slug>/package.json` as the first-listed date. Source: <https://github.com/raycast/extensions>. Script/data: `scripts/analyze.py`, `data/extension_first_listed_git.csv`.
- **Current usage.** I scraped all 343 Raycast Store pages from <https://www.raycast.com/store> and parsed the server-rendered extension objects containing `download_count`. This yielded 3,271 currently active store extensions; 3,252 joined to git first-listed paths, with 19 current-store path mismatches and 196 git-listed paths no longer active. Script/data: `scripts/scrape_store.py`, `data/store_extensions_current.csv`.
- **Usage thresholds.** Modest usage is now **≥100 current cumulative downloads**, selected to address small-audience software; high remains **≥100k**. The previous ≥10k "modest" bar was near the 95th percentile (93% of active extensions have fewer than 10k downloads; p95 is 15,157), so it poorly represented modest use. The ≥1k and ≥10k counts remain secondary measures with their original meanings, not relabeled counts (median 223; p75 1,154; p99 98,974). Downloads are not a count of distinct users.
- **Equal-age caveat.** I could not get complete equal-age downloads. A Wayback CDX probe found Store snapshots but extension-page CDX calls timed out and Store snapshots are not complete per-item cohort history. Therefore all usage counts below favor older cohorts; a recent cohort beating old ones would be strong evidence, but trailing old cohorts is weak evidence.
- **Review queue / submissions.** I counted GitHub PRs with `label:"new extension"` by created and merged quarter using `gh api search/issues`; current open backlog is from `state:open`. Data: `data/new_extension_prs_by_quarter.csv`.

To reproduce from the checked-in data without re-scraping, run `python3 niche-usage/raycast/scripts/analyze.py` from the repository root. It joins the two source CSVs on `relative_path` and regenerates quarter/half-year cohorts, the top-recent list and `data/summary.json`, including threshold definitions and the comparison/sensitivity results.

## Cohort table

Supply is all package first-adds in git. Usage counts are current downloads for extensions still active in the Store.

| Cohort | Supply | Active w/downloads | Median current downloads | ≥100 (modest) | ≥1k | ≥10k | ≥100k (high) | AI-related active |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021H2 | 155 | 147 | 7,934 | 147 | 124 | 65 | 14 | 31 |
| 2022H1 | 315 | 287 | 1,672 | 268 | 177 | 51 | 7 | 25 |
| 2022H2 | 271 | 251 | 782 | 217 | 113 | 31 | 5 | 22 |
| 2023H1 | 323 | 301 | 641 | 255 | 125 | 22 | 2 | 28 |
| 2023H2 | 215 | 201 | 558 | 168 | 62 | 13 | 1 | 17 |
| 2024H1 | 323 | 302 | 337 | 252 | 76 | 12 | 0 | 38 |
| 2024H2 | 253 | 235 | 255 | 174 | 51 | 7 | 0 | 26 |
| 2025H1 | 342 | 329 | 223 | 232 | 71 | 9 | 0 | 65 |
| 2025H2 | 307 | 297 | 120 | 161 | 35 | 1 | 0 | 46 |
| 2026H1 | 550 | 523 | 58 | 197 | 29 | 1 | 0 | 104 |
| 2026H2* | 394 | 379 | 13 | 22 | 0 | 0 | 0 | 86 |

`*` 2026H2 is partial through 2026-10-15.

Quarterly data is in `data/cohorts_quarter.csv`. Annual supply from git first-adds was 576 in 2024, 649 in 2025, and 944 in 2026 YTD (annualizing 2026 YTD gives roughly 1.2k, about 2.1× 2024). Active AI-related extensions listed per year rose from 64 in 2024 to 111 in 2025 and 190 in 2026 YTD.

## Modest-usage comparison and sensitivity

At **≥100 downloads**, the six complete 2022–24 half-year cohorts average **222.3333 extensions per half-year**, compared with **197 in 2026H1**: **−11.3943%**, rounded to **−11%**. Partial 2026H2 (22 so far) is excluded from the comparison. These counts include both AI-related and non-AI extensions; they are not a non-AI-only series.

Every row below uses that same six-half-year baseline and 2026H1 comparison, changing only the cumulative-download threshold:

| Current downloads | 2022–24 mean per half-year | 2026H1 | Observed change |
|---|---:|---:|---:|
| ≥10 | 262.6667 | 469 | +79% |
| ≥100 (modest) | 222.3333 | 197 | −11% |
| ≥500 | 141.3333 | 47 | −67% |
| ≥1k | 100.6667 | 29 | −71% |
| ≥10k (previous modest bar) | 22.6667 | 1 | −96% |
| ≥100k (high, unchanged) | 2.5 | 0 | −100% |

This is a **snapshot comparison, not an estimate of a true 11% decline** in modestly used new software. Older cohorts have had years to accumulate downloads, while the recent cohort has had months; lowering the threshold does not make those ages comparable. The sensitivity table illustrates how much the description depends on the bar, not a reason to select a bar for a desired result. True growth remains **inconclusive**, and these data cannot establish AI causation.

## Submission / review queue check

`new extension` PR submissions are much higher than merged/listed counts, so opened-minus-merged is not a backlog measure (many are closed/rejected/abandoned). The actual current open queue is **236 PRs**, almost all created in 2026Q3-Q4.

| Quarter | New-extension PRs opened | Merged | Currently open from that quarter | Git first-add supply |
|---|---:|---:|---:|---:|
| 2024Q1 | 297 | 162 | 0 | 162 |
| 2024Q2 | 281 | 159 | 0 | 161 |
| 2024Q3 | 263 | 122 | 0 | 122 |
| 2024Q4 | 277 | 132 | 0 | 131 |
| 2025Q1 | 509 | 179 | 0 | 179 |
| 2025Q2 | 471 | 163 | 0 | 163 |
| 2025Q3 | 500 | 152 | 0 | 143 |
| 2025Q4 | 621 | 164 | 0 | 164 |
| 2026Q1 | 990 | 318 | 0 | 318 |
| 2026Q2 | 780 | 234 | 0 | 232 |
| 2026Q3 | 766 | 307 | 134 | 305 |
| 2026Q4* | 142 | 89 | 102 | 89 |

`*` 2026Q4 is partial through 2026-10-15. The queue is real but recent; review throughput also rose sharply in 2026.

## Top recent items / AI and integration check

Top 30 currently most-downloaded extensions first listed in 2025+:

| Rank | First listed | Extension | Downloads | AI/agent? | Kind / project-newness proxy |
|---:|---|---|---:|---|---|
| 1 | 2025-02-25 | Google Calendar | 72,175 | yes | third-party wrapper for existing app/service |
| 2 | 2025-05-08 | Model Context Protocol Registry | 43,619 | yes | official/company-owned integration (Raycast) |
| 3 | 2025-02-14 | App Cleaner | 37,022 | no | standalone Raycast utility |
| 4 | 2026-03-17 | Mole | 22,116 | yes | AI/agent utility or wrapper |
| 5 | 2025-01-08 | Ghostty | 17,568 | no | third-party wrapper for existing app/service |
| 6 | 2025-04-28 | Dia | 15,246 | yes | official/company-owned integration (The Browser Company) |
| 7 | 2025-06-18 | Claude Usage (ccusage) | 14,319 | yes | AI/agent utility or wrapper |
| 8 | 2025-01-10 | Deepseek Quick Actions | 11,661 | yes | AI/agent utility or wrapper |
| 9 | 2025-08-28 | GitHub Copilot | 11,368 | yes | official/company-owned integration (GitHub) |
| 10 | 2025-02-21 | Siri | 11,063 | yes | third-party wrapper for existing app/service |
| 11 | 2025-03-05 | YouTube Search | 11,010 | no | third-party wrapper for existing app/service |
| 12 | 2026-02-11 | Skills | 9,449 | yes | AI/agent utility or wrapper |
| 13 | 2025-03-13 | Model Context Protocol | 9,068 | yes | AI/agent utility or wrapper |
| 14 | 2025-04-30 | Granola | 8,264 | yes | AI/agent utility or wrapper |
| 15 | 2025-05-21 | Instagram Media Downloader | 7,778 | no | third-party wrapper for existing app/service |
| 16 | 2025-09-12 | Everything | 7,290 | no | third-party wrapper for existing app/service |
| 17 | 2025-09-03 | Cursor Agents | 7,181 | yes | official/company-owned integration (Anysphere) |
| 18 | 2026-01-15 | Font Sniper | 6,729 | no | standalone Raycast utility |
| 19 | 2025-06-25 | Claude Code Cheatsheet | 6,339 | yes | AI/agent utility or wrapper |
| 20 | 2025-03-03 | BetterDisplay | 6,168 | yes | third-party wrapper for existing app/service |
| 21 | 2025-08-04 | Google Lens | 5,769 | no | third-party wrapper for existing app/service |
| 22 | 2025-06-05 | Whisper Dictation | 5,685 | yes | AI/agent utility or wrapper |
| 23 | 2025-02-25 | Firecrawl | 5,669 | yes | official/company-owned integration (Firecrawl) |
| 24 | 2025-08-22 | Comet | 5,115 | yes | AI/agent utility or wrapper |
| 25 | 2025-03-13 | Code Execution | 5,091 | yes | AI/agent utility or wrapper |
| 26 | 2025-04-11 | Obsidian Tasks | 4,618 | no | third-party wrapper for existing app/service |
| 27 | 2025-03-25 | Bartender | 4,592 | yes | third-party wrapper for existing app/service |
| 28 | 2025-03-13 | Memory | 4,456 | yes | AI/agent utility or wrapper |
| 29 | 2025-09-30 | Claude Code Launcher | 4,243 | yes | AI/agent utility or wrapper |
| 30 | 2025-11-20 | Antigravity | 4,117 | yes | AI/agent utility or wrapper |

Among the top 20, 14 are AI/agent-related, 4 are manifest/company-owned integrations, 7 are third-party wrappers around existing apps/services, and only 2 are clearly standalone Raycast utilities. Among the top 50, 36 are AI/agent-related and 6 are manifest/company-owned integrations. I could not reliably use GitHub repository creation dates for “new project” because extension source lives in the Raycast monorepo; the table uses manifest owner fields and product identity as the proxy.

## Confounders and interpretation notes

- **Platform growth.** Raycast says “hundreds of thousands” of people used Raycast daily on Mac before Windows, and the Store has “thousands of extensions” (<https://www.raycast.com/blog/raycast-for-windows>, published Nov. 20, 2025). More users alone can raise download counts for later cohorts; current downloads are not normalized by total Raycast users.
- **Windows launch.** Raycast for Windows entered public beta on Nov. 20, 2025, with “hundreds” of extensions already working on Windows and more being added. This is a major supply and demand shock independent of AI coding; 2026 includes many Windows-compatible new extensions.
- **AI Extensions / Raycast AI.** The Store has an AI category (<https://www.raycast.com/store/category/ai>), many extension objects carry an `AI Extensions` category, and 2025+ top items are dominated by MCP, Claude/Copilot/Cursor, AI browser, and AI-tooling integrations. This can create real “new useful software” in the Store while being specifically AI-agent tooling, the exception category seen in other ecosystems.
- **Review policy / throughput.** I did not verify a written review-policy change. The PR data show submissions roughly doubled in 2025 and rose again in 2026, while merged/listed throughput also rose sharply; the current open queue is 236 PRs and is recent, so review friction is a confounder but not enough to explain all 2026 supply.
- **Survivorship.** Usage counts are for active Store entries only. Git supply includes 3,448 package additions; only 3,252 matched active Store entries with downloads. Removed/rejected extensions can depress true cohort success rates.
- **Current-download age bias.** Older cohorts have had years to accumulate downloads; recent cohorts have had only months. The ≥100 modest bar does not correct this, and neither the −11% snapshot comparison nor the absence of recent ≥100k hits establishes a true decline at equal age.

## Three-sentence verdict

Raycast clearly shows **more supply**: git first-adds rose from 576 in 2024 to 649 in 2025 and 944 in 2026 YTD, while `new extension` PR submissions jumped from roughly 260-300/quarter in 2024 to 470-620/quarter in 2025 and 780-990/quarter in early 2026. At **≥100 current downloads**, modestly used new extensions average 222.33 per half-year in 2022–24 versus 197 in 2026H1 (−11% observed, excluding partial 2026H2), but unequal time to accumulate downloads leaves true growth **inconclusive** and establishes neither a decline nor AI causation. No extensions first listed after 2023 have reached the unchanged **≥100k** high bar in this snapshot, also age-confounded; the recent top list is dominated by AI/agent tooling and wrappers/official integrations rather than many brand-new standalone projects.
