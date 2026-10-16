# Flathub usage cohort analysis (2026-10-15)

## Source and method

Sources used:

- `POST https://flathub.org/api/v2/search` for the app catalogue (`added_at`, `installs_last_month`, verification metadata). It returned 3,334 current apps: 3,318 `desktop-application` and 16 `console-application` records. The search endpoint did not return runtimes/extensions/BaseApps; the script still excludes `*.Debug`, `*.Locale`, `*.Sources`, `*.BaseApp`, SDK and Platform IDs.
- `https://flathub.org/api/v2/stats/<app-id>` for current `installs_total` and a validation sample of daily `installs_per_day`.
- `https://flathub.org/stats/YYYY/MM/DD.json` for historical daily stats from 2021-01-01 through 2026-10-14. For each app/day I count **new installs** as `sum_arch(downloads - updates)` from `refs[app_id]`, not the second element alone. I validated this against the app stats endpoint for Firefox, Jan, LM Studio and Sober; last-10-day values matched exactly.
- `gh` search/API for `repo:flathub/flathub is:pr base:new-pr` submission PR counts.
- `https://flathub.org/api/v2/appstream/<app-id>` and GitHub repo metadata for the top recent-item/backlog check.

Files written:

- `scripts/collect_flathub.py`, `scripts/add_platform_scaled.py`, `scripts/enrich_top_recent.py`, `scripts/collect_pr_counts.sh`
- `data/apps.csv`, `data/apps_with_equal_age.csv`, `data/apps_with_equal_age_scaled.csv`, `data/daily_new_installs.csv`, `data/ecosystem_daily.csv`, `data/cohort_summary.csv`, `data/cohort_summary_scaled.csv`, `data/top_recent_enriched.csv`, `data/pr_counts_quarterly.csv`, `data/open_new_prs.tsv`
- raw API caches under `cache/`

Limitations:

- This is a current-catalogue study, so apps removed from Flathub are missing (survivorship bias).
- Historical daily JSONs are available from 2021 onward in this run; equal-age usage is blank for 2017-2020 cohorts, though their supply/current usage is in the CSVs.
- 2026-H2 is incomplete, and only apps listed by 2026-07-16 have a full 90-day window; none have a full 180-day window as of 2026-10-15.
- Flathub listings often package old upstream projects. A Flathub `added_at` date is a registry-listing date, not a project-birth date.
- Seven current app IDs returned 404 from the per-app stats endpoint; their current `installs_total` is blank/zero in threshold counts, but search and historical daily rows remain included where available.

Thresholds used below: low/modest/high = at least 100 / 1,000 / 10,000 new installs in the first 90 or 180 days after listing. Current momentum columns use last-month installs.

## Cohort table

| cohort | supply | 90d observed | 90d >=100/>=1k/>=10k | 180d observed | 180d >=100/>=1k/>=10k | 180d >=1k per 100M ecosystem installs | current last-month >=1k/>=10k |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021-H1 | 158 | 158 | 148/38/3 | 158 | 153/76/8 | 142 | 49/7 |
| 2021-H2 | 118 | 118 | 115/34/2 | 118 | 116/63/11 | 109 | 38/8 |
| 2022-H1 | 268 | 268 | 259/122/14 | 268 | 266/186/43 | 218 | 88/9 |
| 2022-H2 | 178 | 178 | 177/91/12 | 178 | 178/133/28 | 118 | 45/9 |
| 2023-H1 | 242 | 242 | 242/142/21 | 242 | 242/189/42 | 157 | 57/13 |
| 2023-H2 | 245 | 245 | 245/121/17 | 245 | 245/188/27 | 124 | 44/10 |
| 2024-H1 | 221 | 221 | 221/140/15 | 221 | 221/182/37 | 143 | 58/6 |
| 2024-H2 | 250 | 250 | 250/156/14 | 250 | 250/199/38 | 153 | 68/4 |
| 2025-H1 | 214 | 214 | 214/119/16 | 214 | 214/177/29 | 116 | 46/6 |
| 2025-H2 | 201 | 201 | 200/125/25 | 201 | 201/158/41 | 107 | 51/4 |
| 2026-H1 | 308 | 308 | 307/216/25 | 191 | 191/163/35 | 120 | 78/6 |
| 2026-H2* | 145 | 22 | 22/12/2 | 0 | 0/0/0 | n/a | 39/1 |

\* 2026-H2 is partial through 2026-10-15.

Notes:

- Supply rose sharply in 2026-H1 (308 listings), after 2025-H1/H2 were not above the 2023-2024 range. The partial 2026-H2 count (145 by mid-October) is also running high.
- Fixed-threshold early usage improved in 2026-H1: 216 apps reached 1,000 installs in 90 days, versus 119 in 2025-H1 and 125 in 2025-H2.
- Platform growth is large. Daily ecosystem new installs summed by half-year grew from 20.9M in 2021-H1 to 190.7M in 2025-H1 and 243.9M in 2026-H1. When normalizing first-180-day app installs per 100M ecosystem installs, 2026-H1 is similar to 2025, not a step change.
- High-usage hits did not obviously increase: 2026-H1 has 25 apps over 10k installs in 90 days, tied with 2025-H2; current last-month >=10k counts are 6 for 2026-H1, 6 for 2025-H1, and 4 for 2025-H2.

## Submission/review capacity check

`base:new-pr` submissions on `flathub/flathub` appear to be closed after processing rather than normally merged; `merged:` search returns almost all zero, so I use opened vs closed and open backlog.

| half | opened | closed | still open from that half |
|---|---:|---:|---:|
| 2021-H1 | 311 | 330 | 0 |
| 2021-H2 | 239 | 235 | 0 |
| 2022-H1 | 459 | 423 | 0 |
| 2022-H2 | 338 | 322 | 0 |
| 2023-H1 | 361 | 380 | 0 |
| 2023-H2 | 338 | 318 | 0 |
| 2024-H1 | 333 | 305 | 0 |
| 2024-H2 | 389 | 379 | 0 |
| 2025-H1 | 414 | 474 | 1 |
| 2025-H2 | 486 | 468 | 6 |
| 2026-H1 | 1,211 | 1,238 | 24 |
| 2026-H2* | 1,173 | 766 | 44 |

There is a real submission surge in 2026, far larger than the accepted-listing surge. The current open `new-pr` backlog was 75 PRs; most were recent, but the oldest open submission was from 2025-02-09. Review capacity may now be a constraint, especially in 2026-H2, but it does not by itself explain the 2026-H1 usage pattern because many Q1/Q2 submissions were closed.

## Top recent items and AI/backlog check

Top recent = apps listed since 2025-01-01, ranked by `installs_last_month`.

| rank | app | added | last-month installs | AI-related? | project-age check |
|---:|---|---:|---:|---|---|
| 1 | Sober (`org.vinegarhq.Sober`) | 2025-03-30 | 193,490 | no | upstream GitHub 2024-08; new-ish project, verified |
| 2 | Zen Browser | 2025-01-14 | 58,393 | no | upstream GitHub 2024-03; new-ish browser, verified |
| 3 | Bazaar | 2025-08-26 | 45,417 | no | Flathub/app-store utility, verified |
| 4 | Thunderbird | 2026-05-19 | 29,389 | no | old Mozilla project newly listed, verified |
| 5 | Thunderbird ESR | 2026-05-26 | 28,115 | no | old Mozilla project newly listed, verified |
| 6 | Jellyfin Desktop | 2025-12-27 | 26,061 | no | upstream GitHub 2021; existing project, verified |
| 7 | OrcaSlicer | 2026-03-30 | 24,085 | no | upstream GitHub 2022; existing project, verified |
| 8 | LACT | 2025-04-10 | 19,855 | no | upstream GitHub 2020; existing project, verified |
| 9 | Faugus | 2025-06-14 | 19,296 | no | upstream GitHub 2024-06; roughly 1 year older, verified |
| 10 | Opera GX | 2026-04-12 | 17,447 | no/AI features only | old proprietary browser newly listed, verified |
| 11 | VacuumTube | 2025-03-25 | 15,693 | no | upstream GitHub 2024-03; roughly 1 year older, verified |
| 12 | Mocktail | 2026-08-14 | 13,327 | no | upstream GitHub 2026-08; genuinely new, verified |
| 13 | ClamUI | 2026-01-13 | 13,064 | no | UI repo 2025-12; wraps old ClamAV domain, verified |
| 14 | Collabora Office | 2025-12-11 | 12,770 | no | old office suite/new listing, verified |
| 15 | LM Studio | 2026-05-15 | 12,676 | **yes** | local AI model runner; not verified in search metadata |
| 23 | Jan | 2025-11-25 | 8,550 | **yes** | upstream GitHub 2023; AI assistant, verified |
| 31 | OpenCode | 2026-04-23 | 6,736 | **yes, agent tooling** | upstream GitHub 2025; AI coding agent |

Top-50 checks:

- 44/50 of the top recent apps are Flathub-verified, which is a useful but imperfect proxy for first-party/upstream involvement.
- Of the 36 top-50 apps with a non-Flathub GitHub upstream repo detected, 18 repos were already more than a year old at Flathub listing time and 18 were <=1 year old. So repackaging of existing software is a major confounder even among 2025-2026 hits.
- Only three clear AI-related apps appear in the top 50: LM Studio, Jan and OpenCode. Only OpenCode is agent/coding tooling.
- The largest recent hits are mostly gaming/Roblox, browsers, app discovery, emulators, media and utility apps rather than AI-native desktop software.

## Confounders

- **Platform growth:** ecosystem daily new installs grew roughly 9-12x from 2021 to 2025/2026. Fixed thresholds therefore overstate recent cohorts unless normalized.
- **Old apps newly listed:** Thunderbird, Opera GX, Collabora Office, Jellyfin, OrcaSlicer, LACT, Luanti, Sublime Text and others are established upstream projects. Their Flathub listing date is not software creation date.
- **Verification/upstream ownership:** many top recent items are verified, but verification is not the same thing as “new first-party app created in this cohort.”
- **Submission surge/review bottleneck:** 2026 PR submissions to `new-pr` exploded (1,211 in H1; 1,173 by mid-H2) while accepted current listings grew much less. Current backlog is visible but not enormous in count (75 open), though some old PRs remain.
- **Survivorship:** current API results omit removed apps and may undercount failed/abandoned supply.
- **Stats semantics:** historical `refs` values are `[downloads, updates]`; counting new installs requires `downloads - updates`. The top-level `delta_downloads` field is not the app-level new-install count used by the public per-app stats endpoint.

## Three-sentence verdict

Supply: **yes, but late** — 2026-H1 and partial 2026-H2 show a clear listing/submission surge, while 2025 cohorts do not exceed the 2023-2024 range. Modestly used new tools: **yes on fixed equal-age thresholds, weak after platform-growth normalization** — 2026-H1 has many more apps reaching 1k installs in 90 days, but normalized first-180-day usage is roughly in line with 2025. Big hits: **no broad increase** — high-threshold counts are flat, and the few AI-related recent hits are LM Studio, Jan and OpenCode rather than a large wave of AI-era desktop apps.
