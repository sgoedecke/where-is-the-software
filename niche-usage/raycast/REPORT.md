# Raycast Store usage cohorts (2026-10-15)

## Source and method

- **Listing date / supply.** I cloned `github.com/raycast/extensions` bloblessly into `cache/extensions-repo` and treated the first git add of `extensions/<slug>/package.json` as the first-listed date. Source: <https://github.com/raycast/extensions>. Script/data: `scripts/analyze.py`, `data/extension_first_listed_git.csv`.
- **Current usage.** I scraped all 343 Raycast Store pages from <https://www.raycast.com/store> and parsed the server-rendered extension objects containing `download_count`. This yielded 3,271 currently active store extensions; 3,252 joined to git first-listed paths, with 19 current-store path mismatches and 196 git-listed paths no longer active. Script/data: `scripts/scrape_store.py`, `data/store_extensions_current.csv`.
- **Usage thresholds.** I used current downloads only: low = **≥1k**, modest = **≥10k**, high = **≥100k**. In the active store snapshot these are roughly the 75th, 95th and 99th percentiles, respectively (median 223; p75 1,154; p95 15,157; p99 98,974).
- **Equal-age caveat.** I could not get complete equal-age downloads. A Wayback CDX probe found Store snapshots but extension-page CDX calls timed out and Store snapshots are not complete per-item cohort history. Therefore all usage counts below favor older cohorts; a recent cohort beating old ones would be strong evidence, but trailing old cohorts is weak evidence.
- **Review queue / submissions.** I counted GitHub PRs with `label:"new extension"` by created and merged quarter using `gh api search/issues`; current open backlog is from `state:open`. Data: `data/new_extension_prs_by_quarter.csv`.

## Cohort table

Supply is all package first-adds in git. Usage counts are current downloads for extensions still active in the Store.

| Cohort | Supply | Active w/downloads | Median current downloads | ≥1k | ≥10k | ≥100k | AI-related active |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021H2 | 155 | 147 | 7,934 | 124 | 65 | 14 | 31 |
| 2022H1 | 315 | 287 | 1,672 | 177 | 51 | 7 | 25 |
| 2022H2 | 271 | 251 | 782 | 113 | 31 | 5 | 22 |
| 2023H1 | 323 | 301 | 641 | 125 | 22 | 2 | 28 |
| 2023H2 | 215 | 201 | 558 | 62 | 13 | 1 | 17 |
| 2024H1 | 323 | 302 | 337 | 76 | 12 | 0 | 38 |
| 2024H2 | 253 | 235 | 255 | 51 | 7 | 0 | 26 |
| 2025H1 | 342 | 329 | 223 | 71 | 9 | 0 | 65 |
| 2025H2 | 307 | 297 | 120 | 35 | 1 | 0 | 46 |
| 2026H1 | 550 | 523 | 58 | 29 | 1 | 0 | 104 |
| 2026H2* | 394 | 379 | 13 | 0 | 0 | 0 | 86 |

`*` 2026H2 is partial through 2026-10-15.

Quarterly data is in `data/cohorts_quarter.csv`. Annual supply from git first-adds was 576 in 2024, 649 in 2025, and 944 in 2026 YTD (annualizing 2026 YTD gives roughly 1.2k, about 2.1× 2024). Active AI-related extensions listed per year rose from 64 in 2024 to 111 in 2025 and 190 in 2026 YTD.

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
- **Current-download age bias.** Older cohorts have had years to accumulate downloads. The absence of 2025–26 high-download hits is therefore meaningful only at the high end; low/modest thresholds for 2026 especially are too early to judge.

## Three-sentence verdict

Raycast clearly shows **more supply**: git first-adds rose from 576 in 2024 to 649 in 2025 and 944 in 2026 YTD, while `new extension` PR submissions jumped from roughly 260-300/quarter in 2024 to 470-620/quarter in 2025 and 780-990/quarter in early 2026. It does **not yet show more modestly used non-AI new tools** on current downloads: 2025 has fewer ≥1k and ≥10k extensions than 2024 despite more supply, though current-download age bias makes this conservative against recent cohorts. It shows **no new big hits** by the ≥100k threshold after 2023; the recent top list is instead dominated by AI/agent tooling and wrappers/official integrations rather than many brand-new standalone projects.
