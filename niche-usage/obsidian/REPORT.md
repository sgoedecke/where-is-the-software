# Obsidian community plugins: usage cohorts

Source: blobless clone of `obsidianmd/obsidian-releases` (`obsidian-releases/`), which holds `community-plugins.json` and the daily `community-plugin-stats.json` download counts (GitHub release-asset downloads, including updates). Snapshot head: 2026-10-15; 8,970 plugins.

The first-pass agent wrote `analyze_obsidian_monthly.py` (6-month outcomes; `results/monthly_summary.csv`, `results/plugin_6mo_downloads.csv`). It could not read the shared method prompt and did not produce cohort comparisons, so the main analysis below was done afterwards with `scripts/equal_age_60d.py`.

## Policy break: 2026-05-15

Commit `afc12102` (2026-05-15, "Remove submission instructions in favor of new system") replaced PR-based manual review. Afterwards an "Obsidian Bot" mirrors listings, which are tagged "This plugin has not been manually reviewed". Plugin count: 2,750 (2026-04-30) → 8,970 (2026-10-15); themes 415 → 882. The repo's PRs are no longer visible (issues disabled; PR search returns 0), so submission-time supply can't be measured.

Listings fell to 60–140 a quarter in 2025Q3–2026Q1, against ~180–240 before. That points to a growing review backlog, which was then released in May.

## Equal-age outcome: downloads gained in the first 60 days after first appearing in stats

Weekly snapshots; gain = downloads at ~day 60 minus downloads at first appearance. This excludes pre-listing downloads via BRAT/GitHub. `results/plugin_60d_downloads.csv`, `results/cohort_60d_quarterly.csv`.

| Quarter listed | n | gain ≥100 | ≥1k | ≥3k | ≥10k | ≥30k |
|---|---:|---:|---:|---:|---:|---:|
| 2023 avg/qtr | 166 | 160 | 63 | 10 | 1 | 0 |
| 2024 avg/qtr | 191 | 172 | 47 | 7 | 1 | 0 |
| 2025Q1 | 243 | 209 | 35 | 10 | 0 | 0 |
| 2025Q2 | 193 | 169 | 24 | 5 | 0 | 0 |
| 2025Q3 | 137 | 116 | 32 | 8 | 3 | 2 |
| 2025Q4 | 80 | 72 | 15 | 4 | 3 | 1 |
| 2026Q1 | 62 | 56 | 21 | 8 | 3 | 1 |
| **2026Q2** | 2,607 | 2,098 | 324 | 102 | 23 | 4 |
| **2026Q3*** | 1,651 | 1,183 | 221 | 35 | 8 | 2 |

\*Only plugins listed through about mid-August are old enough to have 60-day data.

Ecosystem download growth: monthly increments were about 2.7–3.2M through 2025, rising to 5–6M in Apr–Jun 2026 and about 10M in Aug–Sep 2026 (about 3.3×). Part of this is the new plugins themselves; Claudian alone gained 0.85M in 60 days. Scaling thresholds by 3× (old ≥1k ≈ new ≥3k):
- About 4–14 plugins a quarter cleared the bar before.
- 102 cleared it in 2026Q2 and 35 in the partial 2026Q3.
- That is roughly 5–10× more.

## Backlog check: repo creation dates of plugins gaining ≥1k in 60 days (`results/hits_1k_60d_repo_created.csv`)

- 2026Q2 (313 hits): 225 repos created in 2026H1, 67 in 2025H2, 21 earlier.
- 2026Q3 (218 hits): 162 created in 2026H2, 41 in 2026H1, 15 earlier.

So the surge is mostly genuinely new 2026 projects, not old plugins that were stuck in review.

## Top new plugins (60-day gain)

Claudian (Claude Code/Codex in Obsidian, 847k), a Chinese-language plugin-search tool (56k), draw.io (45k), Agent Client (44k), Hearth dashboard (31k), project management/Gantt (31k), a Claude Code sidebar (29k), block drag-and-drop (28k), semantic search (23k), terminal (23k), WeSight (Claude Code/Codex/OpenCode, 22k), sync engine, Snipd sync, LLM-wiki, Excalidraw extras, family tree/GEDCOM, task/calendar/dashboard tools, an MCP connector.

AI/agent integrations dominate the very top. Below them is a broad tail of non-AI productivity tools.

## Verdict

This is the strongest case in the niche round for "more new small tools that people actually use". About 5–10× more plugins clear modest usage bars at equal age, even after scaling for ecosystem growth. A few more clear high bars, mostly AI-agent integrations.

**Confounders:**
1. The end of manual review removed a gatekeeping step, so tools that would previously have stayed on GitHub/BRAT now get listed and discovered. Some of the jump is a listing effect rather than more software being built.
2. Downloads include update downloads, and AI-assisted plugins may release often.
3. Obsidian's own user base appears to be growing fast in 2026, judging by ecosystem download growth, which plausibly has an AI cause (Claude Code + Obsidian "second brain" workflows).

We can't separate (1) from an AI-driven supply increase, because pre-May submission volume is not observable.
