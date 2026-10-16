# WordPress.org plugin directory niche-usage cohorts

Source: WordPress.org Plugins API (`query_plugins`, `browse=new`) fetched on 2026-10-15 with `per_page=250`. The API reported 75,808 currently listed plugins; this analysis uses the 35,207 still-listed plugins whose `added` date is >= 2021-01-01.

## Cohort table

Usage thresholds are current active-install buckets, not equal-age measurements. `downloads_per_day` is cumulative `downloaded` divided by days since `added`, included as a rough age-normalized velocity proxy.

| cohort | still_listed_created | active_ge_100 | share_active_ge_100 | active_ge_1000 | share_active_ge_1000 | active_ge_10000 | share_active_ge_10000 | dl_per_day_ge_10 | share_dl_per_day_ge_10 | dl_per_day_ge_50 | share_dl_per_day_ge_50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021H1 | 1842 | 589 | 32.0% | 246 | 13.4% | 51 | 2.8% | 276 | 15.0% | 95 | 5.2% |
| 2021H2 | 1590 | 495 | 31.1% | 181 | 11.4% | 33 | 2.1% | 223 | 14.0% | 60 | 3.8% |
| 2022H1 | 1555 | 503 | 32.3% | 175 | 11.3% | 34 | 2.2% | 208 | 13.4% | 66 | 4.2% |
| 2022H2 | 1629 | 474 | 29.1% | 172 | 10.6% | 35 | 2.1% | 203 | 12.5% | 73 | 4.5% |
| 2023H1 | 1298 | 372 | 28.7% | 126 | 9.7% | 21 | 1.6% | 167 | 12.9% | 44 | 3.4% |
| 2023H2 | 546 | 170 | 31.1% | 51 | 9.3% | 12 | 2.2% | 75 | 13.7% | 29 | 5.3% |
| 2024H1 | 1345 | 347 | 25.8% | 117 | 8.7% | 31 | 2.3% | 188 | 14.0% | 64 | 4.8% |
| 2024H2 | 1966 | 415 | 21.1% | 105 | 5.3% | 17 | 0.9% | 182 | 9.3% | 52 | 2.6% |
| 2025H1 | 2555 | 383 | 15.0% | 82 | 3.2% | 14 | 0.5% | 159 | 6.2% | 42 | 1.6% |
| 2025H2 | 3449 | 409 | 11.9% | 79 | 2.3% | 14 | 0.4% | 193 | 5.6% | 40 | 1.2% |
| 2026H1 | 7533 | 358 | 4.8% | 54 | 0.7% | 22 | 0.3% | 480 | 6.4% | 52 | 0.7% |
| 2026H2 | 9899 | 136 | 1.4% | 13 | 0.1% | 4 | 0.0% | 2904 | 29.3% | 86 | 0.9% |

## Method

I enumerated all newest-first API pages until the results crossed below 2021-01-01, using a User-Agent and short sleeps between requests. For each still-listed plugin I retained `slug`, `name`, `added`, `active_installs`, `downloaded`, `rating`, `num_ratings`, `last_updated`, homepage, and short description, then grouped plugins into half-year creation cohorts. Active-install thresholds are the requested WordPress buckets (≥100, ≥1,000, ≥10,000); because the API gives current bucketed installs rather than historical equal-age installs, older cohorts have more time to accumulate usage. As an equal-age-ish alternative, I report `downloaded / age_days` velocity columns; it is still imperfect because downloads include updates, bots, CI, and release cadence.

I also sampled Wayback CDX snapshots for top recent plugins and parsed archived `Active installations` where available. This sample is useful as a sanity check on fast early growth, but it is deliberately not used for the full cohort table because snapshots are sparse, plugin-page markup changes, and the sample is top-heavy.

I did not recover removed or closed plugins. WordPress.org's public API drops closed/removed plugins, so `still_listed_created` is a survivorship count, not the true number submitted, approved, or initially listed.

## Wayback equal-age spot checks

| slug | added | current_active_installs | snapshot_date | age_days | archived_active_installs | note |
| --- | --- | --- | --- | --- | --- | --- |
| sg-ai-studio | 2026-04-14 | 1000000 | 2026-04-21 | 7 | 50,000+ | first parsable early snapshot |
| hostinger-reach | 2025-08-11 | 1000000 | 2025-08-20 | 9 | 10,000+ | first parsable early snapshot |
| cookieadmin | 2025-07-15 | 400000 | 2025-07-19 | 4 | 1,000+ | first parsable early snapshot |
| angie | 2025-09-17 | 100000 | 2026-03-16 | 180 | 7,000+ | first parsable early snapshot |
| manage | 2026-03-08 | 100000 | 2026-03-16 | 8 | 3,000+ | first parsable early snapshot |
| formlayer | 2026-05-26 | 100000 | 2026-07-12 | 47 | 70,000+ | first parsable early snapshot |
| reddit-for-woocommerce | 2025-11-11 | 90000 | 2025-12-05 | 24 | 100+ | first parsable early snapshot |
| snapchat-for-woocommerce | 2025-09-26 | 80000 |  |  |  | CDX failed: HTTPError HTTP Error 503: Service Unavailable |

## Top current-use plugins added in 2025H2–2026

| rank | name | slug | added | active_installs | downloaded | downloads_per_day | ai_theme | explicit_ai_built | judgment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | AI Agent by SiteGround | sg-ai-studio | 2026-04-14 | 1000000 | 13678815 | 74341.386 | yes | no | AI-themed plugin |
| 2 | Hostinger Reach &#8211; AI-Powered Email Marketing for WordPress | hostinger-reach | 2025-08-11 | 1000000 | 700655 | 1629.43 | yes | no | AI-themed plugin |
| 3 | CookieAdmin &#8211; Cookie Consent Banner | cookieadmin | 2025-07-15 | 400000 | 1356007 | 2967.193 | no | no | connector/add-on for established WordPress/SaaS ecosystem |
| 4 | Angie – Agentic AI | angie | 2025-09-17 | 100000 | 966607 | 2459.56 | yes | no | AI-themed plugin |
| 5 | Manage &#8211; Centralized site maintenance and monitoring | manage | 2026-03-08 | 100000 | 458392 | 2074.172 | no | no | niche WordPress utility or vertical tool |
| 6 | FormLayer | formlayer | 2026-05-26 | 100000 | 175805 | 1238.063 | no | no | connector/add-on for established WordPress/SaaS ecosystem |
| 7 | Reddit for WooCommerce | reddit-for-woocommerce | 2025-11-11 | 90000 | 483483 | 1430.423 | no | no | connector/add-on for established WordPress/SaaS ecosystem |
| 8 | Snapchat for WooCommerce | snapchat-for-woocommerce | 2025-09-26 | 80000 | 508189 | 1323.409 | no | no | connector/add-on for established WordPress/SaaS ecosystem |
| 9 | WPVibe – MCP Server for WordPress, works with Claude, ChatGPT &amp; other AI MCP agents | vibe-ai | 2026-04-20 | 70000 | 408511 | 2295.006 | yes | no | AI-themed plugin |
| 10 | Spectra Blocks – AI Website Builder for the Block Editor | spectra-blocks | 2026-07-08 | 60000 | 227280 | 2295.758 | yes | no | AI-themed plugin |

Spot-check notes: the top recent plugins are mostly AI-feature products, hosting/vendor-backed plugins, WooCommerce ad-network connectors, or narrow site-management/form utilities. Rows marked `ai_theme=yes` describe AI functionality; none of the top ten stated in its WordPress.org description that the plugin itself was AI-built/generated.

## Confounders and ecosystem events

- **Survivorship:** closed, delisted, rejected, and removed plugins disappear from the query API. Counts here are "created and still listed".
- **Current-use/age confounding:** `active_installs` is current and bucketed. Old plugins had more time to acquire installs; strong recent performance is robust, but weak recent performance can be inconclusive.
- **Download-rate noise:** `downloaded / age_days` partly controls age, but WordPress downloads include updates/reinstalls and can be inflated by bots, CI, and release cadence. Very young 2026H2 plugins can look high on downloads/day after launch bursts.
- **Review queue and AI submissions:** the Plugins Team said submissions doubled in 2025, 2025 reviews reached 12,713 (+40.6% vs 2024), approvals were 5,415 (+66.2%), and AI affected both plugin submissions and review tooling. Source: https://make.wordpress.org/plugins/2026/01/07/a-year-in-the-plugins-team-2025/
- **2025 queue stats:** by Aug. 31, 2025 the team reported 60,187 published plugins, 7,670 new submissions YTD (+87.3% YoY), an average of 235 submissions/week vs 124 the year before, and 85.3% of first reviews initiated by an automated AI/algorithmic system. Source: https://make.wordpress.org/plugins/2025/08/31/stats-of-plugins-team-after-wordcamp-us/
- **2026 submission surge/backlog:** in Mar. 2026 the team reported weekly submissions had quadrupled vs 2024 and exceeded 500/week; in Jun. 2026 they reported the queue peaked near 1,050 in mid-April, fell near zero, and May hit ~700 submissions/week and nearly 3,000 initial reviews. Sources: https://make.wordpress.org/plugins/2026/03/13/contribute-to-the-plugins-team/ and https://make.wordpress.org/plugins/2026/06/13/update-on-the-status-of-the-team-june-2026/
- **Security/release policy:** WordPress.org announced Protect the Shire in Jun. 2026, temporarily delaying plugin/theme release auto-updates up to 24 hours amid AI-era supply-chain risk. Source: https://wordpress.org/news/2026/06/pts/
- **WP Engine dispute:** 2024–25 WordPress.org governance/distribution disputes may have affected developer behavior and trust, but I did not find a Plugins Team post quantifying its plugin-directory submission effect.

## 3-sentence verdict

The WordPress directory supports the 'more small/lightly used tools' half of the hypothesis mainly through supply: still-listed creations rose from a 2022–24 half-year average of 1390 to 3,449 in 2025H2, 7,533 in 2026H1, and a partial 9,899 in 2026H2. It does not show a matching boom in current active-use hits: the 2022–24 averages were 380 plugins at ≥100 installs, 124 at ≥1,000, and 25 at ≥10,000, versus 409/79/14 in 2025H2, 358/54/22 in 2026H1, and 136/13/4 so far in 2026H2. Wayback spot checks and download-per-day rates show that a few recent platform-backed, connector, and AI-feature plugins grew very fast, but the cohort-level result is a flood of new listings with sharply lower shares clearing install buckets, not clear evidence of more new broadly adopted software.
