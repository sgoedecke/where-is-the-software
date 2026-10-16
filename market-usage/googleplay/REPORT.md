# Google Play Android app cohorts (usage-cohort analysis)

## Source and method

- **Supply:** AppBrain's public `number-of-android-apps` page, cached at `cache/appbrain_number_of_apps.html`, exposes monthly launched and unpublished Google Play app counts from Oct 2021 through Sep 2026; I excluded the partial Oct 2026 datapoint. I cross-checked the current headline against 42matters (`cache/42matters_google_play_stats.html`): 42matters reports 2,632,639 Google Play apps and 2,605 new apps/day on 2026-10-15, with July/Aug/Sep new-app counts of 114,303, 96,244, and 84,664. AppBrain is lower/currently filtered: 2,028,343 apps, including 722,649 low-quality apps and 276,053 apps with >50k downloads in its category table.
- **Equal-age usage:** AppBrain's `android-app-downloads` page says it tracks, for apps launched in a given week, the share crossing >500, >5,000 and >50,000 downloads. I pulled Wayback snapshots via CDX plus the live page (`cache/wayback/`), parsed 19 usable snapshots, and used the oldest exposed age bucket, **23 weeks after launch**, as the equal-age comparison. The half-year usage counts below are estimates: half-year launched supply × mean 23-week crossing rate from archived weekly cohorts in that half; `23w n` is how many archived weekly cohorts supported that half-year.
- **Cohort sample / top-items check:** I installed `google-play-scraper` into `.venv/`, searched 100 mainstream terms/categories plus explicit recent/AI probes, and cached 1,589 app-detail pages in `cache/googleplay/`. This sample is intentionally broad but **search-biased toward popular and current apps**; I use it for qualitative recent winners and current-usage sanity checks, not as an unbiased registry sample. Most top Google Play apps are closed-source, so I could not reliably verify GitHub repository creation dates; the table uses Play `released` date and flags obvious old-brand/new-app cases in the discussion.

## Cohort table

Usage thresholds are AppBrain's thresholds at 23 weeks after launch. `2021H2*` is AppBrain's partial supply window (Oct-Dec only), so do not compare it as a full half-year.

| cohort | months | launched | launched/mo | unpublished | net | 23w n | ≥500 @23w | ≥5k @23w | ≥50k @23w |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021H2* | 3 | 188,902 | 62,967 | 312,816 | -123,914 | 3 | 90k | 39k | 11k |
| 2022H1 | 6 | 401,243 | 66,874 | 333,917 | 67,326 | 0 | — | — | — |
| 2022H2 | 6 | 373,335 | 62,222 | 375,286 | -1,951 | 2 | 156k | 66k | 18k |
| 2023H1 | 6 | 345,348 | 57,558 | 395,669 | -50,321 | 0 | — | — | — |
| 2023H2 | 6 | 406,127 | 67,688 | 644,281 | -238,154 | 2 | 132k | 50k | 15k |
| 2024H1 | 6 | 257,643 | 42,940 | 986,313 | -728,670 | 5 | 85k | 34k | 11k |
| 2024H2 | 6 | 227,024 | 37,837 | 335,008 | -107,984 | 2 | 73k | 32k | 10k |
| 2025H1 | 6 | 245,391 | 40,898 | 272,078 | -26,687 | 4 | 83k | 35k | 12k |
| 2025H2 | 6 | 294,421 | 49,070 | 197,279 | 97,142 | 0 | — | — | — |
| 2026H1 | 6 | 422,557 | 70,426 | 229,995 | 192,562 | 1 | 145k | 53k | 15k |
| 2026H2 | 3 | 201,265 | 67,088 | 98,869 | 102,396 | 0 | — | — | — |

## Search-sample current usage sanity check

This table is **not** used as the platform estimate because Play search over-selects popular apps and older cohorts have more time to accumulate installs. It is useful mainly as a direction check: recent search-visible apps can still reach millions, but the current-install share naturally falls for 2025-26 cohorts because they are younger.

| cohort | n | ≥5k now | ≥50k now | ≥1M now | AI-flagged |
| --- | --- | --- | --- | --- | --- |
| 2021H1 | 40 | 40 | 37 | 26 | 7 |
| 2021H2 | 37 | 37 | 31 | 23 | 11 |
| 2022H1 | 42 | 42 | 38 | 28 | 12 |
| 2022H2 | 43 | 43 | 36 | 22 | 8 |
| 2023H1 | 55 | 52 | 52 | 40 | 31 |
| 2023H2 | 41 | 40 | 38 | 25 | 20 |
| 2024H1 | 51 | 50 | 41 | 26 | 23 |
| 2024H2 | 41 | 37 | 31 | 14 | 15 |
| 2025H1 | 56 | 48 | 39 | 21 | 28 |
| 2025H2 | 41 | 31 | 22 | 12 | 15 |
| 2026H1 | 60 | 29 | 15 | 10 | 21 |
| 2026H2 | 43 | 19 | 12 | 4 | 22 |

## Top recent items in the search sample

Top apps released on Play in 2025-26, sorted by current `realInstalls`. AI flag is a string/description/developer heuristic; false negatives/positives are possible.

| app | category | released | real installs | found via | AI? |
| --- | --- | --- | --- | --- | --- |
| Grok | Productivity | 2025-03-24 | 130,034,069 | ai image generator | yes |
| Edits: Video Editor | Video Players & Editors | 2025-04-21 | 126,282,716 | video editor | yes |
| DeepSeek - AI Assistant | Productivity | 2025-01-08 | 100,330,276 | ai chat | yes |
| Instamart: Groceries & more | Shopping | 2025-01-09 | 72,982,384 | grocery delivery | no |
| SeaBank | Finance | 2026-09-22 | 56,597,879 | banking | no |
| Gemini Notebook | Productivity | 2025-05-16 | 46,295,191 | new productivity app | yes |
| HDFC Bank App: Banking & Cards | Finance | 2025-05-08 | 26,647,018 | banking | no |
| SpeedTop VPN: Fast & Secure | Tools | 2025-06-18 | 25,958,537 | vpn | no |
| Огонь VPN | Tools | 2025-11-05 | 24,189,586 | vpn | no |
| FxPro: Trading & Investing | Finance | 2026-03-11 | 21,401,749 | stock trading | no |
| Ping VPN | Tools | 2026-02-17 | 19,158,271 | vpn | no |
| Riff-Video Chat & Make Friends | Entertainment | 2025-04-18 | 15,110,486 | video call | no |
| Ninja VPN - Fast & Secure VPN | Tools | 2025-01-29 | 11,822,939 | vpn | no |
| Live Wallpaper - Wallpapers 4K | Personalization | 2025-01-17 | 11,667,333 | wallpaper | no |
| Manus AI | Productivity | 2025-04-23 | 11,197,960 | perplexity ai | yes |
| MOVA: More Cashback | Shopping | 2025-01-11 | 8,984,423 | coupon | no |
| KwaiCut - Video Editor | Video Players & Editors | 2025-02-19 | 8,405,940 | video editor | yes |
| ChatGO - AI Chat Assistant | Lifestyle | 2025-12-28 | 7,797,120 | ai chat | yes |
| Dootchi: Chat with AI Chars | Entertainment | 2026-01-17 | 7,445,433 | ai chat | yes |
| Sea Soul: AI Chat | Entertainment | 2026-03-10 | 6,018,573 | ai chat | yes |
| DIY Wallpaper Maker Collage | Personalization | 2026-02-13 | 5,901,119 | wallpaper | no |
| ABCmouse: Kids Learning Games | Education | 2025-02-14 | 5,817,735 | kids game | no |
| Deep Think - AI Seek Chatbot | Productivity | 2025-01-22 | 5,374,638 | perplexity ai | yes |
| Language Learning: Pingo AI | Education | 2025-01-02 | 5,173,667 | language learning | yes |
| Vintage Camera - Film Camera | Photography | 2025-07-11 | 4,996,899 | camera filter | no |

Notable pattern: **29 of the top 50** 2025-26 Play-released apps in this search-biased sample are AI-flagged. The top AI/new-app items include Grok, DeepSeek, Gemini Notebook, Manus AI, Dootchi, Sea Soul, Pingo AI, Tipsy Chat, and Cycle AI; the top non-AI items are mostly incumbent or utility categories (banking/finance, grocery, VPN, wallpapers, video editing). Several high-install “new” apps are old companies or services newly represented by a Play listing (HDFC Bank, FxPro, SeaBank, Instamart, Google/Meta products), so they are not all greenfield software projects.

## Confounders and caveats

- **Policy shocks suppress supply.** Google announced in Nov 2023 that new personal Play Console accounts must run a closed test with at least 20 testers for two weeks before production; the Dec 2024 update reduced this to 12 testers. This lines up with AppBrain's 2024 supply trough and makes 2024-25 a bad baseline for “organic” creation.
- **Developer verification and review intensity.** Google's same Nov 2023 post describes expanded developer verification and deeper app review. Existing developers had to choose verification deadlines in 2024; this likely removed or delayed long-tail listings.
- **Mass removals / survivorship.** AppBrain records huge unpublished counts: 986k in 2024H1 and 335k in 2024H2. Removed apps disappear from Play and the scraper sample, so current snapshots undercount low-quality/failed cohorts.
- **AppBrain filtering.** AppBrain's current total (2.03M) is far below 42matters' 2.63M and AppBrain labels 723k category-listed apps low quality; AppBrain's cohort/threshold data is probably a filtered market view, not raw Play Console submissions.
- **Platform/user-base scaling.** I did not find a public Android equivalent to Demirer et al.'s iOS result with total usage by cohort. Download thresholds are unscaled; Android's global user base grew, so a constant 50k-download threshold is easier over time than a share-of-platform threshold.
- **Enumeration bias.** Google Play cannot be fully enumerated with the public scraper. The AppBrain aggregate is the main quantitative evidence; the scraper sample is only a qualitative/top-items check.

## Verdict (3 sentences)

Google Play **does not show a clean AI-era supply explosion**: after a severe 2024 policy/removal trough, AppBrain launches recovered to about 70k/month in 2026H1, which is higher than 2024-25 but only roughly back to / slightly above 2021-23 highs. More apps are reaching real install thresholds than in the depressed 2024-25 cohorts (estimated 53k apps over 5k downloads by 23 weeks in 2026H1 vs 35k in 2025H1), but not more than the best pre-AI observed cohort (66k in 2022H2) and the 23-week crossing rates are not rising. There are many recent AI hits in the top sample, but no evidence of a broad increase in non-AI blockbuster creation beyond the rebound from policy/removal distortions.
