# Are long-stuck problems getting unstuck faster?

Date: 2026-10-15. Outputs in this folder were produced after writing `prereg_list.md`; scripts are in `scripts/`, raw/derived CSVs in `data/`.

## Files produced

- `prereg_list.md` — 40 candidate stalled projects/features, written before status lookups.
- `scripts/collect_github_issue_closures.py` — GitHub Search API collector using `reason:completed` and quarterly buckets.
- `scripts/collect_bugzilla.py` — Mozilla Bugzilla REST collector.
- `scripts/analyze_results.py` — aggregation/trend-break summaries.
- Main data: `data/github_old_issue_closures_quarterly.csv`, `data/github_top_reacted_issues.csv`, `data/github_top_reacted_hazard.csv`, `data/mozilla_bugzilla_fixed_quarterly.csv`, `data/qualitative_stalled_projects.csv`.

## Method summary

GitHub: I counted issues closed `reason:completed` in 15 large long-lived repos, quarterly from 2022Q1 through 2026Q3. "Old" means created before the quarter start minus three years, so quarterly counts are conservative for issues that crossed the three-year mark mid-quarter. I used `react/react`, the current repository name for the former `facebook/react`. I did not reconstruct historical open old-issue stock because GitHub search exposes current state easily but not a cheap, reliable historical open-at-date denominator.

Mozilla: I counted Bugzilla bugs in Core, Firefox, and Toolkit resolved `FIXED`, with "old" defined as created before quarter start minus five years. 2026 security-sensitive bugs may be hidden, so Mozilla 2026 counts are lower-bound-ish for some classes of fixes.

Qualitative: I used the pre-registered list, then filled a structured CSV from project release pages/blogs/GitHub releases. The milestone flag is conservative: it counts the originally famous stuck target, not merely ordinary release cadence.

## Part A: old-issue closure rates

### GitHub aggregate trend

Across the 15 repos, completed closures of issues older than 3 years did **not** show a clear positive break after agentic coding went mainstream.

| period | old completed | all completed | old share | notes |
|---|---:|---:|---:|---|
| 2022-2024 baseline | 7,172 | 154,640 | 4.64% | baseline period |
| 2025-2026Q2 | 3,283 | 66,860 | 4.91% | essentially baseline-like |
| 2026Q3 | 1,425 | 11,668 | 12.21% | broad late spike, not a single detected mass cleanup |
| 2025-2026Q3 total | 4,708 | 78,528 | 6.00% | higher than baseline average, but driven by 2026Q3 |

Baseline 2022-2024 linear trend in old-issue closures was +7.9 old closures/quarter. Extrapolating that trend into 2025-2026Q3 predicts 4,708.2 old closures; observed was 4,708, i.e. **0.0% below/above the baseline-count trend**. The old-share trend is different: the 2022-2024 old-share slope was already rising, and observed 2025-2026Q3 old-share sum was **16.8% below** that extrapolated share trend despite being above the simple baseline average.

The only notable spike is 2026Q3. Spot checks in `github_old_issue_spotcheck.csv` show many real bugs/features with fix/verified labels (VS Code, Rust, Flutter, TypeScript, CPython), but also some labels like Go `FrozenDueToAge` and Electron `stale`, so `reason:completed` is not a perfect real-fix filter. A daily spike check (`github_2026q3_daily_spike_check.csv`) found no one-day 100+ old-issue cleanup; the largest daily clusters were Go (61 on 2026-08-20) and TypeScript (31 on 2026-09-08).

### GitHub by repo

| repo | 2022-24 old/all | 2025-Q3 2026 old/all | share change pp |
|---|---:|---:|---:|
| ansible/ansible | 358/2951 (12.1%) | 68/657 (10.4%) | -1.8 |
| bevyengine/bevy | 27/2977 (0.9%) | 71/1682 (4.2%) | +3.3 |
| electron/electron | 62/1902 (3.3%) | 104/879 (11.8%) | +8.6 |
| flutter/flutter | 1281/27848 (4.6%) | 846/10792 (7.8%) | +3.2 |
| godotengine/godot | 639/14448 (4.4%) | 454/5871 (7.7%) | +3.3 |
| golang/go | 649/10519 (6.2%) | 569/4823 (11.8%) | +5.6 |
| home-assistant/core | 11/17948 (0.1%) | 13/10328 (0.1%) | +0.1 |
| kubernetes/kubernetes | 218/5364 (4.1%) | 151/2474 (6.1%) | +2.0 |
| microsoft/TypeScript | 702/6740 (10.4%) | 434/1245 (34.9%) | +24.4 |
| microsoft/vscode | 445/37716 (1.2%) | 263/24900 (1.1%) | -0.1 |
| neovim/neovim | 200/3334 (6.0%) | 155/1847 (8.4%) | +2.4 |
| nodejs/node | 181/2985 (6.1%) | 138/1584 (8.7%) | +2.6 |
| python/cpython | 1148/8761 (13.1%) | 665/5222 (12.7%) | -0.4 |
| react/react | 35/1259 (2.8%) | 21/651 (3.2%) | +0.4 |
| rust-lang/rust | 1216/9888 (12.3%) | 756/5573 (13.6%) | +1.3 |

Interpretation: there are repo-specific increases, especially TypeScript, Electron, Go, Flutter, Godot, and Bevy, but the aggregate increase is not a clean post-H2-2025 break. VS Code, CPython, and Ansible are flat/down; Home Assistant has too few old completed closures to matter. TypeScript's high post share is partly a denominator effect: total completed closures fell sharply.

### Mozilla Bugzilla

| period | old FIXED bugs (created >=5y before quarter) | all FIXED | old share |
|---|---:|---:|---:|
| 2022-2024 | 1,306 | 48,151 | 2.71% |
| 2025-2026Q3 | 690 | 41,409 | 1.67% |

Mozilla is the clearest negative result: all FIXED volume rose in 2025-2026, but old-bug FIXED share fell materially. This is not evidence that long-stuck Mozilla bugs started clearing faster.

### Top-reacted issues hazard

For the current top 50 `+1`-reacted issues in VS Code, Rust, Go, Godot, Flutter, and Home Assistant, I measured how many issues still open/unresolved at the start of each year were closed `completed` during that year.

| year | at-risk top issues | closed completed | hazard |
|---|---:|---:|---:|
| 2022 | 140 | 13 | 9.3% |
| 2023 | 139 | 18 | 12.9% |
| 2024 | 128 | 8 | 6.3% |
| 2025 | 123 | 9 | 7.3% |
| 2026 YTD | 123 | 10 | 8.1% |

There is no obvious post-2025 jump in resolving top-voted requests. Rust and Home Assistant improved in 2026, but VS Code, Go, Godot, and Flutter did not in this current-top-50 sample. This measure is selection-biased because it sorts by reactions as of 2026, not as of each historical year.

## Part B: famous stalled projects

I pre-registered 40 candidates and coded 36 in `qualitative_stalled_projects.csv`. Conservative milestone counts:

| window | projects with major target/target-adjacent milestone | fraction of coded list |
|---|---:|---:|
| Apr 2023-Dec 2024 | 10/36 | 27.8% |
| Jan 2025-Oct 2026 | 4/36 | 11.1% |

Post-2025 clear wins were GIMP 3.0/non-destructive filters (Mar 2025), fish 4.0 Rust port (Feb 2025), Servo's concrete versioned releases/revival continuing into 2026, and Brawlback working/playable in Oct 2026 (the Brawlback AI credit is from the prior/user-supplied investigation and should be independently cited before publication). Several important milestones happened **before** the agentic-coding period: Bun 1.0 (Sep 2023), Deno 2.0 (Oct 2024), PCSX2 2.0 (Jul 2024), KDE Plasma 6 HDR (Feb 2024), Inkscape 1.3/1.4-era features, Thunderbird Android, and Zelda64Recomp/MM-era N64 work.

Notable non-unlocks by the original target definition: ReactOS still has no 0.5; OpenMW still has no 1.0 despite 0.50/0.51; Zig still has no 1.0; Asahi's official Fedora page still lists M1/M2 support rather than M3/M4; Linux Rust GPU drivers are not ordinary-user-ready; OpenRA's Tiberian Sun-style target is not a stable mainstream release; Wind Waker/Twilight Princess/Melee decomp/recomp targets remain incomplete.

I found little explicit maintainer AI credit in official release notes/blogs. Most major wins look like long-running human-maintainer roadmaps finally landing, not public AI-driven breakthroughs. Brawlback is the standout possible AI-agent-assisted hobbyist reversal, but it is one case, not a population-level pattern.

## Caveats

- Quarterly old-issue threshold is approximate and conservative; an issue created mid-quarter exactly three years earlier may be missed until the next quarter.
- `reason:completed` removes `not_planned`, but not every completed closure is a code fix; some stale/age labels remain. I therefore spot-checked samples and spike days, but did not manually classify all 11,880 old GitHub closures.
- GitHub issue practices differ dramatically by repo: some use issues as support queues, some use tracking issues, some close via PR automation, and some migrated repositories.
- Current top-reacted issue samples are hindsight-biased.
- The qualitative list is intentionally famous-project-biased and contains selection effects in both directions: it overrepresents memorable hard targets, and milestone coding is necessarily judgmental.
- Public AI-credit evidence is sparse; absence of public credit is not evidence of absence of AI use.

## 3-sentence bottom line

I do not find strong evidence that long-stuck problems began getting unstuck faster after agentic coding went mainstream: GitHub old-issue closures are almost exactly on the 2022-2024 count trend, Mozilla old FIXED bugs fell as a share of all fixes, and top-voted issue hazard is flat. There are real post-2025 wins, especially GIMP 3.0, fish 4.0, Servo, and Brawlback, but the pre-registered famous-project list has fewer major milestones in Jan 2025-Oct 2026 than in the previous 21 months. The best reading is "some hobbyist/specialist breakthroughs, no broad quantitative break yet."
