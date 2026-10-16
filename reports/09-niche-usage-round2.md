# 09: Does "more small tools that people actually use" hold beyond NVDA and HACS? (2026-10-15)

Report 08 found that NVDA and HACS have 2–4× more *modestly used* new tools, with no more big hits. This round tests whether that generalises to six more ecosystems. Each was measured by usage, not just listings. Detail, data and scripts are in `niche-usage/<source>/REPORT.md`.

Baseline is 2022–24, compared with 2025H2–2026 unless noted. "Equal-age" means usage measured at the same age since listing. "Current" means today's usage, which favours older cohorts: recent cohorts *beating* old ones is strong evidence, while recent cohorts trailing is weak evidence.

## Cross-ecosystem table

| Ecosystem | Supply growth | Low/modest usage bar | High bar | Measure | Verdict |
|---|---|---|---|---|---|
| NVDA add-ons (08) | ~4× | ≥1k downloads in 180d: 18–34/HY → 78 | ≥10k flat (~2) | equal-age | **Yes** |
| HACS (08) | 5–6× | ~≥100 installs: ~19 → ~45/qtr (scaled for user base) | ≥1k flat | equal-age | **Yes** |
| **Obsidian plugins** | listings ~20× after 2026-05-15 policy change | ≥3k downloads in 60d (≈1k pre-growth): 4–14/qtr → 102 (2026Q2) and 35 (partial Q3) | ≥30k: 0–2 → 4 and 2 (mostly AI-agent plugins) | equal-age, scaled for 3.3× ecosystem growth | **Yes, strongly, but confounded** |
| **Firefox add-ons (AMO)** | 4.8× | ADU ≥10: 2.5×; ADU ≥100: 1.7× | ≥1k flat; ≥10k down (~17 → 4–9/HY) | current | **Yes** |
| **Nexus Mods** (code/tool mods, 5 games) | 1.6× | ≥100 downloads: +23% (4,637 → 5,685/HY) | ≥1k and ≥10k down | current | **Weak yes** |
| **WordPress plugins** | 2.5–5.4× (1,390 → 3,449 → 7,533/HY) | ≥100 active installs flat (~380 → 409, 358) | ≥1k down (124 → 79, 54); ≥10k down (25 → 14, 22) | current | **No (inconclusive at low bar)** |
| **CRAN packages** | ~2× in 2026H1 only | ≥2k downloads, equal-age, mirror-normalised: down in 2025H2–26H1 (56, 43 vs ~64–295) | ≥20k flat (~5–17/HY) | equal-age | **No** |
| **OctoPrint plugins** | *down* (2–4/HY vs 7–40) | ≥10 instances: 3.0 vs 11.8/HY | ≥1k: 0 vs 3 total | current + sparse equal-age | **No** (platform declining) |

## What generalises
1. **High-usage hits: no increase anywhere.** In 8 of 8 ecosystems, new tools clearing a high usage bar are flat or down. The only exception is Obsidian (≥30k in 60 days, 0–2 → 2–4 per quarter), and its top new hits are mostly AI-agent integrations: Claudian, Agent Client, a Claude Code sidebar, WeSight, an MCP connector. This matches every earlier round (Show HN, Steam, Homebrew, VS Code).
2. **Modestly used tools: up in about half.** NVDA, HACS, Obsidian and AMO show 1.7–10× more new tools reaching a few hundred or a few thousand users. Nexus code mods show a small rise. WordPress, CRAN and OctoPrint do not.
3. **Supply: up everywhere except OctoPrint**, by 1.6–20×.

So the round 08 pattern partly holds. "Many more lightly used tools, no more big hits" fits personal customisation ecosystems, but not all of them.

## Why some ecosystems and not others? (speculative)
- **Builder = user, small social distribution.** NVDA, HACS, Obsidian, browser extensions and game mods are mostly "scratch my own itch, share it with people like me". That is the case where AI lowers the build cost for people who couldn't previously build.
- **Professional or saturated markets.** WordPress plugins are a mature, commercial and SEO-driven market, so new listings compete with incumbents. CRAN packages are mostly written by people who could already code, adoption runs through papers and teaching, and the 2026 surge is too young to show up.
- **Declining platforms.** OctoPrint is losing users to Klipper/Mainsail and closed Bambu printers, so cheaper building can't overcome a shrinking audience.
- **Gatekeeping matters.** Obsidian's biggest jump coincides with ending manual review. Most of its 2026 hits are genuinely new repos (about 80% created in 2026, so this isn't just the backlog), but how easy it is to get listed clearly shapes what gets discovered. HACS still has a review backlog of about 2,000 PRs, and F-Droid admits 3× more apps while receiving about 12× more submissions. Reviewer capacity, not building capacity, may now be the binding constraint in some registries.

## Caveats
- Measures are inconsistent. AMO, Nexus and WordPress use current usage; NVDA, HACS, Obsidian and CRAN use equal-age usage. Downloads (Obsidian, NVDA, Nexus) include update downloads and bots.
- The CRAN ≥2k series is noisy (64–295 per half-year in the baseline), so treat its decline loosely.
- Survivorship: AMO, WordPress, Nexus and CRAN only count items still listed.
- AMO's top 2026 items include suspicious new-tab/search extensions with high ADU but near-zero downloads, so they may be external or bundled distribution.
- Obsidian has no pre-May submission data (PRs are not visible), so a cheaper listing process can't be separated from more software being built. Its user base also appears to be growing fast, plausibly for AI-related reasons.
- Recent frontier models are only weeks old. Re-check in Q2 2027.

## Bottom line
Across 8 niche ecosystems, the strongest robust finding is that AI-era supply growth has not produced more new widely used tools, except AI tooling itself. The softer finding, more new tools that get *some* real use, holds in personal-customisation communities (NVDA, HACS, Obsidian, Firefox, and weakly Nexus). It does not hold in professional or declining ones (WordPress, CRAN, OctoPrint).

---

## Round 3 additions (2026-10-15): Flathub, Decky Loader, Raycast, Blender Extensions
Detail is in `niche-usage/{flathub,decky,raycast,blender}/REPORT.md`.

| Ecosystem | Submissions | Listings | Modestly used new tools | Big hits | Measure | Verdict |
|---|---|---|---|---|---|---|
| **Flathub** | ~340–490/HY → 1,211 (26H1), 1,173 (26H2 partial): **3–5×** | ~200–250 → 308 (+30%) | ≥1k new installs in 90d: 120–156 → 216 (+50%), but **flat once normalised** for ecosystem install growth (21M → 244M/HY since 2021) | ≥10k in 90d: 14–25 → 25, flat | equal-age (daily stats) | **No** beyond platform growth. Reviewers absorb the surge. |
| **Decky Loader** | addition PRs 13–42/HY → 68 (26H1), 38 (26H2, 0 merged yet) | 5–24/HY → 21 | ≥20k: 2–13 → 5 | ≥100k down | current (equal-age only from 2024-08) | **No**; review-bottlenecked; tiny |
| **Raycast** | rising; 236 open, nearly all 2026Q3–Q4 | ~580–650/yr → 944 YTD (~2×) | current only; recent cohorts trail (age confound) | none recent | current | **Inconclusive**; top recent items mostly AI/agent tooling and company integrations |
| **Blender Extensions** (launched Jul 2024) | queue ~725 (Apr 2025) → ~2,170 (Oct 2026) | 152 → 250/HY; genuinely new GitHub-linked projects 40 (25Q2) → 91 (26Q2) → 123 (26Q3) | ≥1k downloads: 196 (26H1) vs 151–194, despite less time | ≥10k down; recent big hits mostly migrated old add-ons | current | **Weak yes** |

AI add-ons in Blender's queue (BlenderGPT, several MCP bridges) were mostly declined. Flathub's top new apps are LM Studio, Jan and OpenCode.

## Updated picture across 12 ecosystems
- **Big hits (new tools reaching high usage):** flat or down in all 12, except AI tooling and Obsidian's AI-agent plugins.
- **Modestly used new tools:**
  - Clearly up: NVDA, HACS, Obsidian, Firefox add-ons.
  - Weakly up: Nexus code mods, Blender.
  - Flat after normalising: Flathub.
  - No: WordPress, CRAN, OctoPrint, Decky.
  - Inconclusive: Raycast.
- **New observation: submissions are surging much faster than listings wherever humans review.**
  - Flathub: submissions 3–5×, listings +30%.
  - Decky: 68 addition PRs vs 23 merged.
  - Raycast: 236 PRs queued.
  - Blender: queue about 3×.
  - F-Droid: submissions ~12× vs admissions 3×.
  - HACS: ~2,000-PR backlog.
  - Obsidian removed manual review and its listings went ~20×.

  So a registry's measured supply depends heavily on its review policy. The "more modestly used tools" signal is strongest where listing is cheap (Firefox add-ons, Obsidian after May) or reviewers keep up with niche demand (NVDA, HACS). Where reviewers filter hard (Flathub), what gets through looks like the pre-AI mix, so filtering seems to remove mostly low-use submissions rather than a hidden layer of good software.
