# Critique of the external AI research record (2026-10-14)

Source: `reports/external-ai-research-record.html`, another AI's "Where is all the new, good software?" research record. The user supplied it and asked for it to be incorporated critically.

How I checked it:
- Re-ran its three original computations: Show HN, F-Droid and Modrinth.
- Added stress tests of my own (new data in `data/hn_show_monthly.tsv`, `data/fdroid_*.tsv` and `data/modrinth_cohorts.tsv`).
- Had a research agent fetch all 22 cited sources.

## Verdict in one paragraph
The record is unusually careful. Its numbers check out. It separates "released" from "useful" from "improves lives". It flags most of its own confounders. Its weakness is the headline: it says the evidence supports "concrete useful improvements" as well as "a substantial expansion in attempts and releases". The release expansion is solid. The "useful" part rests on existence cases and vendor telemetry. When I applied quality thresholds to its own datasets, almost all of the growth disappeared at higher bars. A few cited sources also say something weaker than the record implies (details below). The record covers app/plugin supply and enterprise productivity, but says almost nothing about game studios, reliability or accessibility. It therefore complements our questions (b)–(d) rather than answering them.

## 1. Replication of its original computations
| Claim | My re-run | Status |
|---|---|---|
| Show HN Jan–Sep: 7,425 → 37,622 (2022→2026); Sep 2026 3,742 | Identical | ✅ Replicates |
| F-Droid first admissions (main ∪ archive) Jan–Sep: 329 / 386 / 1,155 (2024/25/26); union 6,935 | Identical | ✅ Replicates |
| Modrinth mods created Jan–Sep 2026: 30,669; 2025: 14,296 | 30,668 / 14,296 | ✅ Replicates |

## 2. Stress tests that change the interpretation
### Show HN: the raw volume grew, but the high-engagement count did not
Jan–Sep totals from the Algolia API, by points threshold (`data/hn_show_monthly.tsv`, `scripts/hn.py`):

| Year | All Show HN | ≥10 pts | ≥50 pts | ≥100 pts | Show HN share of all ≥100-pt stories |
|---|---|---|---|---|---|
| 2022 | 7,425 | 1,649 | 733 | 455 | 3.6% |
| 2024 | 12,916 | 2,160 | 994 | 631 | 5.8% |
| 2025 | 19,742 | 2,350 | 1,002 | 588 | 5.7% |
| 2026 | 37,622 | 3,045 | 1,104 | 613 | 5.1% |

**2025→2026 growth by threshold:**
- Raw posts: +91%.
- ≥10 points: +30%.
- ≥50 points: +10%.
- ≥100 points: +4%.

Front-page attention is finite, so the ≥100 count is partly fixed by design. But Show HN's *share* of high-scoring stories also fell. The doubling is almost entirely in posts that nobody upvoted. This is a direct example of "more software, not more good software".

The record also says all responses were exhaustive. But the Algolia index's *all-story* denominator jumps from ~25k a month to ~370k in some 2026 months (Jan–Mar, Jul, Sep). That is an indexing or spam artefact, and the record didn't check for it. Show HN counts appear unaffected, but the series is less clean than the record presents it.

### F-Droid: the rise is real, and demand rose even more than admissions
The record noted that F-Droid's new build server could explain faster listing. I counted merge requests to `fdroiddata` with "new app" in the title (`data/fdroiddata_newapp_mrs.tsv`):
- **Submissions:** ~45 a month in 2025, then 147 (Mar 2026), 291 (Jun) and **547 (Sep 2026)**, about 12×.
- **Admissions:** about 190 a month.

The infrastructure explanation therefore fails: submissions grew roughly 12×, which supports a real supply surge. It also shows a growing review backlog, with roughly a third admitted. That is the same bottleneck we saw at HACS and Obsidian. The record's spot check is consistent with this: 10 of 12 sampled source repos were created in 2026.

### Modrinth: the platform was already growing fast, and fewer new mods find users
Mods created Jan–Sep, surviving today, by lifetime downloads (`data/modrinth_cohorts.tsv`):

| Cohort | All | ≥1k | ≥10k | ≥100k |
|---|---|---|---|---|
| 2021 | 1,020 | 747 | 459 | 265 |
| 2023 | 5,669 | 4,525 | 2,664 | 1,298 |
| 2024 | 9,684 | 6,917 | 3,158 | 1,178 |
| 2025 | 14,296 | 7,643 | 2,905 | 844 |
| 2026 | 30,668 | 9,194 | 2,219 | 462 |

- **Pre-trend.** Modrinth grew 1.5–2.5× a year *before* agentic coding, as players migrated from CurseForge. The 2026 jump (2.1×) is only modestly above trend. The record mentions "platform growth" but doesn't show the pre-trend.
- **Mods with at least 1k downloads.** The 2026 cohort has had less time to collect downloads, yet it still has *more* of these (+20% vs 2025). That is the best "useful output grew" number in the record's datasets, though the bar is low. The share reaching 1k fell from 53% to 30%.
- **Higher bars.** At ≥10k and ≥100k, age dominates and no comparison is possible.

## 3. Source check: 22 citations
20 verified, 2 partly correct, 0 wrong. Corrections that matter:

1. **Demirer, Musolff & Yang: the "+30% releases" is mislabelled.**
   - The record calls it an "agent-era effect". The paper reports **no release effect for async agents**. The ~30% comes from autocomplete (+9%) plus sync assistants (+20%).
   - The paper's headline is that gains "translated only partially into shipped and used software", with an elasticity of 0.23.
   - Its app-store data shows new iOS apps roughly tripling (~33–45k a month to ~108k by Apr 2026) **while total usage stayed flat**.
   - Read correctly, the record's strongest causal source supports "more software, not more used software".
2. **Software investment (FRED) argues against acceleration.**
   - YoY growth was 11–14% in 2025–26. The 2019–22 CAGR was 12.97%, and 2022–25 was 7.71%. The recent pace just returns to the pre-AI trend after a 2023–24 slump.
   - The record lists this as a "macro cross-check" but never says it shows no break above trend.
3. **Steam ≥1,000-review games, 337 → 608.** The record cites this as "releases with an audience".
   - Zukowski, the source, **does not attribute it to AI**. He calls 2025 a possible "indie golden age" and singles out newly translated Chinese FMV games: 19 reached 1,000+ reviews.
   - The success *rate* fell from 2022 to 2024, then rose in 2025 (2.74% → 2.44% → 2.99%).
   - In the Q1 2026 data the extra volume sits at ≤50 reviews (+48%), while 1,000+ games went only 88 → 96. Zukowski's own word for that tail is "slop".
4. **Obsidian's doubling to 8,000 is mostly a process change.**
   - It followed automated review, a 2,300-item backlog being cleared, and near-instant approval.
   - The record flags this, but still uses the figure as evidence of growth.
5. **Apple acceleration is real but small.**
   - Available apps grew +10.8% in 2025, against +4.9% a year before.
   - Review submissions grew +17% against ~13%, and they include resubmissions.
   - The record gives 2025 figures without a prior-year denominator, which is the same error it criticises in the Replit stock figure.
6. **RevenueCat / Appfigures: 7× more subscription apps.**
   - Launches since 2025 earn **3%** of subscription revenue. Pre-2020 apps earn 69%.
   - The AI link is RevenueCat's own guess.
7. **The Chen & Stratton "+3.3% Jira issues" figure is derived, not stated.** The paper gives β = 0.12 on a 3.67 baseline, which isn't significant. Coding *assistants* (as opposed to agents) had no significant PR effect. This is consistent with our finding (a).
8. **Vendor items carry the same visual weight as administrative data in the register.** These are Lovable, Retool, Supabase, Replit and RevenueCat. Lovable's "720M visits" is self-reported and has no unique-user count. Retool's survey sample is its own customers, and 64% are managers.
9. **The Nexus "Mod of the Month" items are fine as existence cases.** Both are tagged AI-assisted. The winner is closed-source, and Effigy has 19 open bug reports.

## 4. Inferences I would not carry over
- **"Concrete useful improvements."** These are existence cases: Cobblemon Catch Rate Display, Effigy, Firefox security fixes. They are not a trend. The Firefox fixes are real, but they are AI *finding* bugs, which is our reliability (c) story, not new software.
- **"A falling success rate does not mean fewer successes."** This is true as arithmetic, but the record uses it to imply successes are rising. In its own sources, absolute counts above meaningful bars are roughly flat:
  - Show HN ≥100 points: +4%.
  - Steam 1,000+ reviews in Q1: 88 → 96, with no AI attribution.
  - Usage per Demirer: flat.
  - Revenue share for new apps: 3%.
  The only clear absolute gain is at low bars: Modrinth ≥1k downloads, Show HN ≥10 points.
- **Q1 vs Q2 non-AI Show HN (+139% vs +27%).** This volatility suggests a short burst in early 2026 (the Feb peak was 6,217), not a steady rise. The record notes it, but its pooled +79.5% half-year figure hides it.
- **Its points worth keeping:**
  - The "frontier models are largely outside the research windows" caveat is valid and important. Opus 5 has had about 12 weeks and Astra about 6. Our own data runs through Sep 2026, so it partly covers them.
  - Its proposed "next study" design is good: cohort follow-up at 90, 180 and 365 days, absolute counts at several audience thresholds, and incumbent-product panels.

## 5. What this adds to our answer
| Our question | What the record adds (after critique) |
|---|---|
| (a) Features | Corroborates our finding. Chen & Stratton: PRs +23%, resolved issues not significant. CircleCI: main branch flat. He et al.: PRs ×1.5–2 under a mandate, merge and revert rates flat. Demirer: commits +240% → releases about +30% (pre-agent tools), usage flat. |
| (b) Games | Little on studios. Steam has more games with an audience in 2025, attributed to an indie and Chinese-translation boom, not AI. |
| (c) Reliability | Only the Firefox bug-finding wave, which we already have. |
| (d) Niche | Adds more ecosystems that show a large rise in *supply*: F-Droid ~3× admissions and ~12× submissions, Modrinth 2×, Show HN 2×, iOS apps ~3× (Demirer). In each case the extra supply is concentrated in low-engagement entries. |

**Net effect on our conclusion.** The record strengthens "lots more software exists" and widens it from niche registries to general app and plugin stores. Read critically, it also strengthens "but not much more software that people use". In every dataset where I could apply a quality bar, the count above the bar barely moved: Show HN, Steam, Modrinth, Demirer usage and RevenueCat revenue share.

**Addendum (2026-10-16): Modrinth ≥1k split by AI disclosure.** Re-queried: 2026 Jan–Sep cohort ≥1k = 9,333 (vs 7,651 for 2025, 6,920 for 2024). AI-code-disclosed mods: 2,565 listed, 884 ≥1k (34% hit rate, similar to the 30% overall). Excluding them, non-AI ≥1k is 8,449 vs 7,484 (+13%). The cohort-on-cohort increase in ≥1k mods (+22%) exceeds 2025's (+10%) despite the 2026 cohort being younger, so this counts as a weak yes for more modestly used mods. Caveats: lifetime downloads (age favours older cohorts, so this understates 2026), Modrinth's own user growth is not normalised, and disclosure is self-reported.
