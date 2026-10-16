# AMO Firefox extension cohorts (current ADU)

Source: AMO public API v5, Firefox extensions (`type=extension&app=firefox`), fetched 2026-10-15. Output files in this folder:

- `fetch_amo.py` — cached AMO search fetcher.
- `analyze_amo.py` — cohort/top-item analysis.
- `wayback_equal_age_probe.py` — best-effort Wayback equal-age probe.
- `addons_firefox_extensions_current.csv` — flattened current AMO records (90,572 rows).
- `cohorts_current_adu.csv` — cohort table below.
- `top_recent_current_adu.csv` — top recent add-ons by current ADU.
- `wayback_equal_age_probe_2024H1_top10.csv` — small Wayback coverage probe.

Thunderbird was not included: the cheap probes `https://addons.thunderbird.net/api/v5/addons/search/?type=extension&sort=created&page_size=3&app=thunderbird` and AMO with `app=thunderbird` returned 404/400 respectively.

## Method

I used half-year creation cohorts from 2021H1 through 2026H2-to-date. The global AMO search sorted by creation date reports 109,672 Firefox extensions but exposes only 600 result pages at `page_size=50`; date slicing was therefore required. AMO accepts `created__gte` and `created__lte`, and every half-year slice stayed below the cap (maximum 403 pages), so the fetch enumerated all currently public/listed search results in each slice.

Usage is `average_daily_users` (ADU), as returned by the API at fetch time. This is a valuable active-use measure, but it is **not equal-age**: old extensions have had more time to accumulate awareness, while some old extensions also decay. Removed, disabled, and unlisted add-ons are not recoverable from this search endpoint, so `N` below means **still listed by AMO now**, not all add-ons ever created.

I tried the Wayback path for equal-age ADU. For the top 10 current-ADU 2024H1 add-ons, I queried 2025H2 detail-page captures, roughly creation+18 months, and parsed AMO's embedded `average_daily_users`. Coverage was only 6/10, and it was a top-current-ADU sample, so it is not enough for cohort threshold counts. It does confirm that detail pages can contain historical ADU, but a full equal-age run would require many more CDX requests and would still be biased by sparse captures.

## Cohorts, current ADU

| cohort | still listed | ADU ≥10 | share | ADU ≥100 | share | ADU ≥1k | share | ADU ≥10k | share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021H1 | 2,375 | 872 | 36.7% | 372 | 15.7% | 113 | 4.8% | 22 | 0.9% |
| 2021H2 | 1,958 | 747 | 38.2% | 286 | 14.6% | 82 | 4.2% | 16 | 0.8% |
| 2022H1 | 2,135 | 736 | 34.5% | 289 | 13.5% | 73 | 3.4% | 15 | 0.7% |
| 2022H2 | 2,279 | 815 | 35.8% | 336 | 14.7% | 79 | 3.5% | 15 | 0.7% |
| 2023H1 | 2,973 | 1,042 | 35.0% | 409 | 13.8% | 108 | 3.6% | 21 | 0.7% |
| 2023H2 | 3,163 | 965 | 30.5% | 396 | 12.5% | 113 | 3.6% | 19 | 0.6% |
| 2024H1 | 3,730 | 1,108 | 29.7% | 406 | 10.9% | 93 | 2.5% | 19 | 0.5% |
| 2024H2 | 5,248 | 1,384 | 26.4% | 450 | 8.6% | 80 | 1.5% | 10 | 0.2% |
| 2025H1 | 11,517 | 2,168 | 18.8% | 666 | 5.8% | 138 | 1.2% | 9 | 0.1% |
| 2025H2 | 14,978 | 2,264 | 15.1% | 603 | 4.0% | 99 | 0.7% | 4 | 0.0% |
| 2026H1 | 20,096 | 3,178 | 15.8% | 673 | 3.3% | 86 | 0.4% | 6 | 0.0% |
| 2026H2* | 20,120 | 1,201 | 6.0% | 190 | 0.9% | 38 | 0.2% | 4 | 0.0% |

\* 2026H2 is partial through 2026-10-15 and much younger on the current-ADU measure.

Baseline 2022-24 mean per half-year: 3,255 listed, 1,008 with ADU ≥10, 381 with ADU ≥100, 91 with ADU ≥1k, and 16.5 with ADU ≥10k. 2025H1-2026H1 mean: 15,530 listed, 2,537 with ADU ≥10, 647 with ADU ≥100, 108 with ADU ≥1k, and 6.3 with ADU ≥10k. Thus the low/modest bars rose in absolute count despite severe age disadvantage, while the high bars were flat or down.

## Top recent items by current ADU (2025H2-2026H2)

| rank | add-on | cohort | ADU | judgment |
|---:|---|---|---:|---|
| 1 | [7TV](https://addons.mozilla.org/en-US/firefox/addon/7tv-new/) | 2026H1 | 73,218 | Established Twitch/YouTube emote ecosystem newly/again listed on AMO; not AI-themed; not stated AI-built. |
| 2 | [DuckDuckGo No-AI Search](https://addons.mozilla.org/en-US/firefox/addon/duckduckgo-no-ai-search/) | 2026H1 | 36,644 | Official DuckDuckGo anti-AI/search product; AI-themed only in the sense of avoiding AI; not stated AI-built. |
| 3 | [Bato Image Auto-Fixer](https://addons.mozilla.org/en-US/firefox/addon/bato-image-auto-fixer/) | 2025H2 | 30,206 | Genuinely niche site-specific bato.to repair tool; not AI-themed; not stated AI-built. |
| 4 | [Video DownloadHelper](https://addons.mozilla.org/en-US/firefox/addon/video-downloadhelper-allinone/) | 2026H1 | 28,672 | Generic video downloader using an established extension name; likely opportunistic/clone-like rather than a new niche community tool; not AI-themed. |
| 5 | [TTV AB - Lightweight Twitch.tv Ad Blocker](https://addons.mozilla.org/en-US/firefox/addon/ttv-ab-twitch-ad-blocker/) | 2026H1 | 22,452 | Twitch ad-blocker with GitHub support link; niche-ish but follows an existing category/project pattern; not AI-themed. |
| 6 | [City Scapes](https://addons.mozilla.org/en-US/firefox/addon/city-scapes-ext/) | 2026H2 | 21,722 | New-tab/search extension from a publisher also holding adjacent landscape themes; very high ADU with tiny weekly downloads suggests external distribution or measurement oddity; not AI-themed. |
| 7 | [Beautiful Beaches](https://addons.mozilla.org/en-US/firefox/addon/beautiful-beaches/) | 2026H2 | 21,682 | Same publisher/theme cluster as City Scapes; not a clearly organic niche tool; not AI-themed. |
| 8 | [Knockoff - Amazon Shopping Filter](https://addons.mozilla.org/en-US/firefox/addon/knockoff-amazon-brand-filter/) | 2026H2 | 21,634 | Genuinely new shopping-filter niche tool; not AI-themed; not stated AI-built. |
| 9 | [Majestic Mountain Views](https://addons.mozilla.org/en-US/firefox/addon/majestic-mountain-views/) | 2026H2 | 21,618 | Same landscape/new-tab/search cluster; not a clearly organic niche tool; not AI-themed. |
| 10 | [Age verification bypass](https://addons.mozilla.org/en-US/firefox/addon/age-verification-bypass/) | 2026H1 | 18,308 | Niche bypass utility with GitHub support link; not AI-themed; not stated AI-built. |

Only one top-10 item is AI-themed, and it is anti-AI search, not AI-built. I found no top-10 description or linked summary explicitly saying the extension was built with AI. The 2025H2-2026 cohorts do include many AI-related text hits (`ai_text_counts_recent.json`), but these were not the largest winners.

## Confounders and caveats

- **Current ADU is age-confounded.** Recent cohorts are disadvantaged for awareness/retention; older cohorts may also be decayed. Therefore recent cohorts beating old cohorts at ADU ≥10/≥100 is strong evidence, while recent cohorts trailing at ≥1k/≥10k is less conclusive.
- **Firefox user base is slowly declining.** Fixed ADU thresholds likely become harder over time if the platform shrinks; I did not scale thresholds because I did not pull a clean half-year Firefox-total denominator. Mozilla's public Firefox activity dashboard is the relevant denominator source.
- **AMO survivorship.** The API search only exposes add-ons still listed/public now. Deleted, disabled, rejected, and unlisted creations are missing, so creation counts are lower bounds for public-listed supply.
- **Policy/review changes.** Firefox MV3 work changed extension architecture requirements beginning around Firefox 106/MV3 rollout; Mozilla's Extension Workshop documents MV3 migration. AMO policies also now include detailed data-transmission consent rules, including built-in consent for Firefox 140+ extensions. Validator/review requirements can alter listing rates independently of AI coding.
- **Bots/external installs/search extensions.** Some 2026 top items have very high ADU and near-zero weekly downloads, especially new-tab/search clusters. These may reflect external distribution, bundling, enterprise/policy installs, or AMO telemetry quirks rather than organic community adoption.
- **Review backlog and spam.** The enormous 2025-26 creation jump includes many zero-ADU or very low-ADU entries and likely some spam/SEO/search extensions; top-item classification shows several non-community or opportunistic entries.

## Verdict

AMO strongly supports the “more small tools” half of the hypothesis: compared with the 2022-24 mean, 2025H1-2026H1 had about 4.8× as many listed creations, 2.5× as many extensions with ADU ≥10, and 1.7× as many with ADU ≥100. It does **not** show more big hits: ADU ≥1,000 is roughly flat and ADU ≥10,000 is down, even before discounting suspicious externally distributed new-tab/search items. The result matches the niche-community pattern, with the caveat that this is current ADU rather than full equal-age measurement.
