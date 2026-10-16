# Usage cohorts: count only what people use

Generated on 2026-10-15. Data CSVs are in `data/`; reproducible collection code is in `scripts/collect_usage_cohorts.py`. Large inputs were streamed or held only transiently in the session scratch area, which was deleted after collection; no raw crates dump or cloned Homebrew repository is stored here.

## Three-sentence bottom line

Counting only items with visible usage does not produce a universal 2025–26 boom. The best positive evidence is in developer package managers: Homebrew formulae at equal-ish age and crates.io recent downloads both have more used new items than the 2022–24 trend, although Homebrew is already curated and crates downloads are heavily bot/CI-inflated. VS Code Marketplace shows the opposite pattern: new extension supply explodes, but the absolute count clearing 10k installs is below trend, so the AI-era surge is mostly not turning into widely installed extensions yet.

## At-a-glance trend comparison

| ecosystem | metric | 2022-24 avg/q | 2025 avg/q | 2026H1 avg/q | verdict |
|---|---|---|---|---|---|
| Homebrew formulae | equal-age 30d installs ≥1k | 10.7 | 23.2 | 31.0 | above trend (Q2 not mature) |
| Homebrew formulae | equal-age 30d installs ≥10k | 2.6 | 5.0 | 7.0 | above trend, small-N |
| Homebrew casks | current 30d installs ≥1k | 4.2 | 3.5 | 11.0 | 2026 up, age-confounded |
| crates.io | current recent downloads ≥1k | 1,287 | 1,833 | 4,649 | yes, but bots/CI |
| crates.io | total downloads ≥100k | 658 | 446 | 402 | not yet; age-confounded |
| VS Code Marketplace | current installs ≥10k | 157 | 80.8 | 59.5 | no |

## Method

- **Homebrew formulae/casks.** Usage comes from `https://formulae.brew.sh/api/analytics/install/30d.json` and `.../cask-install/30d.json`; creation quarter is the first git commit adding the formula/cask file in `Homebrew/homebrew-core` or `Homebrew/homebrew-cask`, using blobless clones and rename detection so sharding moves do not count as new creations. Equal-age formula counts use Wayback snapshots nearest six months after each cohort closes; this means items are roughly 6–9 months old. Cask Wayback coverage is sparse before late 2025, so cask equal-age rows are mostly blank. Homebrew's inclusion process is itself a quality/notability filter: acceptable formulae/casks must be stable, maintained, and fit documented project rules (`docs.brew.sh/Acceptable-Formulae`, `docs.brew.sh/Acceptable-Casks`).

- **crates.io.** The official `static.crates.io/db-dump.tar.gz` was streamed, reading only `crates.csv`, `crate_downloads.csv`, `versions.csv`, and `version_downloads.csv`. Crates with no non-yanked versions were excluded; I did not apply a stronger name-squatting classifier because doing so reliably requires semantic/project inspection. `crate_downloads` is lifetime downloads; `version_downloads` covered 2026-07-16 through 2026-10-15 here and is treated as current ~90-day usage.

- **VS Code Marketplace.** The public `extensionquery` API was paged by `publishedDate` for `Microsoft.VisualStudio.Code` targets, deduped by extension id, and current install/rating statistics were counted. I found no practical equal-age historical install source.

- **Skipped PyPI/npm.** Equal-age package downloads are possible in principle, but getting unbiased random creation cohorts requires broad registry/change-feed enumeration or a third-party index; doing that cheaply and reproducibly was less feasible than completing the three higher-priority ecosystems.

## Homebrew formulae: equal-age 30-day installs

| cohort | N created | ≥100 | ≥1k | ≥10k | target | snapshot 30d end | days off |
|---|---|---|---|---|---|---|---|
| 2021Q1 | 129 | 39 | 12 | 6 | 2021-10-01 | 2021-09-28 | -3 |
| 2021Q2 | 134 | 48 | 13 | 3 | 2022-01-01 | 2022-01-19 | 18 |
| 2021Q3 | 177 | 57 | 18 | 9 | 2022-04-01 | 2022-05-28 | 57 |
| 2021Q4 | 129 | 47 | 15 | 6 | 2022-07-01 | 2022-05-28 | -34 |
| 2022Q1 | 121 | 36 | 12 | 4 | 2022-10-01 | 2022-09-21 | -10 |
| 2022Q2 | 165 | 34 | 3 | 1 | 2023-01-01 | 2022-12-04 | -28 |
| 2022Q3 | 157 | 6 | 3 | 0 | 2023-04-01 | 2023-03-31 | -1 |
| 2022Q4 | 151 | 28 | 15 | 6 | 2023-07-01 | 2023-06-01 | -30 |
| 2023Q1 | 158 | 46 | 11 | 2 | 2023-10-01 | 2023-10-04 | 3 |
| 2023Q2 | 138 | 37 | 3 | 0 | 2024-01-01 | 2023-12-05 | -27 |
| 2023Q3 | 196 | 89 | 24 | 7 | 2024-04-01 | 2024-02-27 | -34 |
| 2023Q4 | 245 | 43 | 11 | 4 | 2024-07-01 | 2024-07-14 | 13 |
| 2024Q1 | 120 | 40 | 5 | 3 | 2024-10-01 | 2024-10-10 | 9 |
| 2024Q2 | 125 | 34 | 5 | 0 | 2025-01-01 | 2025-01-21 | 20 |
| 2024Q3 | 129 | 40 | 10 | 2 | 2025-04-01 | 2025-03-17 | -15 |
| 2024Q4 | 269 | 75 | 26 | 2 | 2025-07-01 | 2025-07-10 | 9 |
| 2025Q1 | 293 | 68 | 8 | 2 | 2025-10-01 | 2025-09-12 | -19 |
| 2025Q2 | 204 | 25 | 5 | 1 | 2026-01-01 | 2025-12-11 | -20 |
| 2025Q3 | 260 | 75 | 30 | 12 | 2026-04-01 | 2026-04-11 | 10 |
| 2025Q4 | 234 | 91 | 50 | 5 | 2026-07-01 | 2026-06-27 | -4 |
| 2026Q1 | 236 | 85 | 31 | 7 | 2026-10-01 | 2026-08-12 | -50 |
| 2026Q2 | 211 |  |  |  | 2027-01-01 |  |  |

**Verdict:** yes for formulae. The 2022–24 average was 10.7 new formulae per quarter reaching ≥1k installs at equal-ish age; 2025 averaged 23.3 and 2026Q1 had 31 (2026Q2 is not old enough).

## Homebrew casks: current and sparse equal-age 30-day installs

Current 30-day installs, age-confounded:

| cohort | N created | ≥100 | ≥1k | ≥10k |
|---|---|---|---|---|
| 2021Q1 | 153 | 14 | 6 | 0 |
| 2021Q2 | 109 | 9 | 2 | 1 |
| 2021Q3 | 85 | 11 | 5 | 0 |
| 2021Q4 | 124 | 9 | 1 | 0 |
| 2022Q1 | 80 | 9 | 0 | 0 |
| 2022Q2 | 108 | 16 | 5 | 1 |
| 2022Q3 | 88 | 10 | 2 | 0 |
| 2022Q4 | 89 | 13 | 3 | 0 |
| 2023Q1 | 73 | 11 | 3 | 1 |
| 2023Q2 | 130 | 21 | 3 | 0 |
| 2023Q3 | 95 | 17 | 3 | 1 |
| 2023Q4 | 102 | 11 | 1 | 0 |
| 2024Q1 | 82 | 14 | 3 | 0 |
| 2024Q2 | 2579 | 120 | 20 | 3 |
| 2024Q3 | 100 | 11 | 5 | 0 |
| 2024Q4 | 212 | 15 | 2 | 2 |
| 2025Q1 | 167 | 19 | 2 | 0 |
| 2025Q2 | 164 | 10 | 0 | 0 |
| 2025Q3 | 161 | 20 | 5 | 1 |
| 2025Q4 | 168 | 31 | 7 | 2 |
| 2026Q1 | 160 | 33 | 9 | 1 |
| 2026Q2 | 215 | 55 | 13 | 0 |

Equal-age rows where Wayback had a snapshot; blank threshold cells mean no snapshot was found:

| cohort | N created | ≥100 | ≥1k | ≥10k | target | snapshot 30d end | days off |
|---|---|---|---|---|---|---|---|
| 2021Q1 | 153 |  |  |  | 2021-10-01 |  |  |
| 2021Q2 | 109 |  |  |  | 2022-01-01 |  |  |
| 2021Q3 | 85 |  |  |  | 2022-04-01 |  |  |
| 2021Q4 | 124 |  |  |  | 2022-07-01 |  |  |
| 2022Q1 | 80 |  |  |  | 2022-10-01 |  |  |
| 2022Q2 | 108 |  |  |  | 2023-01-01 |  |  |
| 2022Q3 | 88 |  |  |  | 2023-04-01 |  |  |
| 2022Q4 | 89 |  |  |  | 2023-07-01 |  |  |
| 2023Q1 | 73 |  |  |  | 2023-10-01 |  |  |
| 2023Q2 | 130 |  |  |  | 2024-01-01 |  |  |
| 2023Q3 | 95 |  |  |  | 2024-04-01 |  |  |
| 2023Q4 | 102 |  |  |  | 2024-07-01 |  |  |
| 2024Q1 | 82 |  |  |  | 2024-10-01 |  |  |
| 2024Q2 | 2579 |  |  |  | 2025-01-01 |  |  |
| 2024Q3 | 100 |  |  |  | 2025-04-01 |  |  |
| 2024Q4 | 212 |  |  |  | 2025-07-01 |  |  |
| 2025Q1 | 167 | 24 | 2 | 0 | 2025-10-01 | 2025-11-26 | 56 |
| 2025Q2 | 164 | 9 | 1 | 0 | 2026-01-01 | 2025-12-08 | -24 |
| 2025Q3 | 161 |  |  |  | 2026-04-01 |  |  |
| 2025Q4 | 168 | 37 | 7 | 3 | 2026-07-01 | 2026-06-27 | -4 |
| 2026Q1 | 160 |  |  |  | 2026-10-01 |  |  |
| 2026Q2 | 215 |  |  |  | 2027-01-01 |  |  |

**Verdict:** weak yes only in current data. Casks with ≥1k current 30-day installs average 11.0 per quarter in 2026H1 versus 4.2 in 2022–24, but cask snapshots are too sparse for a clean equal-age test and 2024Q2 is distorted by a mass Google Fonts addition.

## crates.io: lifetime and current recent downloads

| cohort | N created | lifetime ≥1k | lifetime ≥10k | lifetime ≥100k | recent ≥100 | recent ≥1k | recent ≥10k |
|---|---|---|---|---|---|---|---|
| 2021Q1 | 4882 | 4882 | 2072 | 664 | 2005 | 1094 | 622 |
| 2021Q2 | 4951 | 4951 | 2189 | 847 | 2062 | 1111 | 662 |
| 2021Q3 | 4333 | 4333 | 1667 | 511 | 1604 | 852 | 488 |
| 2021Q4 | 4850 | 4850 | 2011 | 673 | 1893 | 971 | 619 |
| 2022Q1 | 5753 | 5753 | 2310 | 650 | 2016 | 1034 | 624 |
| 2022Q2 | 5754 | 5754 | 2041 | 595 | 1936 | 966 | 578 |
| 2022Q3 | 5906 | 5906 | 2284 | 672 | 2155 | 1135 | 626 |
| 2022Q4 | 6613 | 6613 | 2374 | 738 | 2247 | 1188 | 755 |
| 2023Q1 | 8173 | 8173 | 3156 | 852 | 3147 | 1629 | 873 |
| 2023Q2 | 7892 | 7892 | 2660 | 661 | 2695 | 1253 | 695 |
| 2023Q3 | 7439 | 7439 | 2532 | 657 | 2652 | 1233 | 696 |
| 2023Q4 | 7642 | 7642 | 2724 | 686 | 2689 | 1339 | 747 |
| 2024Q1 | 8658 | 8658 | 3038 | 628 | 3229 | 1397 | 747 |
| 2024Q2 | 7820 | 7820 | 2326 | 505 | 2773 | 1301 | 616 |
| 2024Q3 | 9016 | 9016 | 2867 | 688 | 3512 | 1479 | 829 |
| 2024Q4 | 9093 | 8271 | 2192 | 568 | 3343 | 1494 | 739 |
| 2025Q1 | 10033 | 7859 | 1873 | 473 | 3746 | 1594 | 727 |
| 2025Q2 | 10840 | 7888 | 1551 | 377 | 3961 | 1636 | 660 |
| 2025Q3 | 11654 | 6593 | 1220 | 384 | 4149 | 1592 | 717 |
| 2025Q4 | 16575 | 5194 | 1544 | 552 | 6496 | 2511 | 1099 |
| 2026Q1 | 32249 | 6822 | 1877 | 477 | 13119 | 3992 | 1308 |
| 2026Q2 | 44996 | 7905 | 1652 | 326 | 20475 | 5306 | 1390 |

**Verdict:** yes for current usage, no for high lifetime thresholds yet. Recent ≥1k-download crates jump from a 2022–24 average of 1,287 per quarter to 4,649 in 2026H1, but lifetime ≥100k-download crates are below trend because young crates have had little time to accumulate downloads; bot/CI traffic is a major confounder.

## VS Code Marketplace: current installs

| cohort | N published | ≥1k installs | ≥10k installs | ≥100k installs | ≥10 ratings |
|---|---|---|---|---|---|
| 2021Q1 | 2264 | 1063 | 318 | 60 | 66 |
| 2021Q2 | 2657 | 1105 | 289 | 49 | 54 |
| 2021Q3 | 2615 | 1028 | 302 | 60 | 51 |
| 2021Q4 | 2431 | 899 | 222 | 41 | 45 |
| 2022Q1 | 17393 | 951 | 244 | 35 | 45 |
| 2022Q2 | 13175 | 899 | 213 | 32 | 30 |
| 2022Q3 | 2788 | 869 | 181 | 44 | 39 |
| 2022Q4 | 2696 | 790 | 171 | 38 | 38 |
| 2023Q1 | 3173 | 970 | 219 | 38 | 49 |
| 2023Q2 | 3274 | 868 | 170 | 29 | 41 |
| 2023Q3 | 3102 | 729 | 164 | 28 | 35 |
| 2023Q4 | 3063 | 678 | 122 | 17 | 26 |
| 2024Q1 | 3323 | 691 | 113 | 14 | 30 |
| 2024Q2 | 3101 | 554 | 103 | 10 | 20 |
| 2024Q3 | 3639 | 561 | 91 | 15 | 16 |
| 2024Q4 | 3755 | 534 | 91 | 17 | 24 |
| 2025Q1 | 4770 | 640 | 97 | 25 | 19 |
| 2025Q2 | 5284 | 571 | 89 | 34 | 26 |
| 2025Q3 | 5555 | 525 | 72 | 8 | 18 |
| 2025Q4 | 6424 | 465 | 65 | 15 | 16 |
| 2026Q1 | 10090 | 645 | 77 | 6 | 16 |
| 2026Q2 | 11362 | 346 | 42 | 7 | 16 |

**Verdict:** no. Published extensions rose sharply in 2025–26, but ≥10k-install extensions fell from a 2022–24 average of 157 per quarter to 81 in 2025 and 60 in 2026H1; this is age-confounded but still a poor sign for broad adoption.

## Confounders and caveats

- **Age:** Current install/download counts favor old cohorts; equal-age was only practical for Homebrew formulae via Wayback.

- **Bots/CI:** crates.io download counts include automated builds, dependency resolution, mirrors, and CI, so they are usage-ish rather than human adoption.

- **Curated gates:** Homebrew formulae/casks already pass notability/maintainership rules, so their creation counts are not raw software supply.

- **Marketplace noise:** VS Code has spam/import waves (notably 2022Q1–Q2) and extensions can be installed by automation; ratings are included as a second, stricter but much lower-volume signal.

- **Historical gaps:** Wayback did not have enough cask analytics snapshots for 2021–24 or several 2025–26 targets; blank cells are unknown, not zero.
