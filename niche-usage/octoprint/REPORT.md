# OctoPrint plugin cohort usage

Generated 2026-10-15. Source: OctoPrint plugin registry, plugins.octoprint.org git history, data.octoprint.org exports, Wayback Machine snapshots. Current 30-day OctoPrint instance denominator: 50,989.

## Cohort table: current 30-day active instances

This table uses current `instances_month` for plugins still listed today; deleted/unlisted plugins are counted in `created` where recovered from git, but have no current usage in the registry, so the usage shares are also shown over still-listed plugins.

| cohort | created incl. recovered deleted | still listed | ≥10 | ≥100 | ≥1,000 |
|---|---:|---:|---:|---:|---:|
| 2021H1 | 40 | 40 | 36 (90%) | 23 (57%) | 2 (5%) |
| 2021H2 | 21 | 19 | 14 (74%) | 9 (47%) | 0 (0%) |
| 2022H1 | 30 | 29 | 21 (72%) | 9 (31%) | 1 (3%) |
| 2022H2 | 9 | 8 | 7 (88%) | 2 (25%) | 0 (0%) |
| 2023H1 | 14 | 14 | 13 (93%) | 5 (36%) | 2 (14%) |
| 2023H2 | 8 | 8 | 7 (88%) | 5 (62%) | 0 (0%) |
| 2024H1 | 17 | 17 | 16 (94%) | 9 (53%) | 0 (0%) |
| 2024H2 | 7 | 7 | 7 (100%) | 4 (57%) | 0 (0%) |
| 2025H1 | 4 | 4 | 3 (75%) | 1 (25%) | 0 (0%) |
| 2025H2 | 2 | 2 | 2 (100%) | 1 (50%) | 0 (0%) |
| 2026H1 | 3 | 3 | 3 (100%) | 1 (33%) | 0 (0%) |
| 2026H2 | 4 | 4 | 4 (100%) | 1 (25%) | 0 (0%) |

## Equal-age check

For equal-age usage, I chose the closest available 30-day active-instance snapshot between 150 and 365 days after a plugin's published/add date. Snapshots are sparse, so `eligible` is often below `created`; normalized columns scale each plugin by OctoPrint total instances at the nearest `instance_stats_30d` snapshot to the current denominator where a nearby total-instance snapshot exists.

| cohort | created | eligible | norm eligible | ≥10 abs | ≥100 abs | ≥1,000 abs | ≥10 norm | ≥100 norm | ≥1,000 norm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021H1 | 40 | 40 | 3 | 40 (100%) | 32 (80%) | 7 (18%) | 3 (100%) | 2 (67%) | 0 (0%) |
| 2021H2 | 21 | 20 | 19 | 20 (100%) | 13 (65%) | 2 (10%) | 19 (100%) | 8 (42%) | 1 (5%) |
| 2022H1 | 30 | 30 | 0 | 29 (97%) | 18 (60%) | 1 (3%) | n/a | n/a | n/a |
| 2022H2 | 9 | 2 | 0 | 2 (100%) | 2 (100%) | 0 (0%) | n/a | n/a | n/a |
| 2023H1 | 14 | 14 | 0 | 14 (100%) | 12 (86%) | 4 (29%) | n/a | n/a | n/a |
| 2023H2 | 8 | 8 | 6 | 8 (100%) | 6 (75%) | 0 (0%) | 5 (83%) | 3 (50%) | 0 (0%) |
| 2024H1 | 17 | 17 | 17 | 17 (100%) | 12 (71%) | 0 (0%) | 16 (94%) | 10 (59%) | 0 (0%) |
| 2024H2 | 7 | 7 | 7 | 7 (100%) | 4 (57%) | 0 (0%) | 7 (100%) | 4 (57%) | 0 (0%) |
| 2025H1 | 4 | 4 | 4 | 3 (75%) | 0 (0%) | 0 (0%) | 3 (75%) | 0 (0%) | 0 (0%) |
| 2025H2 | 2 | 2 | 2 | 2 (100%) | 1 (50%) | 0 (0%) | 2 (100%) | 1 (50%) | 0 (0%) |
| 2026H1 | 3 | 2 | 2 | 2 (100%) | 1 (50%) | 0 (0%) | 2 (100%) | 1 (50%) | 0 (0%) |
| 2026H2 | 4 | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

## Top recent plugins

| plugin | cohort | current instances | judgement | AI? |
|---|---:|---:|---|---|
| OctoPrint Wrapped! (`wrapped`) | 2025H2 | 462 | appears newly created/listed together | no explicit AI signal in description/README spot-check |
| Octo Fire Guard (`octo_fire_guard`) | 2026H1 | 324 | appears newly created/listed together | no explicit AI signal in description/README spot-check |
| OctoPrint-Maintenance-Reminder (`maintenance_reminder`) | 2026H2 | 176 | appears newly created/listed together | no explicit AI signal in description/README spot-check |
| OctoPrint-Remote_connection (`remote_connection`) | 2025H2 | 85 | appears newly created/listed together | no explicit AI signal in description/README spot-check |
| BitBang (`bitbang`) | 2026H2 | 39 | appears newly created/listed together | registry attribute: ai-developed |
| PSU Control - eWeLink (`psucontrol_ewelink`) | 2026H1 | 35 | appears newly created/listed together | registry attribute: ai-developed |
| OctoPrint-Proxy4Artisan (`proxy4artisan`) | 2026H1 | 13 | appears newly created/listed together | no explicit AI signal in description/README spot-check |
| Tapo Auto Shutdown + Obico Delay (`tapoautoshutdown`) | 2026H2 | 10 | appears newly created/listed together | AI-themed/mentions AI; registry attribute: ai-developed |
| Prusa Chamber Light (`chamberlight`) | 2026H2 | 10 | appears newly created/listed together | registry attribute: ai-developed |

## Klipper comparison

As a cheap comparison for the Klipper/Moonraker ecosystem, I counted GitHub repositories with the `klipper-plugin` topic by repository creation year. This is a supply-side comparison, not usage.

| year | klipper-plugin repos created |
|---:|---:|
| 2021 | 0 |
| 2022 | 0 |
| 2023 | 0 |
| 2024 | 1 |
| 2025 | 1 |
| 2026 | 24 |

## Method

- Creation cohorts are half-years from 2021H1 through partial 2026H2. For still-listed plugins I used the registry `published` date; for deleted/unlisted plugins I recovered first-add dates for `_plugins/*.md` from the site git history where possible. The site repo contains listing files and a `plugins.json` template; rendered stats are not committed there, so historical stats come from data exports and Wayback snapshots.
- Usage is OctoPrint anonymous-telemetry `instances_month` (unique active instances seen in the last 30 days), not cumulative downloads. Current usage comes from `https://plugins.octoprint.org/plugins.json`; historical equal-age usage comes from Wayback snapshots of that file plus `data.octoprint.org/export/plugin_stats_30d.json`.
- Normalization uses `data.octoprint.org/export/instance_stats_30d.json` total OctoPrint instances and scales historical plugin instances to the current total denominator. When no nearby total-instance snapshot exists, normalized counts omit that plugin.
- API calls used a custom User-Agent, cached responses under this output folder, and slept between requests.

## Confounders

- Survivorship: removed plugins are recoverable for counts from git, but current registry usage only exists for plugins still listed. Historical snapshots partly mitigate this but are sparse.
- OctoPrint active instances appear flat/down versus the pandemic-era peak; current `instance_stats_30d` is about 51k, and normalized equal-age counts are therefore important.
- Registry review/listing dates may lag actual plugin creation, and a GitHub repo can predate the registry listing.
- Stats are anonymous telemetry from opted-in/reporting OctoPrint instances, not all installations, and commercial/manipulated plugins may be excluded from public stats.
- Maker ecosystem demand shifted toward Klipper/Moonraker/Mainsail/Fluidd and Bambu workflows, so OctoPrint is not the full 3D-printing plugin market.

## Verdict

OctoPrint does not show a big post-2025 explosion in successful new plugins: current listed-plugin cohorts in 2025H2-2026 average 3.0 plugins above 10 active instances per half-year versus 11.8 in 2022-24, and the ≥100 bar is 1.0 versus 5.7.
The ≥1,000 bar remains essentially empty for new cohorts: 0 recent plugins versus 3 across 2022-24 cohorts, and equal-age snapshots tell the same story despite sparse coverage.
This source therefore weakly supports the broader hypothesis only at the very low bar, if at all: OctoPrint has some new niche utilities, including several registry entries marked `ai-developed`, but no clear surge of widely used new software.
