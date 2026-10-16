# Chrome Web Store extension usage cohorts

## Source and method

- Primary source: Chrome-Stats public `advanced-search` API, queried 2026-10-15 against the 2026-10-14 snapshot. I filtered `itemCategory = extension` and `obsolete != true`, so the cohort table is **active public browser extensions**, not themes/apps and not removed listings. Chrome-Stats reports 283,169 active extensions on its public stats page; the API filter returned 283,176 (7-item drift, likely crawl/update timing).
- Listing date: Chrome-Stats `creationDate` (“date added”; Chrome-Stats says this can be a best guess for older extensions). CWS detail pages expose users, ratings, version, updated date and size, but not creation date.
- Usage: current displayed user count from Chrome-Stats/CWS, with thresholds ≥100, ≥1k, ≥10k and ≥100k active users. I could not get cohort-specific equal-age user histories without premium exports or per-item trend crawling, so current usage **favours older cohorts**. Chrome-Stats’ aggregate age curve says only ~0.25% of listings exceed 1k users at launch versus ~9.5% by 24 months, and ~0.028% exceed 10k at launch versus ~2.0% by 24 months.
- Enumeration check: the CWS sitemap exists at `https://chromewebstore.google.com/sitemap`; it had 44 shard URLs on 2026-10-14, and shard 0 contained 8,799 detail URLs. I used Chrome-Stats for cohorts because the sitemap has no creation date.
- Files: scripts in `scripts/`, caches in `cache/`, derived data in `data/`.

## Cohort table: active current extensions by listing half-year

| Cohort | Active listings | ≥100 users | ≥1k users | ≥10k users | ≥100k users | ≥100 share | ≥1k share |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021H1 | 2,628 | 1,659 | 873 | 339 | 73 | 63.1% | 33.2% |
| 2021H2 | 3,571 | 1,870 | 962 | 363 | 86 | 52.4% | 26.9% |
| 2022H1 | 6,071 | 2,719 | 1,237 | 402 | 65 | 44.8% | 20.4% |
| 2022H2 | 6,901 | 3,320 | 1,540 | 518 | 115 | 48.1% | 22.3% |
| 2023H1 | 9,751 | 4,330 | 1,845 | 574 | 115 | 44.4% | 18.9% |
| 2023H2 | 10,399 | 4,570 | 1,934 | 597 | 105 | 44.0% | 18.6% |
| 2024H1 | 12,681 | 5,165 | 2,023 | 532 | 97 | 40.7% | 16.0% |
| 2024H2 | 18,542 | 6,629 | 2,308 | 506 | 80 | 35.8% | 12.5% |
| 2025H1 | 26,762 | 7,563 | 2,144 | 425 | 54 | 28.3% | 8.0% |
| 2025H2 | 35,570 | 7,535 | 1,810 | 368 | 49 | 21.2% | 5.1% |
| 2026H1 | 76,842 | 10,410 | 2,015 | 346 | 39 | 13.6% | 2.6% |
| 2026H2* | 60,411 | 3,546 | 550 | 64 | 11 | 5.9% | 0.9% |

\* 2026H2 is partial through the 2026-10-14 Chrome-Stats snapshot.

### Reading the table

Supply has exploded: 2026H1 active listings are 2.9× 2025H1, 6.1× 2024H1, and 29× 2021H1. This is much steeper than the AMO result (4.8× listing growth).

At the low “real users” threshold, growth is real but much smaller than supply: 2026H1 has 10,410 extensions with ≥100 users, 1.38× 2025H1 and 2.02× 2024H1. That is comparable to AMO’s ≥100-user growth (1.7×), but Chrome’s supply grew far faster, so the success rate fell sharply.

At modest/high thresholds the current-user evidence is weak or negative: 2026H1 has about the same ≥1k extensions as 2024H1 (2,015 vs 2,023), fewer ≥10k (346 vs 532), and fewer ≥100k (39 vs 97). Because current usage penalizes young cohorts, these are not final equal-age outcomes; however, there is no evidence yet of a broad non-AI wave of new Chrome extensions becoming big hits.

## Top recent items check

Top 5 by current users in each recent quarter; full table is `data/top_recent_items.csv`.

| Slice | Extension | Created | Users | AI/agent? | Note |
|---|---|---:|---:|---|---|
| 2025Q3 | Claude | 2025-09-17 | 18.0M | Yes | Anthropic browser/agent extension; genuine new CWS extension, existing Claude product. |
| 2025Q3 | Phantom | 2025-07-24 | 5.0M | No | Crypto wallet; established product newly/re-listed in CWS. |
| 2025Q3 | CRXLauncher | 2025-07-03 | 1.0M | No | Extension launcher/dev-tool. |
| 2025Q3 | Ace AI Search | 2025-09-18 | 1.0M | Yes | AI search. |
| 2025Q3 | Bing Search and Homepage | 2025-09-21 | 1.0M | Yes-ish | Search/homepage extension with AI/GenAI tags; Microsoft/Bing product. |
| 2025Q4 | You Shall Not Pass by TeacherMagic.org | 2025-11-23 | 700k | No | Classroom/site blocking. |
| 2025Q4 | Amazon Quick | 2025-10-09 | 600k | Yes | Tagged AI/GenAI/marketing; quality unclear. |
| 2025Q4 | Manus AI Browser Operator | 2025-11-14 | 500k | Yes | AI browser operator/agent. |
| 2025Q4 | AutoGLM | 2025-11-18 | 500k | Yes | Zhipu/GLM AI. |
| 2025Q4 | Ad Block Wonder | 2025-11-10 | 300k | No | Ad blocker. |
| 2026Q1 | AdScrubber | 2026-03-22 | 1.0M | No | Ad blocker. |
| 2026Q1 | Quick Heal Web Protection | 2026-03-21 | 800k | No | Established security vendor. |
| 2026Q1 | Sicoob Internet Banking | 2026-03-19 | 600k | No | Bank/security helper; likely not a new software project. |
| 2026Q1 | Flexera Web Metering | 2026-03-03 | 600k | No | Enterprise IT/vendor extension. |
| 2026Q1 | 7TV | 2026-03-27 | 500k | No | Streaming/community extension; likely established project. |
| 2026Q2 | ChatGPT / Codex | 2026-05-07 | 7.0M | Yes | OpenAI/Codex browser extension; major AI hit. |
| 2026Q2 | i芒果・新标签页 | 2026-05-07 | 700k | No | Media/new-tab extension. |
| 2026Q2 | Kimi | 2026-04-19 | 500k | Yes | AI assistant/search. |
| 2026Q2 | Ad Block Ninja | 2026-06-06 | 400k | No | Ad blocker. |
| 2026Q2 | Cat Gatekeeper | 2026-04-24 | 300k | No | Blocking/gatekeeper utility. |
| 2026Q3 | Lightspeed Filter Helper Agent | 2026-09-24 | 700k | No | Education/filtering vendor helper; “agent” here is not AI. |
| 2026Q3 | GoFullPage BETA | 2026-08-14 | 300k | No | Beta/companion to an established screenshot product. |
| 2026Q3 | HP AI for Print | 2026-07-14 | 300k | Yes | HP AI print feature. |
| 2026Q3 | Ad Blocker Pro | 2026-08-13 | 200k | No | Ad blocker. |
| 2026Q3 | seats.aero | 2026-07-11 | 100k | No | Travel/award-search utility. |
| 2026Q4* | Previews (Twitch/YouTube/Kick) | 2026-10-12 | 70k | AI-tagged | Established media preview extension; tagged AI by Chrome-Stats. |
| 2026Q4* | Ask Advisor by Google | 2026-10-01 | 10k | Yes | Google marketing advisor/AI. |
| 2026Q4* | MFCA Labs | 2026-10-02 | 7k | No | Data/task utility. |
| 2026Q4* | My Direction Maps | 2026-10-01 | 7k | No | Maps/navigation. |
| 2026Q4* | CijferPacks | 2026-10-05 | 7k | No | Education/entertainment. |

The recent big-hit check is dominated by AI/browser-agent products at the very top (Claude, ChatGPT/Codex, Manus, Kimi, HP AI), plus established brands and utility clones (wallets, ad blockers, banking/security/filtering helpers). Many top “new” CWS listings are not new projects; they are browser companions, migrations, beta/relisted variants, or existing companies’ extensions newly appearing with a 2025–26 CWS creation date.

## Confounders and limitations

- **Current usage, not equal-age usage.** Recent cohorts have had less time to accumulate users. This makes a recent cohort beating older cohorts strong evidence, but a recent cohort trailing older cohorts weak evidence.
- **Survivorship/removals.** The table filters active public extensions. Removed/obsolete items are not counted in the main cohort table, so older supply is understated relative to recent supply. Chrome-Stats does retain obsolete records, but current real-user counts for removed items are not comparable.
- **Manifest V2 → V3 transition.** Chrome stopped accepting new public/unlisted MV2 extensions in Jan 2022; phase-out began in 2024; MV2 was disabled everywhere in Jul 2025; remaining MV2 extensions were removed from CWS by Aug 31 2026. This can kill old listings, force migrations/republications, and move users to newly listed MV3 replacements.
- **Featured and policy changes.** Chrome said MV2 extensions with the Featured badge lost it starting Jun 2024. CWS policy enforcement and MV3 remote-code/minimum-functionality reviews affect both spam and legitimate migrations.
- **Spam/search/ad-block clones.** The huge 2025–26 supply jump includes many low-user utilities, ad blockers, search/homepage extensions and thin clones; the falling ≥100/≥1k shares are consistent with that.
- **Platform growth.** Chrome-Stats reports ~3.16B total active users across active extensions, but I did not find a public historical denominator to scale thresholds over time. Absolute thresholds therefore ignore Chrome/CWS audience growth.
- **Creation date quality.** Chrome-Stats labels creation date as a best guess for some older extensions. CWS itself does not expose creation date on detail pages.

## Verdict

1. **More supply:** yes, dramatically — active 2026H1 CWS extension listings are 6.1× 2024H1 and 2.9× 2025H1, a larger supply surge than AMO.
2. **More modestly used new tools:** only at the low end — ≥100-user extensions increased, but far less than supply; ≥1k is roughly flat/down in current usage, subject to the age caveat.
3. **More big hits:** not broadly — ≥10k and ≥100k current-user counts are down for recent cohorts, and the standout recent big hits are mostly AI/browser-agent extensions or established-company companions rather than a broad wave of new non-AI software.
