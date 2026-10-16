# Nexus Mods niche usage cohorts

Source folder: `nexus`. Games: Skyrim Special Edition, Stardew Valley, Cyberpunk 2077, Baldur's Gate 3, and Fallout 4.

## Cohort table (selected games combined)

Counts are public still-listed mods created in each half-year. `2026H2*` is partial through 2026-10-15. Download counters are current cumulative totals, so older cohorts are age-advantaged.

| cohort | class | N | >=100 dl | >=1k dl | >=10k dl | >=10 end | >=100 end |
|---|---|---|---|---|---|---|---|
| 2021H1 | code_tool | 2322 | 2245 | 1579 | 702 | 2105 | 1184 |
| 2021H1 | asset_only | 5396 | 5221 | 3706 | 1613 | 4930 | 2809 |
| 2021H2 | code_tool | 2595 | 2505 | 1801 | 936 | 2360 | 1321 |
| 2021H2 | asset_only | 4959 | 4791 | 3330 | 1378 | 4503 | 2391 |
| 2022H1 | code_tool | 3077 | 2958 | 2143 | 1110 | 2785 | 1466 |
| 2022H1 | asset_only | 6127 | 5901 | 4187 | 1834 | 5539 | 2865 |
| 2022H2 | code_tool | 3695 | 3496 | 2356 | 1194 | 3222 | 1591 |
| 2022H2 | asset_only | 7374 | 7066 | 4792 | 2131 | 6482 | 3161 |
| 2023H1 | code_tool | 3840 | 3634 | 2370 | 1091 | 3267 | 1352 |
| 2023H1 | asset_only | 7798 | 7463 | 5058 | 2534 | 6782 | 3327 |
| 2023H2 | code_tool | 6162 | 5852 | 4013 | 1900 | 5203 | 2345 |
| 2023H2 | asset_only | 10016 | 9487 | 6557 | 3098 | 8454 | 4022 |
| 2024H1 | code_tool | 7219 | 6665 | 3913 | 1754 | 5310 | 1884 |
| 2024H1 | asset_only | 13968 | 13144 | 8505 | 3802 | 11314 | 4796 |
| 2024H2 | code_tool | 5883 | 5217 | 2853 | 1198 | 4034 | 1212 |
| 2024H2 | asset_only | 11320 | 10290 | 6339 | 2879 | 8597 | 3446 |
| 2025H1 | code_tool | 6203 | 5312 | 2649 | 1050 | 3844 | 1011 |
| 2025H1 | asset_only | 11558 | 10450 | 5853 | 2674 | 8243 | 3039 |
| 2025H2 | code_tool | 6851 | 5512 | 2380 | 890 | 3703 | 789 |
| 2025H2 | asset_only | 11747 | 10208 | 5458 | 2344 | 7746 | 2342 |
| 2026H1 | code_tool | 8645 | 5858 | 2238 | 719 | 3670 | 662 |
| 2026H1 | asset_only | 12952 | 9729 | 4430 | 1574 | 6690 | 1576 |
| 2026H2* | code_tool | 7105 | 3961 | 1142 | 219 | 2063 | 311 |
| 2026H2* | asset_only | 7842 | 5115 | 1792 | 366 | 3149 | 403 |

Full per-game rows are in `cohorts_by_game_class.csv`; combined rows are in `cohorts_aggregate.csv`.

## Method

I introspected `https://api.nexusmods.com/v2/graphql`, then queried `mods` by `gameDomainName`, `createdAt` epoch-second ranges, category filters and threshold filters. Each cohort/class request batched six counts (`N`, three download thresholds, two endorsement thresholds) into one GraphQL call; responses are cached under `cache/` with a fixed User-Agent and pacing. Removed/hidden mods are not recoverable from the public listing, so `N` means still listed. `uniqueDownloads` appears as a sort input but not as a `Mod` field or `ModsFilter`; the public unauthenticated API exposes `downloads`, so thresholds below use current cumulative total downloads rather than unique downloads.

Classification is category-based and reproducible in `category_classification.csv`: utility/tool/framework/script/patch/bug-fix/UI/gameplay categories are `code_tool`; texture/model/preset/armour/clothing/appearance/audio/location/weapon/equipment categories are `asset_only`; other categories are kept as `other_mixed` in the CSVs. This deliberately separates code/tool-like mod work from asset-heavy categories, but many mods are mixed.

I did not use Wayback for the cohort table: Nexus pages are dynamic and CDX snapshots do not expose reliable download counters at scale. Therefore recent cohorts beating older cohorts is robust, while recent cohorts trailing older ones is inconclusive.

## Top recent code/tool mods

| game | mod | downloads | end | category | origin | AI |
|---|---|---|---|---|---|---|
| Skyrim Special Edition | [Immersive Collections Resources](https://www.nexusmods.com/skyrimspecialedition/mods/158971) | 2436459 | 584 | Modders Resources | appears newly listed | no explicit AI-built claim found |
| Skyrim Special Edition | [Follower Stats](https://www.nexusmods.com/skyrimspecialedition/mods/159406) | 1287555 | 2038 | User Interface | likely established/port/update/framework | no explicit AI-built claim found |
| Skyrim Special Edition | [Julian's Patches - RS Children Patch Hub](https://www.nexusmods.com/skyrimspecialedition/mods/164145) | 1262469 | 177 | Patches | appears newly listed | no explicit AI-built claim found |
| Skyrim Special Edition | [HorsePower - Modernized Horse Riding (Total Riding Overhaul)](https://www.nexusmods.com/skyrimspecialedition/mods/169335) | 1252525 | 3368 | Gameplay | appears newly listed | no explicit AI-built claim found |
| Skyrim Special Edition | [Skyrim Cell load Freeze fix NG](https://www.nexusmods.com/skyrimspecialedition/mods/160704) | 1115845 | 8023 | Bug Fixes | likely established/port/update/framework | explicit AI-assisted/generated tag/text found |
| Cyberpunk 2077 | [Auto Drive Enhanced](https://www.nexusmods.com/cyberpunk2077/mods/23157) | 928463 | 2045 | Gameplay | appears newly listed | no explicit AI-built claim found |
| Cyberpunk 2077 | [Deceptious Quest Core Utilities and Settings](https://www.nexusmods.com/cyberpunk2077/mods/24404) | 846672 | 1852 | Utilities | likely established/port/update/framework | no explicit AI-built claim found |
| Skyrim Special Edition | [Save and Load Accelerator for SKSE Cosaves - S.L.A.C.K.](https://www.nexusmods.com/skyrimspecialedition/mods/163969) | 809019 | 4364 | Bug Fixes | likely established/port/update/framework | no explicit AI-built claim found |
| Skyrim Special Edition | [Misc Utility Plugins](https://www.nexusmods.com/skyrimspecialedition/mods/143035) | 787333 | 715 | Utilities | likely established/port/update/framework | no explicit AI-built claim found |
| Cyberpunk 2077 | [Map Exit Lighting and HDR Fixes](https://www.nexusmods.com/cyberpunk2077/mods/23420) | 782885 | 1669 | Gameplay | appears newly listed | no explicit AI-built claim found |

## AI-assisted tag share

The public facets expose tags including `AI-Generated Content`, `AI Assisted`, and `AI Media`; the table reports the share of recent code/tool-category mods carrying one of those tags.

| period | game | class | n | ai_tagged_n | ai_tagged_share |
|---|---|---|---|---|---|
| 2025H2-2026YTD | Skyrim Special Edition | code_tool | 10204 | 1515 | 0.1485 |
| 2025H2-2026YTD | Stardew Valley | code_tool | 3451 | 773 | 0.224 |
| 2025H2-2026YTD | Cyberpunk 2077 | code_tool | 2740 | 361 | 0.1318 |
| 2025H2-2026YTD | Baldur's Gate 3 | code_tool | 3072 | 317 | 0.1032 |
| 2025H2-2026YTD | Fallout 4 | code_tool | 3134 | 337 | 0.1075 |
| 2025H2-2026YTD | ALL | code_tool | 22601 | 3303 | 0.1461 |

## Confounders

- Nexus GraphQL returns public still-listed mods only; deleted, hidden, adult/user-blocked, or policy-removed items are a survivorship blind spot.
- Current cumulative downloads/endorsements are age-confounded and discovery-confounded; older cohorts had more time to accrue usage.
- Game events matter: Fallout 4's April 2024 next-gen update, BG3 official modding tools and patches in 2024-25, Skyrim Anniversary Edition/runtime churn, Stardew 1.6, and Cyberpunk 2.x/Phantom Liberty framework churn.
- Nexus Collections, search/ranking changes, and AI-content policy/tagging can affect visibility and metadata independently of AI coding.
- Category boundaries are fuzzy: some gameplay mods are data-only; some armour/weapon mods contain plugins; Content Patcher/SMAPI ecosystems blur code vs asset packs.

## Verdict

Across these five stable modding scenes, code/tool-category cohorts rose from a 2022-24 mean of 4979 still-listed mods per half-year to 7748 in 2025H2-2026H1 (1.6x); asset-heavy cohorts rose from 9434 to 12350 (1.3x). High-download code/tool hits did not show the same break: ≥10k-download code/tool mods averaged 1374 per half-year in 2022-24 versus 804 in 2025H2-2026H1, despite the metric favouring older cohorts. This supports the hypothesis for Nexus: many more small/recent mods, including code/tool mods, but no clear surge of new breakout hits.

## Files

- `fetch_nexus.py`: reproducible script
- `schema_introspection_lite.json`: introspection evidence
- `cohorts_aggregate.csv`, `cohorts_by_game_class.csv`: cohort counts
- `category_classification.csv`, `notable_tags.csv`: classification evidence
- `recent_top_code_mods.csv`, `ai_tag_share.csv`: recent top mods and AI tag checks
