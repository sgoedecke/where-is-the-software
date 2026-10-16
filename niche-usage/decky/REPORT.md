# Decky Loader plugin usage-cohort analysis

Run date: 2026-10-15. Output files: scripts in `scripts/`, raw caches in `cache/`, derived CSVs in `data/`.

## Sources and method

- Store API: `https://plugins.deckbrew.xyz/plugins?query=&tags=&sort_by=downloads`, fetched 2026-10-15. It returns 110 visible/stable plugins with top-level `downloads`, `updates`, `created`, `updated`, and per-version `created`, `downloads`, `updates`. I use top-level `created` as first stable listing date; it matches the first version timestamp in the API.
- Hidden API check: `https://plugins.deckbrew.xyz/plugins?hidden=true` returns 130 plugins: the 110 visible stable plugins plus 20 non-visible/hidden mostly old plugins. The cohort table below is for visible stable plugins only; hidden removals are a survivorship confounder.
- Registry repo: cloned `SteamDeckHomebrew/decky-plugin-database` at `a8e6d7f25cd2e39809f9501263fc7091e3d1971d` (2026-10-14). Plugins are submitted as submodules; `data/git_submodule_additions.csv` records first-addition commits for current submodules.
- Submission/backlog data: `gh pr list` for all 1,096 PRs, counting `plugin-addition` PRs and excluding `not-plugin`.
- Equal-age usage: Wayback has downloadable API snapshots with `downloads` from 2024-08 onward, but early 2023 snapshots lack downloads/created fields. `equal_age_*` below is the closest snapshot to 180 days after listing with age >=120 days; for 2022-2023 cohorts this is **not** really equal-age (median snapshot age 355-685 days), so equal-age comparisons are most useful from 2024 onward.
- Usage thresholds: low = >=5k downloads, modest = >=20k, high = >=100k. These are plugin downloads, not update counts.

## Cohort table

H2 2026 is partial through 2026-10-15 and has submission PRs but no new visible stable API listings yet.

| Cohort | Stable plugins now | Current >=5k | Current >=20k | Current >=100k | Equal-age n | Median age days | Equal-age >=5k | Equal-age >=20k | Equal-age >=100k | Addition PRs created | Addition PRs merged |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022-H2 | 11 | 11 | 11 | 9 | 11 | 685 | 11 | 9 | 5 | 42 | 27 |
| 2023-H1 | 24 | 24 | 24 | 13 | 24 | 496 | 24 | 20 | 6 | 36 | 23 |
| 2023-H2 | 14 | 14 | 13 | 7 | 14 | 355 | 13 | 8 | 1 | 28 | 19 |
| 2024-H1 | 8 | 8 | 7 | 4 | 8 | 215 | 7 | 3 | 1 | 23 | 8 |
| 2024-H2 | 5 | 4 | 2 | 0 | 5 | 184 | 2 | 0 | 0 | 13 | 5 |
| 2025-H1 | 19 | 19 | 13 | 3 | 19 | 272 | 16 | 7 | 1 | 23 | 20 |
| 2025-H2 | 8 | 8 | 4 | 1 | 8 | 207 | 7 | 2 | 1 | 15 | 7 |
| 2026-H1 | 21 | 15 | 5 | 0 | 21 | 215 | 14 | 4 | 0 | 68 | 23 |
| 2026-H2 | 0 | 0 | 0 | 0 | 0 | — | 0 | 0 | 0 | 38 | 0 |

Supply fell sharply in 2024 (13 visible stable listings for the whole year) and then recovered: 27 in 2025 and 21 in 2026-H1 alone. Submissions rose much more sharply than accepted stable listings in 2026-H1 (68 addition PRs, 23 merged), which means the stable-store supply count is review/backlog-limited. Current-download counts favor older cohorts, but 2025-H1 still has 13 modestly used plugins and 2026-H1 already has 5 modestly used plugins despite much less calendar time.

## Top recent items and AI/backlog check

Top 30 visible stable plugins listed since 2025 by current downloads. `New?` means the GitHub repo was created within 180 days before store listing; repo creation was checked with the GitHub API. 24/30 are genuinely recent repos by this rule.

| # | Plugin | Listed | Downloads | Repo created | New? | AI/agent note |
|---:|---|---:|---:|---:|---|---|
| 1 | Decky-Framegen | 2025-02-14 | 374,694 | 2025-01-21 | yes | graphics framegen/upscaling, not LLM/agent |
| 2 | Decky LSFG-VK | 2025-11-27 | 347,948 | 2025-07-11 | yes | graphics framegen/upscaling, not LLM/agent |
| 3 | PlayCount | 2025-01-14 | 158,376 | 2024-12-28 | yes |  |
| 4 | Deck Settings | 2025-01-25 | 130,040 | 2025-01-05 | yes |  |
| 5 | HueSync | 2025-06-22 | 81,299 | 2023-04-19 | old (795d) |  |
| 6 | Picture in Picture | 2025-01-14 | 74,888 | 2025-01-04 | yes |  |
| 7 | Virtual Surround Sound | 2025-03-05 | 50,647 | 2025-02-05 | yes |  |
| 8 | LetMeReShade | 2025-06-09 | 47,320 | 2025-02-05 | yes |  |
| 9 | Music Control | 2025-10-21 | 37,560 | 2025-09-11 | yes |  |
| 10 | Decky Sunshine | 2025-06-10 | 35,969 | 2024-03-29 | old (438d) |  |
| 11 | DeckSP | 2025-03-17 | 32,525 | 2023-12-24 | old (449d) |  |
| 12 | Better Keyboard | 2025-10-22 | 28,994 | 2025-09-21 | yes |  |
| 13 | Speed Test | 2026-01-06 | 28,897 | 2026-01-05 | yes |  |
| 14 | WiFi Locker | 2025-05-17 | 27,723 | 2025-03-28 | yes |  |
| 15 | Decky-Lookup | 2025-02-15 | 27,584 | 2025-01-18 | yes |  |
| 16 | Decky Proton Launch | 2026-05-13 | 22,973 | 2026-02-27 | yes |  |
| 17 | Non-Steam Badges | 2026-04-20 | 22,565 | 2026-01-23 | yes |  |
| 18 | Simple Timer | 2025-02-07 | 22,480 | 2025-01-22 | yes |  |
| 19 | Deck Shelves | 2026-05-06 | 21,707 | 2024-07-14 | old (661d) |  |
| 20 | Launch Options | 2026-02-22 | 20,935 | 2026-01-10 | yes |  |
| 21 | Dimmer Deck | 2025-10-13 | 20,849 | 2025-09-18 | yes |  |
| 22 | Crosshair | 2025-01-16 | 20,287 | 2025-01-11 | yes |  |
| 23 | Decky Ludusavi | 2025-03-23 | 17,792 | 2024-01-06 | old (442d) |  |
| 24 | MuraDeck | 2025-08-07 | 17,712 | 2025-05-10 | yes |  |
| 25 | Decky Translator | 2026-02-27 | 17,434 | 2026-01-12 | yes | translation; only strict AI-term hit |
| 26 | Deck Progress Tracker | 2026-04-23 | 16,190 | 2026-02-08 | yes |  |
| 27 | Game Sync | 2025-04-14 | 15,947 | 2023-10-20 | old (542d) |  |
| 28 | Network Sentinel | 2025-11-27 | 15,843 | 2025-10-07 | yes |  |
| 29 | Steam Status | 2026-02-14 | 12,211 | 2026-01-02 | yes |  |
| 30 | Download All | 2026-03-28 | 11,923 | 2026-03-27 | yes |  |

Strict AI/LLM/agent term scan of all stable plugin names/descriptions/tags only flagged Decky Translator; there is no visible LLM/coding-agent plugin cohort. If graphics frame generation/upscaling is counted as AI-adjacent, the two largest recent hits are AI-adjacent graphics utilities, but they are not AI coding or agent tools.

Backlog: as of the PR scrape, there are 21 open `plugin-addition` PRs, 6 marked `stale`; the oldest is #1015, opened 2026-04-01. H2 2026 already has 38 addition PRs but zero merged/listed stable plugins, indicating a queue/review bottleneck rather than lack of attempted supply. The Decky testing guide says submitted plugins are installed via the testing store and tested from PRs before production-store acceptance, so PR volume is a better leading indicator than stable-store listings during a backlog.

## Confounders and caveats

- **Current downloads favor old cohorts.** Equal-age download snapshots only start in 2024-08 with download fields. Old cohorts' equal-age rows are over-aged; use them only as rough context.
- **Survivorship/delisting.** The default store API hides 20 non-visible plugins returned by `hidden=true`, mostly old low/zero-download plugins plus Decky Recorder. Excluding hidden plugins makes early cohorts look healthier.
- **Review/testing bottleneck.** The production store requires testing via PR/testing store before merge; 2026 PR submissions greatly exceed merged additions.
- **Store/version instrumentation changed.** Wayback snapshots before 2024-08 lack download and created fields, and Decky Loader v3.0.0 shipped in 2024-09 with store/install work in its changelog. That limits equal-age measurement and may affect download comparability.
- **Platform/user-base growth.** Steam Deck and handheld SteamOS adoption grew across this period; Steam Deck OLED, SteamOS updates, and SteamOS on non-Valve handhelds in 2025 expand the addressable base, so raw downloads are not normalized by installed base.
- **SteamOS/Decky breakage cycles.** SteamOS changes can break Decky or plugins; Decky release notes include SteamOS 3.7-related fixes in 2025. Such cycles can suppress or spike updates/downloads independent of plugin quality.

## Verdict

Decky **does show more supply** after the AI-coding inflection, but the strongest signal is submissions/backlog: stable listings rose from 13 in 2024 to 27 in 2025 and 21 in 2026-H1, while 2026-H1 had 68 addition PRs. Decky **does show more modestly used new tools**: 2025-H1 has 13 current >=20k plugins and 2026-H1 already has 5, with equal-age proxies also showing several 2025-2026 plugins clearing 20k. Decky **does not clearly show more big hits**: 2025 produced four current >=100k recent hits (two framegen/upscaling), but 2026 has none yet and the 2022-2023 cohorts still dominate high-download counts.
