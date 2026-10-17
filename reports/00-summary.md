# Summary: where is all the new good software? (as of 2026-10-15)

Prompt: Nate Meyvis, https://www.natemeyvis.com/where-is-all-the-new-good-software/ (12 Oct 2026).
Detail: reports 01–06 (06 = critical review of an external AI research record, which also adds F-Droid/Modrinth/Show HN/app-store data). Own data collection: `data/`, `scripts/`. Literature: `05-literature-review-raw.md`.

> ⭐ **Most interesting result so far (reports 08–10).** We checked usage, not just supply, in 17 ecosystems: 13 niche (incl. Modrinth from report 06) plus Steam, Google Play, Chrome Web Store and Atlassian (report 10).
>
> **Report 10:**
> - Chrome looks like Firefox: more modestly used extensions.
> - Steam has more modest successes, but only in proportion to supply. Its big hits are flat since 2024 (full count).
> - Atlassian (B2B) has no more used apps.
> - Google Play saw no AI-era surge, because its developer-testing rule acts as a gate.
>
> **Niche rounds:** The four added last (Flathub, Decky Loader, Raycast, Blender) are mostly weak, flat or inconclusive. They do show submissions up 3–5× while listings rise much less, because human reviewers absorb the surge. Across the first eight:
> - **Where builders are also users** (NVDA, Home Assistant/HACS, Obsidian, Firefox add-ons, and weakly Nexus mods), AI-era supply growth has produced **2–10× more new tools that get modest real use** (hundreds to a few thousand users).
> - **No ecosystem shows more new big hits** (now 17/17), apart from AI-agent tooling itself.
> - **Professional, saturated or declining ecosystems** (WordPress, CRAN, OctoPrint) show more listings but no more used tools.
> - **Review queues may now limit some registries.** Obsidian's jump coincided with it ending manual review, and HACS and F-Droid have big submission backlogs.
>
> This is the best evidence-based answer to "where is the software": much of it is small, used, and invisible outside niche registries. That holds in about half the niches we checked, not all of them.

## One-paragraph answer
The new software is real, but it isn't where people look for it. It shows up in three places:
1. **Long-tail and niche communities**, where people who couldn't build tools before now can. NVDA add-ons are up ~4×, Home Assistant integrations 6×, ham-radio repos ~6×.
2. **Hobbyist reverse-engineering of old games.** Unofficial ports are up ~10–20×. Projects stuck for years are being finished in weeks: Brawl rollback, MW2 decomp, first native Switch and PS4 ports.
3. **More code churn inside companies.** Companies are producing more code (PR volume up a lot, about half of commits AI-co-authored at some orgs), but only ~0–27% more delivered features.

It does **not** show up in:
- Reliability. Flat for normal services; much worse for AI-traffic-hit ones.
- Announced product features (AWS What's New is flat).
- Studio-side ports, remasters or patches of old games. Flat except for the Switch 2 launch.

## Scorecard
| Question | Verdict | Strongest evidence |
|---|---|---|
| (a) More features from tech companies? | **More code, modestly more delivery** | Own data: merged human PRs up 1.4–2× in big OSS company repos, but mostly from more contributors (+10–40%/author); AWS announcements flat. Literature: CircleCI main-branch throughput −7% (median team); DX +5–15%; Jellyfish 2× PRs but +27% epics; Faros no org-level DORA change; Answer.AI PyPI release cadence unchanged. |
| (b) Games doing more hard technical work? | **Studios no; hobbyists yes, dramatically** | Studios: Steam patch share of old games flat (~19%); dormant-revival flat; Gematsu port headlines (ex-Switch 2) down; remasters flat. Hobbyists: DSOGaming port articles 0–2/mo → 21–22/mo; recomp repos 41 → 617/mo; decomp.dev projects 38 → 145; Xbox's Oct 13 memo acknowledges this. Brawlback (the long-running Brawl rollback project) went from "ETA: NONE" to working rollback within days of merging AI-agent-built snapshot code from Orca (see 03). |
| (c) More reliable? | **No.** Flat for normal SaaS; worse for AI-load services | Own: ~30 status pages median index 1.00 (major 1.09); GitHub 2–4×, Claude 7×. Uptime Institute: outages still slowly declining (pre-existing trend). Mobile crash-free sessions flat 99.95%. CircleCI main-branch success 70.8% (5-yr low). CVEs +50% but driven by AI *finding* bugs (Firefox security bugs ~5×). |
| (d) Niche communities? | **Yes. Clearest signal** (but the extra supply is mostly low-engagement. More modestly used tools in NVDA, HACS, Obsidian and Firefox add-ons; not in WordPress, CRAN or OctoPrint; no more big hits anywhere except AI tooling; see 08/09) | NVDA add-ons ~6/mo → ~27/mo; NVDA-related repos 56 → 632; Double Tap (blind tech podcast) vibe-coding episodes 1 → 44; HACS +101 (2024) → +1,367 (2026 YTD) with a 1,953-PR backlog; Raycast 2×; amateur-radio repos 103 → 592. Also fan translations of never-localized games. |

## Quality-threshold check (added after reviewing the external report, see 06)
Wherever a quality bar can be applied, the count *above* the bar barely moves while raw counts double or more:

| Dataset | Raw growth | Above a bar |
|---|---|---|
| Show HN, Jan–Sep 2025→26 | +91% | ≥10 pts +30%; ≥100 pts +4% |
| F-Droid | admissions 3×, "new app" MRs ~12× | n/a (too recent) |
| Modrinth mods, 2025→26 cohort | 2.1× (pre-trend 1.5–2.5×/yr) | ≥1k downloads +20% despite less time (+13% excl. AI-disclosed; recheck 2026-10-16: 9,333 vs 7,651); share 53%→30% |
| Steam Q1 2024→26 (Zukowski) | ≤50 reviews +48% | 1,000+ reviews 88→96 |
| iOS (Demirer et al.) | new apps ~3× | total usage flat |
| Subscription apps (RevenueCat) | 7× launches | 2025+ apps = 3% of revenue |
| Software investment (BEA) | +11–14% YoY | = 2019–22 trend, no break |

## Round 3: direct checks of whether more *good* software exists (see 07)
- **Survival.** AI-built Show HN projects survive like their peers: 82% alive vs 84%, but only 7–11% are still maintained after 6–12 months.
- **Stalled problems.** Old-issue closures in 15 big repos are on their pre-AI trend. Firefox old-bug fixes are down as a share of fixes. Major milestones on a pre-registered list of 36 famous stalled projects: 4 in 2025–26 vs 10 in 2023–24.
- **Progress meters** (ProtonDB, emulators, Wine, Interop): flat. WebAIM accessibility errors are getting worse faster.
- **Usage.** Counting only installs users explicitly request, new Homebrew formulae with ≥1k installs are within the 2020–23 range: 22 (2025) and 29 (2026) vs 13–34 before. The apparent jump in total installs came from packaging work (the Qt 6 split, unbundling Node's dependencies). The new requested tools are mostly AI and agent tooling; only about 9 are genuinely new non-AI tools. VS Code: fewer new extensions reaching 10k installs. crates.io: up, but inflated by bots and CI.

## Niche usage check (see 08)
- **NVDA add-ons with ≥1k early downloads:** about 18–34 per half-year → 78 in 2026 H1, the clearest rise in *used* new software we found. Add-ons with ≥10k are flat.
- **HACS integrations with ~100+ installs at equal age:** about 2.3× (adjusted for user-base growth). Integrations with ~1,000+ are flat.
- **Pattern:** many more lightly-used tools for small audiences, but no more big hits.

## Niche usage round 2 (see 09)
Six more ecosystems, measured by usage:
- **Supply:** up 1.6–20× everywhere except OctoPrint.
- **High-usage new tools:** flat or down in all 8 ecosystems. Obsidian is the slight exception, and its new hits are mostly AI-agent plugins.
- **Modestly used new tools:** up in personal-customisation ecosystems:
  - Obsidian ~5–10×, confounded by its May 2026 switch away from manual review
  - Firefox add-ons with ≥10 users 2.5× (≥100 users 1.7×)
  - Nexus code mods slightly up
- **Not up** in WordPress (flat), CRAN (down) or OctoPrint (a declining platform).
- **Gatekeeping:** registry review capacity (HACS backlog, F-Droid, Obsidian's pre-May queue) looks like a real constraint.
- **Round 3 (Flathub, Decky Loader, Raycast, Blender):**
  - Blender is weakly up. Flathub is flat after adjusting for ecosystem growth. Decky shows no increase. Raycast is **inconclusive**: at the revised ≥100-download modest bar, 222.33/HY (2022–24 mean) → 197 (2026H1), −11% observed, excluding partial 2026H2. Current cumulative downloads give older cohorts years and recent ones months; the lower bar does not fix age comparability, establish a true decline or prove AI causation (≥100k high bar unchanged).
  - No new big hits beyond AI tooling.
  - Submissions are surging 3–5× while listings rise ~30% to 2×, because reviewers absorb the flood.

## Mapping to Nate's hypotheses
| # | Hypothesis | Evidence |
|---|---|---|
| 1 | Fewer bugs and better performance | **Against.** Reliability is flat or worse. |
| 2 | More features in existing products | **Weak.** Delivery is up ~0–27%; the gains are concentrated in the top teams and in migrations. |
| 3 | Few people adopt new software | Untested directly. |
| 4 | Non-coding bottlenecks | **Supported.** AI PRs wait 4.6× longer for review (LinearB); review time is up 91% (Faros); registry review backlogs (HACS, Obsidian). |
| 5 | More ephemeral software | Untested. |
| 6 | Private and bespoke software | **Partially supported.** Niche and personal tools are surging, but much of it *is* public, just in long-tail registries nobody browses. |
| 7 | More software rather than better software | **Strongly supported.** Volume is up a lot, quality metrics are not, and counts above engagement thresholds are roughly flat (see quality-threshold table). |
| 8 | Gains taken as leisure | Untested. Per-author PR output is only up 10–40%, which is consistent with this. |
| 9 | Less software use | Untested. |

Two additions not on Nate's list:
- **Legal and organisational friction redirects the work.** The hardest and most impressive AI-enabled work (ports, decomps, emulators) is happening in hobbyist and legally grey spaces that publishers take down: Bethesda, Activision, Take-Two.
- **Communities resist AI-made work.** Dolphin, N64Recomp, Codeberg, Zelda/Banjo Recompiled and Panic are all refusing it.

## Biggest caveats
- Pull requests aren't features.
- Status-page reporting practices vary.
- The Steam sample covers only popular games.
- Keyword counts are noisy.
- Studio announcements lag development by 1–3 years, so a mid-2026 shift at studios would not be visible yet.
- Much of the literature is vendor telemetry.
- Search engines and Reddit were blocked for the research agents.
