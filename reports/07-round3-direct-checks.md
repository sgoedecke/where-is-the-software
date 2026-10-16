# Round 3: direct checks on whether "good" software has increased (2026-10-15)

These checks follow the "investigator" approach: look straight at survival, use, and progress on hard problems, rather than at volume. There are four checks. Each has its own folder with data, scripts and a REPORT.md:
- `followup-audit/`
- `stalled-projects/`
- `progress-meters/`
- `usage-cohorts/`

## Headline
**All four point the same way.** Across measures of durable or hard-won software, there is no broad break from trend after 2025:
- Projects survive at the same rate.
- Old problems are not getting fixed faster.
- Hard-progress meters are flat or worse.

The one place where *used* new software clearly increased is developer tooling on Homebrew. When I inspected it by hand, about half of the genuinely new, widely-installed tools are themselves AI-agent tooling.

## 1. Do "I built this with AI" projects survive? (`followup-audit/`)
Samples: 200 Show HN posts that mention AI-assisted building (Oct 2025–Apr 2026), 200 non-mentioning posts from the same window, and 200 from 2022–23.

| Cohort | Alive now | Maintained (push in last 90 days) | External-user signal |
|---|---|---|---|
| AI-build mention | 81.5% | 11.0% | 27.5% |
| No mention, same window | 84.5% | 7.5% | 15.5% |
| 2022–23 baseline (alive now) | 69.0% | 4.5% | 27.0% |

- AI-built projects are about as durable as their peers. Both groups are mostly abandoned within a year: only 7–11% are still maintained.
- The higher external-user signal in the AI group is confounded. About 80% of that group are AI products, which attract early GitHub interest.
- The baseline checked at the same age (16.5% alive) relies on Wayback Machine coverage and isn't reliable, so I discard it.
- The alive/dead classifier agreed with my hand check on 20 of 20 items.

## 2. Are long-stuck problems getting unstuck? (`stalled-projects/`)
- **Old GitHub issues.** In 15 big repos, issues closed as completed when they were 3 or more years old went from 4.6% of completed closures (2022–24) to 6.0% (2025–26 Q3). But the count sits exactly on the 2022–24 linear trend, with a bump only in 2026 Q3. This could be the earliest sign of Opus 5/Astra and is worth rechecking in 6 months.
- **Firefox.** Bugs that were 5 or more years old when fixed *fell* as a share of fixes, from 2.7% to 1.7%. The flood of AI-found security bugs dilutes the share.
- **Top-voted feature requests.** The rate at which they get resolved is flat: 7–8% a year, below 2022–23.
- **Pre-registered list of 36 famous stalled projects.**
  - Major milestones: 10 projects in Apr 2023–Dec 2024, versus only 4 in Jan 2025–Oct 2026.
  - The 2025–26 wins are GIMP 3.0, fish 4.0, Servo and Brawlback. GIMP 3.0 and fish 4.0 were years of work that predates agents. Only Brawlback is plausibly AI-driven.
  - Caveat: the list was built from famous *old* stalls. It misses the new hobbyist reverse-engineering scene, where report 02 found the action is.

## 3. Published progress meters (`progress-meters/`)
| Series | 2025–26 slope ÷ 2022–24 slope | Read |
|---|---|---|
| ProtonDB "works" share | 0.63 | Slower |
| ProtonDB apps tested | 1.17 | Slightly up |
| Xenia playable | 0 | Flat |
| Vita3K playable | 0.75 | Slower |
| shadPS4 playable | n/a (was 0) | Up, but the project is young |
| ScummVM supported games | 3.9 | Up, but games are added in batches |
| WPT Interop | 1.26 | Modest; scores reset each year |
| Wine bugs fixed per release | 1.02 | Flat |
| WebAIM errors per page | 1.70 | **Accessibility getting worse, faster** |

There is no broad acceleration. Mature meters are flat. The web is getting *less* accessible, which pushes against our niche finding (d): blind users are building their own tools, but the mainstream web isn't improving for them.

## 4. Count only what people use (`usage-cohorts/`)
| Ecosystem | Metric (per quarterly cohort) | 2022–24 | 2025 | 2026 H1 |
|---|---|---|---|---|
| Homebrew formulae | ≥1k installs in 30 days, at equal age | 10.7 | 23.2 | 31.0 |
| Homebrew formulae | ≥10k, at equal age | 2.6 | 5.0 | 7.0 |
| crates.io | ≥1k downloads in 90 days | 1,287 | 1,833 | 4,649 (inflated by bots and CI) |
| VS Code Marketplace | ≥10k installs | 157 | 81 | 60 (age-confounded) |

**What is driving the Homebrew rise?** I checked by hand. I listed formulae that had ≥1k installs in the last 30 days and were absent from Homebrew's Dec 2024 formula list. There are 141:
- **84 (60%)** are library versions, splits or dependencies: python@3.14, openssl@4, about 35 Qt module splits, sdl3 and so on.
- **29 (21%)** are AI or agent tooling: opencode, gemini-cli, qwen-code, pi-coding-agent, goose, beads, ccusage, openspec, MCP servers, whisper.cpp, ggml, mlx-c and similar.
- **28 (20%)** are other tools. About half of these are established tools migrating into Homebrew core: bun, vercel, wrangler, supabase, ghidra, powershell.
- Checking each project's creation date shows that only **9** are genuinely new (created Oct 2024 or later) and not AI-related:
  - mole (Mac cleaner, Sep 2025, about 70k stars)
  - Apple `container` (May 2025)
  - ty (Astral's Python type checker, 2025)
  - prek (pre-commit replacement, Oct 2024)
  - fresh-editor (Dec 2024)
  - tuios (Sep 2025)
  - bbrew (Jan 2025)
  - betterleaks (Feb 2026)
  - git-pkgs (Jan 2026)
- 3 more are new but built for AI agents:
  - gogcli (from the OpenClaw org)
  - asc (from Rork, an AI app builder)
  - hunk ("diff viewer for agent-authored changesets")
- The rest predate 2024 and were only added to Homebrew core recently: bun, ghidra, powershell, tree-sitter, lazysql, xan, swiftly, fvm, otel-cli, mermaid-cli, supabase, vercel, wrangler, snowflake-cli, grafana-alloy and git-format-staged.

So the clearest "more *used* new software" signal is mostly **software for using AI to write software**.

**Follow-up: counting only installs that users explicitly asked for.** Homebrew's `install-on-request` analytics exclude installs pulled in as dependencies. I re-dated every formula from homebrew-core git history and kept only Jan–Sep cohorts (`usage-cohorts/data/homebrew_formula_onrequest_by_name.csv`):

| Cohort (Jan–Sep) | Added (still in core) | Unversioned, ≥1k on-request installs/30d | Dependency-driven, ≥1k installs |
|---|---|---|---|
| 2020 | 382 | 23 | 30 |
| 2021 | 389 | 34 | 19 |
| 2022 | 408 | 23 | 10 |
| 2023 | 457 | 28 | 10 |
| 2024 | 362 | 13 | 6 |
| 2025 | 738 | 22 | 20 (12 are Qt-split or versioned) |
| 2026 | 663 | 29 | 15 (6 are Qt-split or versioned) |

- **Additions roughly doubled in 2025–26, but formulae that users choose to install did not.** Requested new formulae are within the 2020–23 range, even though older cohorts have had longer to build an audience.
- **The bump in dependency libraries is packaging work, not new software.**
  - Homebrew split monolithic Qt 6 into about 15 module formulae (Sep 2025).
  - It unbundled Node.js's vendored dependencies (uvwasi, llhttp, nbytes, merve, hdrhistogram_c).
  - New LLVM and ICU versions were added.
  - Even this is within the historical range: 2020 had 30 such additions.
- **The requested lists are dominated by AI tooling.** That covers 9 of 22 in 2025 and about 16–19 of 29 in 2026: opencode, gemini-cli, qwen-code, pi-coding-agent, rtk, herdr, beads, openspec, ccusage, MCP servers and so on.
- **Correction to the usage-cohorts agent.** Its "Homebrew above trend" verdict used total installs, which count dependency pulls. On a user-requested basis there is no trend break. That fits the pattern elsewhere: in RevenueCat's data, AI tools are the main new category that people actually pay for.

## Combined interpretation
1. **Supply has exploded** (rounds 1–2): registries are up 2–12× and app launches are up about 3×.
2. **Survival and use have not kept pace** (round 3). Per-project survival is unchanged, so the *absolute* count of surviving projects has grown with volume. But counts above meaningful usage bars are roughly flat, except for AI tooling and low-bar tiers.
3. **Hard problems are not being solved faster in general.** The exceptions are specific hobbyist breakthroughs: Brawlback, decomps and recomps, shadPS4.
4. **Timing caveat.** Opus 5 (Jul 2026) and Astra (Sep 2026) are only 6–12 weeks old. The 2026 Q3 uptick in old-issue closures and the Sep 2026 surges in Raycast and F-Droid could be the start of something. These checks should be re-run in Q2 2027. The scripts are in place for that.
