# 10: Mainstream and professional markets (Steam, Google Play, Chrome Web Store, Atlassian) (2026-10-15)

This round fills gaps left by the niche rounds (08–09): paid and mainstream consumer software (games, Android, the largest extension store), plus a professional/B2B market. The method is the same: cohorts by listing date, usage at equal age where possible, confounders. Detail is in `market-usage/<source>/REPORT.md`.

| Market | Supply growth | Modestly used new items | Big hits | Measure | Verdict |
|---|---|---|---|---|---|
| **Steam** | 2.6× 2021→2026H1; +56% vs 2024H1. 26–29% of 2026 releases disclose AI use | ≥100 reviews in 90d: ~520–770/HY (2021–23) → 852 (24H1) → 1,382 (26H1) (sampled). Hit rate flat at ~12% | **Full count:** ≥1k reviews in 90d 146/HY (2022–23) → 207 (2024) → 251 (26H1); ≥2k and ≥5k flat since 2024 | equal-age (monthly/weekly review histograms) | **More modest successes, in proportion to supply; no more big hits** |
| **Google Play** | 60–68k/mo (2022–23) → ~40k (2024–25, testing rule + purges) → 70k (2026H1): **a rebound, not a surge** | ≥5k downloads at 23 weeks tracks supply: 50–66k → 32–35k → 53k | Recent big hits disproportionately AI apps | equal-age (AppBrain aggregates, sparse Wayback) | **No AI-era surge.** Contrasts with iOS (~3× new apps) |
| **Chrome Web Store** | 12.7k (24H1) → 76.8k (26H1): **6×** | ≥100 users: 5.2k → 10.4k (2×). ≥1k: 2,015 vs 2,023, despite ~¼ the age | ≥10k and ≥100k lower so far (346 vs 532; 39 vs 97); top new items are AI/agent extensions | current users (age-biased against recent) | **Likely yes at low and modest bars; no sign of more hits.** Mirrors Firefox add-ons |
| **Atlassian Marketplace** (Cloud) | 287/HY (2021–24) → 826/HY (2025H2–26): ~3× | ≥100 installs: ~70 → ~30/HY | ≥1k: 9 → ~2/HY; new hits are AI-agent integrations (Claude Agent for Jira, Cursor, Copilot) or established vendors | current (age-biased) | **No.** Matches the professional-market pattern (WordPress, CRAN) |

## Notes on interpretation
- **Steam.** Our full count supersedes the agent's sampled high-bar estimate (342 → 251 for ≥1k in 2026H1). The extra modestly successful games come from more releases at an unchanged hit rate, not from a better hit rate. AI-disclosed games clear the ≥100-review bar at about half the rate of other games. Steam's audience grew ~10% from 2024 to 2026, so the ≥1k rise (+20%) is only slightly above audience growth.
- **Google Play.** The rule requiring new personal developer accounts to run a closed test with 12–20 testers for 14 days (Nov 2023) is another gate. On iOS, Demirer et al. found new apps up ~3× with flat usage; Android supply only returned to its 2022 level. Without that gate, Android might look like iOS.
- **Chrome.** Chrome-Stats' age curve says only ~0.25% of extensions have >1k users at launch, vs ~9.5% by 24 months. A 2026H1 cohort already matching 2024H1 at ≥1k is therefore strong evidence that more extensions will clear that bar. Survivorship (removed extensions are missing) flatters older cohorts too.
- **Atlassian.** A one-off 2025H1 spike (919 Cloud listings, 274 with ≥100 installs) is mostly established vendors re-listing during the Server→Cloud and Connect→Forge migrations, so it is excluded.

## How this changes the overall picture (16 ecosystems with usage data)
1. **Big hits: no increase anywhere** except AI tooling. Steam is now confirmed by a full count. This is the most robust finding of the whole project.
2. **Modestly used new software is up where supply is cheap to list and the audience is consumers or hobbyists:**
   - NVDA, HACS, Obsidian
   - Firefox and Chrome extensions
   - Steam (in proportion to supply)
   - weakly Nexus and Blender
3. **It is not up** in professional or B2B markets (Atlassian, WordPress, CRAN), declining platforms (OctoPrint), or registries whose gatekeeping limits listings (Flathub, Decky, Google Play).
4. **Hit rates fall almost everywhere.** In Chrome, Firefox and WordPress, the share of new items reaching any given bar drops as supply grows. Steam is the exception: its ≥100-review hit rate held at ~12%, even though AI-disclosed games clear the bar at about half the rate of others.
