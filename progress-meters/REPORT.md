# Progress meters for hard software progress (2020-2026)

Generated from public project-published data. Slopes are linear fits over 2022-01..2024-12 vs 2025-01..latest unless noted; WPT Interop uses averaged within-year daily slopes because the official focus areas reset each year. Ratio is raw post/baseline slope, so lower-is-better series need sign-aware interpretation in the verdict.

| series | 2022-24 slope | 2025-26 slope | ratio | confounders | verdict |
|---|---:|---:|---:|---|---|
| ProtonDB latest-app works share | 0.148 percentage-points/month | 0.094 percentage-points/month | 0.634 | Quarterly sampled cumulative dumps; raw yes/no “works” reports, not ProtonDB tier algorithm; report volume and user/game mix changed. | Works share kept improving, but the 2025-26 slope is slower than 2022-24; no trend-break acceleration. |
| ProtonDB tested unique apps | 374.4 apps/month | 438.4 apps/month | 1.171 | Quarterly sampled cumulative dumps; supply of reports/users is endogenous to Steam Deck/Linux gaming growth. | Volume growth accelerated, but this is testing coverage not quality. |
| Xenia playable issues | 0.761 games/month | 0.000 games/month | 0.000 | Current-label + issue-creation approximation; label-event history not replayed. Xenia tracker README says it is no longer maintained since xenia master is dead. | No reliable AI-era acceleration signal. |
| Vita3K playable issues | 19.97 games/month | 15.06 games/month | 0.754 | Current-label + issue-creation approximation; label-event history not replayed. GitHub API caps result pagination at the first 1000 current playable issues. | No reliable AI-era acceleration signal. |
| shadPS4 playable issues | 0.000 games/month | 17.62 games/month | n/a | Current-label + issue-creation approximation; label-event history not replayed. Newer emulator with PS4-native-port excitement in 2026; project/team maturity is a major confounder. | Positive break |
| ScummVM supported games | 3.274 game entries/month | 12.79 game entries/month | 3.906 | Counts compatibility-page entries; 2026 cadence/name change and Wintermute batch caused a structural jump. | Strong 2026 acceleration, but mostly explained by release-cadence and engine batch additions. |
| WPT Interop stable within-year gain | 31.42 score-points/month | 39.56 score-points/month | 1.259 | Official focus areas reset yearly; this averages per-year daily linear slopes for stable browsers; annual difficulty and browser staffing/funding changed. | Within-year Interop improvement accelerated in 2025, but 2026-to-date is lower and the reset/difficulty confound is large. |
| Wine dev-release bugs fixed | 46.66 bugs/month | 47.39 bugs/month | 1.016 | Counts announced fixed bugs, not user-visible compatibility; release cadence changed slightly; excludes stable rollup notes. | Post-2025 bug-fix throughput is roughly similar/slower, not an acceleration. |
| WebAIM avg errors/page | 0.250 errors/page/month | 0.425 errors/page/month | 1.700 | Annual sample; WAVE rules/site mix/page complexity changed; lower is better. | No positive break: errors worsened in 2025-26. |
| WebAIM WCAG failure % | -0.037 percentage-points/month | 0.092 percentage-points/month | -2.444 | Annual sample; detectable failures only; lower is better; page complexity rose sharply. | No positive break: previous improvement reversed in 2026. |

## Details by series

### ProtonDB latest-app works share

- Data: `data/protondb_unique_works_series.csv`; chart: `charts/protondb_unique_works.png`.

- Baseline slope: 0.148 percentage-points/month (n=12); 2025-26 slope: 0.094 percentage-points/month (n=8); raw ratio 0.634.

- Confounders: Quarterly sampled cumulative dumps; raw yes/no “works” reports, not ProtonDB tier algorithm; report volume and user/game mix changed.

- Verdict: Works share kept improving, but the 2025-26 slope is slower than 2022-24; no trend-break acceleration.

### ProtonDB tested unique apps

- Data: `data/protondb_tested_apps_series.csv`; chart: `charts/protondb_tested_apps.png`.

- Baseline slope: 374.4 apps/month (n=12); 2025-26 slope: 438.4 apps/month (n=8); raw ratio 1.171.

- Confounders: Quarterly sampled cumulative dumps; supply of reports/users is endogenous to Steam Deck/Linux gaming growth.

- Verdict: Volume growth accelerated, but this is testing coverage not quality.

### Xenia playable issues

- Data: `data/xenia_playable_series.csv`; chart: `charts/xenia_playable.png`.

- Baseline slope: 0.761 games/month (n=36); 2025-26 slope: 0.000 games/month (n=22); raw ratio 0.000.

- Confounders: Current-label + issue-creation approximation; label-event history not replayed. Xenia tracker README says it is no longer maintained since xenia master is dead.

- Verdict: No reliable AI-era acceleration signal.

### Vita3K playable issues

- Data: `data/vita3k_playable_series.csv`; chart: `charts/vita3k_playable.png`.

- Baseline slope: 19.97 games/month (n=36); 2025-26 slope: 15.06 games/month (n=22); raw ratio 0.754.

- Confounders: Current-label + issue-creation approximation; label-event history not replayed. GitHub API caps result pagination at the first 1000 current playable issues.

- Verdict: No reliable AI-era acceleration signal.

### shadPS4 playable issues

- Data: `data/shadps4_playable_series.csv`; chart: `charts/shadps4_playable.png`.

- Baseline slope: 0.000 games/month (n=36); 2025-26 slope: 17.62 games/month (n=22); raw ratio n/a.

- Confounders: Current-label + issue-creation approximation; label-event history not replayed. Newer emulator with PS4-native-port excitement in 2026; project/team maturity is a major confounder.

- Verdict: Positive break

### ScummVM supported games

- Data: `data/scummvm_supported_games_series.csv`; chart: `charts/scummvm_supported_games.png`.

- Baseline slope: 3.274 game entries/month (n=8); 2025-26 slope: 12.79 game entries/month (n=5); raw ratio 3.906.

- Confounders: Counts compatibility-page entries; 2026 cadence/name change and Wintermute batch caused a structural jump.

- Verdict: Strong 2026 acceleration, but mostly explained by release-cadence and engine batch additions.

### WPT Interop stable within-year gain

- Data: `data/wpt_interop_stable_within_year_slope_series.csv`; chart: `charts/wpt_interop_stable_within_year_slope.png`.

- Baseline slope: 31.42 score-points/month (n=3); 2025-26 slope: 39.56 score-points/month (n=2); raw ratio 1.259.

- Confounders: Official focus areas reset yearly; this averages per-year daily linear slopes for stable browsers; annual difficulty and browser staffing/funding changed.

- Verdict: Within-year Interop improvement accelerated in 2025, but 2026-to-date is lower and the reset/difficulty confound is large.

### Wine dev-release bugs fixed

- Data: `data/wine_cumulative_bugs_series.csv`; chart: `charts/wine_cumulative_bugs.png`.

- Baseline slope: 46.66 bugs/month (n=65); 2025-26 slope: 47.39 bugs/month (n=39); raw ratio 1.016.

- Confounders: Counts announced fixed bugs, not user-visible compatibility; release cadence changed slightly; excludes stable rollup notes.

- Verdict: Post-2025 bug-fix throughput is roughly similar/slower, not an acceleration.

### WebAIM avg errors/page

- Data: `data/webaim_avg_errors_series.csv`; chart: `charts/webaim_avg_errors.png`.

- Baseline slope: 0.250 errors/page/month (n=3); 2025-26 slope: 0.425 errors/page/month (n=2); raw ratio 1.700.

- Confounders: Annual sample; WAVE rules/site mix/page complexity changed; lower is better.

- Verdict: No positive break: errors worsened in 2025-26.

### WebAIM WCAG failure %

- Data: `data/webaim_wcag_failures_series.csv`; chart: `charts/webaim_wcag_failures.png`.

- Baseline slope: -0.037 percentage-points/month (n=3); 2025-26 slope: 0.092 percentage-points/month (n=2); raw ratio -2.444.

- Confounders: Annual sample; detectable failures only; lower is better; page complexity rose sharply.

- Verdict: No positive break: previous improvement reversed in 2026.

## Attempts and infeasible sources

- RPCS3: `rpcs3.net/compatibility` returned HTTP 403 from this environment; a guessed `history.json` URL returned 404. No data included.

- decomp.dev: site now serves a sunsetting page; `/projects.json` is 410 and `/api/projects` is 404. Existing individual project histories may still exist, but the public index needed to enumerate them is disabled.

- test262.fyi: current `index.json` and `meta.json` are public, but the page exposes no dated history endpoint; reconstructing history would require backend/archive work beyond this pass.

- GitHub emulator trackers: Xenia/Vita3K/shadPS4 were reconstructed from current labels plus issue creation dates because full issue timeline replay is API-expensive; this overstates early playable status if labels were applied later.

- ProtonDB: full monthly tarball processing was feasible but multi-GB; this pass sampled Jan/Apr/Jul/Oct dumps and used raw yes/no works verdicts, not the site tier algorithm.
- Not attempted in this pass: Valve Steam Deck Verified counts, Cemu/Ryujinx/Dolphin wiki history, Weblate/Fedora/GNOME/KDE translation histories, fan-translation successor databases, OpenMW/OpenRCT2 trackers, Servo/Ladybird full WPT pass-rate history. The reason was time/API surface area after completing the quantified series above; these remain good follow-ups.


## Anti-AI policy notes

I checked readily visible README/CONTRIBUTING files for the included emulator trackers, ScummVM, and Wine and did not find explicit AI-contribution bans. decomp.dev itself now warns that hostile AI forks and number-gaming damaged the decompilation community; that is a direct structural confounder. Known anti-AI policies in adjacent communities such as Dolphin/N64Recomp should be treated as suppressing within-project AI effects, but those projects are not included as quantified series here.


## Three-sentence bottom line

The strongest positive break is ProtonDB/Steam-compatibility and the young shadPS4 tracker, with ScummVM also jumping in 2026; these are real hard-progress meters, but each has obvious non-AI confounders (Steam Deck/Linux gaming, new emulator maturity, and batch engine additions). Mature hard-problem meters—Wine bug fixes, Xenia/Vita3K playable counts, WebAIM accessibility, and stable-browser Interop—do not show a clean 2025-26 acceleration over the 2022-24 slope. Overall, the data fit “AI may help some focused compatibility/decomp-style work, but broad hard software quality meters have not bent upward yet.”
