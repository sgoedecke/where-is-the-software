## Context
We are investigating, with evidence rather than speculation, "if AI coding is so great, where is all the new good software?" (Nate Meyvis, Oct 2026). Today is 2026-10-15.

Our finding so far is that in niche ecosystems where builders are also users (NVDA add-ons, Home Assistant/HACS, Obsidian plugins, Firefox add-ons), AI-era supply growth (2025–26) produced **2–10× more new tools reaching modest real usage**, with **no more big hits** apart from AI-agent tooling. WordPress, CRAN and OctoPrint did not show this. We are testing whether the pattern generalises to more ecosystems.

AI coding timeline:
- Claude Code: Feb/May 2025.
- Agentic coding mainstream: H2 2025.
- Opus 4.5: Nov 2025.
- Opus 5: Jul 2026.
- Newest models: Sep 2026, too recent to show up.

## Method requirements
- **Cohorts.** Group items by the date first listed in the registry, using half-years (or quarters if the data supports it), from 2021 or as early as available. Report supply, i.e. the count listed per cohort. Where possible, also report submission or queue counts.
- **Usage thresholds.** Count items per cohort clearing low, modest and high usage thresholds that suit the ecosystem's scale, e.g. ≥100, ≥1k, ≥10k installs or downloads.
- **Equal age.** Prefer equal-age usage: usage at a fixed age after listing (e.g. 90 or 180 days). Get it from historical stats, git history of stats files, or Wayback snapshots (`https://web.archive.org/web/<timestamp>id_/<url>`; CDX API at `web.archive.org/cdx/search/cdx`; snapshots may be gzipped, so check for magic bytes 1f8b). If you can only get current usage, say so clearly: it favours older cohorts, so a recent cohort beating older ones is strong evidence and one trailing them is weak evidence.
- **Platform growth.** Correct or at least note it, e.g. by scaling thresholds by total ecosystem installs.
- **Backlog check.** For the top ~20–50 recent items, note what they are and whether they are AI or agent tooling. Check whether they are genuinely new projects (GitHub repo creation date) or old projects newly listed.
- **Confounders.** Note registry launches, policy or review changes, platform user-base changes and survivorship (removed items missing). Use web search where helpful.
- **Scope.** Be pragmatic: if the full data is huge, sample sensibly and say so. Aim to finish within about 40 minutes of work.
- **Tools.** `gh` CLI is authenticated; Python 3 is available.

## Output rules
- Write **only** inside your assigned absolute output directory.
- Do **not** use /tmp, the current working directory, or any other location.
- Do not modify any other repos under ~/Code.
- Put scripts in `scripts/`, derived CSVs in `data/` and raw caches in `cache/`.
- Write `REPORT.md` with: source and method, cohort table, top recent items, confounders, and a 3-sentence verdict on whether the ecosystem shows (i) more supply, (ii) more modestly used new tools, (iii) more big hits.
- Your final reply should be short: a compact cohort table plus a one-line verdict.
