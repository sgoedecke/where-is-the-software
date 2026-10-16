# Steam games usage-cohort analysis

## Source and method

- **Supply source:** Steam store search JSON/HTML (`category1=998`, `sort_by=Released_DESC`, `infinite=1`) crawled on 2026-10-15. I kept release dates from 2021-01-01 through 2026-09-30 and excluded obvious demos/soundtracks/DLC leaks by title. Result: **86,023 game rows**.
- **Usage source:** `store.steampowered.com/appreviewhistogram/<appid>` was verified to return monthly `rollups` with up/down recommendations. I sampled **100 games per release month** (6,900 apps), counted monthly rollups overlapping the first 90 and 365 days after Steam's release date, and scaled threshold counts by month supply. Because the endpoint is monthly, 90-day counts are approximate and can include up to one extra partial month.
- **Thresholds:** low/modest/high = **≥10 / ≥100 / ≥1,000 reviews** in the first 90 days; 365-day counts are included where cohorts are old enough. Reviews are only a sales proxy (Boxleiter ratio roughly 1 review per 30-60 sales, varying by genre, region and F2P).
- **AI disclosure:** for a separate post-policy sample (6,359 apps), I fetched store pages and detected the `AI Generated Content Disclosure` block. This is only meaningful after Steam's Jan 2024 AI disclosure policy.
- **Top-items check:** top recent games were cross-checked with SteamSpy `request=all` current review totals, then the same review-histogram endpoint was used for early reviews.
- **Outputs:** scripts in `scripts/`; raw caches in `cache/`; derived CSVs in `data/` (`steam_supply_apps.csv`, `steam_sample_reviews.csv`, `steam_ai_disclosure_sample.csv`, `cohort_summary.csv`, `top_recent_by_90d_reviews.csv`).

## Cohort table

Estimated counts clearing review thresholds at equal age. 90-day counts are complete through 2026H1; 2026H2 is partial/July-heavy. 365-day counts are complete through 2025H1.

| Cohort | Supply | ≥10 rev 90d | ≥100 rev 90d | ≥1k rev 90d | ≥100 rev 365d | AI disclosure share |
|---|---:|---:|---:|---:|---:|---:|
| 2021H1 | 4,383 | 1,982 | 519 | 168 | 655 | — |
| 2021H2 | 4,996 | 2,027 | 504 | 67 | 596 | — |
| 2022H1 | 4,748 | 2,276 | 579 | 154 | 768 | — |
| 2022H2 | 5,367 | 2,393 | 769 | 174 | 952 | — |
| 2023H1 | 5,616 | 2,525 | 686 | 139 | 861 | — |
| 2023H2 | 6,254 | 2,423 | 686 | 115 | 803 | — |
| 2024H1 | 7,299 | 3,139 | 852 | 183 | 1,120 | 7.9% |
| 2024H2 | 8,796 | 3,954 | 1,161 | 240 | 1,423 | 13.3% |
| 2025H1 | 8,789 | 3,410 | 1,059 | 273 | 1,275 | 15.8% |
| 2025H2 | 10,070 | 4,583 | 1,425 | 378 | partial | 21.1% |
| 2026H1 | 11,354 | 4,909 | 1,382 | 342 | — | 28.9% |
| 2026H2* | 8,351 | 788* | 232* | 93* | — | 41.6% |

Supply roughly **2.6x'd** from 2021H1 to 2026H1. The estimated count of new games reaching **≥100 reviews in their first 90 days** also rose about **2.7x** (519 → 1,382), but the share is nearly flat (about 12%). The estimated count reaching **≥1,000 early reviews** rose in absolute terms but stayed in a narrow ~2-4% band; after Steam peak concurrency rose from ~27M in 2021 to 40M+ in 2025-26, fixed review thresholds overstate recent cohorts.

AI disclosures are a major supply driver: from 2024H1 to 2026H1, estimated AI-disclosed launches rose from ~574 to ~3,285, explaining about two-thirds of the net supply increase in this sample. Cross-check: the Q1 supply growth in this crawl (3,517 in 2024Q1 → 5,282 in 2026Q1, +50%) is close to Chris Zukowski's published Q1 2024 → Q1 2026 low-review-growth figure (+48% for ≤50 reviews), while his 1,000+ review count (88 → 96) is more conservative than this sampled/monthly estimate and reinforces caution on big-hit growth.

## Top recent items check

Approximate first-90-day reviews among high-current-review 2025-26 releases:

| Game | Release date used | 90d reviews | Check |
|---|---:|---:|---|
| Schedule I | 2025-03-24 | 200k | New small/indie studio (TVGS), original surprise hit. |
| R.E.P.O. | 2025-02-26 | 153k | Small studio co-op horror, original. |
| Monster Hunter Wilds | 2025-02-27 | 136k | Capcom AAA franchise sequel. |
| Clair Obscur: Expedition 33 | 2025-04-24 | 103k | New IP, AA/established publisher. |
| ELDEN RING NIGHTREIGN | 2025-05-29 | 101k | FromSoftware franchise spinoff. |
| Kingdom Come: Deliverance II | 2025-02-04 | 77k | Sequel from established studio. |
| Grand Theft Auto V Enhanced | 2025-03-04 | 64k | Re-release of old AAA hit. |
| Palworld | 2026-07-09 | 60k | Old Early Access mega-hit/full-release date, not a genuinely new project. |
| Split Fiction | 2025-03-06 | 54k | Established Hazelight/EA title. |
| Oblivion Remastered | 2025-04-22 | 51k | Remaster of old AAA game. |
| Hades II | 2025-09-25 | 38k | Sequel; Early Access history. |
| Civilization VII | 2025-02-10 | 33k | Long-running AAA strategy franchise. |

The top list is mixed: a couple of genuine new indie breakouts, but many of the biggest early-review games are sequels, remasters, franchise spinoffs, re-releases, or older Early Access projects whose Steam release date is not first public availability.

## Confounders and caveats

- **Release date is imperfect:** Steam's displayed release date can be full-release date, not first listing or Early Access launch; Palworld, Valheim and Hades II show why this matters.
- **Monthly rollups:** review histograms are monthly, so fixed-age review counts are approximate.
- **Platform growth:** Steam's user base grew materially (peak concurrent users roughly 27M → 40M+), so fixed thresholds are easier to clear in 2025-26.
- **Review-to-sales ratio:** reviews are an imperfect purchase/play proxy, especially for free games, Chinese-market games and genres with different review cultures.
- **Steam Next Fest:** demo festivals can shift wishlist and launch outcomes; demos were excluded from supply, but festival exposure affects usage.
- **Chinese-market growth:** regional growth changes review volume and the mix of high-usage games.
- **Review-prompt and visibility changes:** any Steam UI/prompt changes affect review propensity independent of sales.
- **Survivorship:** delisted/hidden games are missing from current search.
- **AI policy:** pre-2024 AI use is not observable; post-2024 disclosures depend on compliance and store-page availability.
- **Switch 2 launch:** 2026 attention and release timing may be affected by the broader console market.

## Verdict

Steam clearly shows **more supply**: new game releases roughly doubled to tripled from 2021 to 2026, with AI-disclosed games accounting for a large share of recent growth. It also shows **more modestly used new games in absolute count** at fixed equal-age review thresholds, but mostly because there are many more launches and a larger Steam audience; the percentage clearing ≥100 early reviews is not improving. It does **not** show convincing evidence of many more big hits: ≥1,000-review launches are up somewhat in count, but top items remain dominated by sequels, established studios, remasters/re-releases and old Early Access projects, with only a few new indie breakouts.

## Addendum (main session): full count at high thresholds, and AI share among used games
The sampled ≥1k estimates above are noisy, since only about 12–24 sampled games per half-year clear the bar.

`scripts/full_count_1k.py` takes *every* game in the supply crawl with ≥1,000 current reviews and fetches its review histogram. It then counts reviews in the first 90 days, handling weekly vs monthly rollups. `data/full_count_90d_candidates.csv`; no fetch errors.

| Cohort | ≥1k reviews in 90d | ≥2k | ≥5k |
|---|---:|---:|---:|
| 2021H1 | 99 | 63 | 27 |
| 2021H2 | 170 | 119 | 58 |
| 2022H1 | 113 | 58 | 31 |
| 2022H2 | 160 | 92 | 48 |
| 2023H1 | 132 | 85 | 43 |
| 2023H2 | 177 | 108 | 55 |
| 2024H1 | 188 | 120 | 56 |
| 2024H2 | 225 | 139 | 61 |
| 2025H1 | 203 | 127 | 57 |
| 2025H2 | 250 | 139 | 77 |
| 2026H1 | 251 | 127 | 64 |

- **≥1k (roughly ≥30–60k sales):** the 2022–23 average was 146 per half-year, rising to 207 (2024), 227 (2025) and 251 (2026H1). That is +20% vs 2024, against roughly +10% Steam audience growth.
- **≥2k and ≥5k:** flat since 2024.
- **Comparison with the sample:** the sampled estimate of 342 for 2026H1 was too high. The full count is closer to Zukowski's Q1 figure (88 → 96).

AI disclosure among the sample, using apps with both review and disclosure data:

| Cohort | AI share of releases | AI share among ≥10-review games | AI share among ≥100-review games |
|---|---:|---:|---:|
| 2024H1 | 8% | 6% | 4% |
| 2025H2 | 21% | 16% | 19% |
| 2026H1 | 26% | 18% | 13% |

The share of releases clearing ≥100 reviews in 90 days is flat at about 12–13% (70/599 → 75/600). The growth in modestly used games is therefore supply growth times an unchanged hit rate, and AI-disclosed games clear the bar at about half the rate of others.

**Revised verdict:** there are more modestly successful games in absolute terms: ≥100 early reviews about +60% vs 2024H1 (sampled), and ≥1k +20% (full count). There are no more big hits (≥2k/≥5k flat since 2024). A quarter of new releases now disclose AI use.
