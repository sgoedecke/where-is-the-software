# Where is all the new good software? — Round 1 findings (2026-10-14)

Prompt: https://www.natemeyvis.com/where-is-all-the-new-good-software/ (12 Oct 2026).
Questions: (a) are tech companies shipping more features, (b) are game companies doing more hard technical work on old codebases, (c) is software more reliable (excluding AI-traffic-hit services), (d) are niche communities suddenly building software.

AI timeline used for breaks: Claude Code Feb/May 2025; agentic coding mainstream H2 2025; Claude Fable 5 Jun 9 2026; Opus 5 Jul 24 2026; Opus 5.5 Sep 22 2026. Baseline = 2022–24.

## (a) Feature velocity — more code, not visibly more announced features

Merged human PRs (bots excluded), Sep 1–14 each year (`data/authors.tsv`, `scripts/authors.py`):

| Repo | 2024 | 2026 | PRs/author 2024→2026 |
|---|---|---|---|
| VS Code | 389 | 703 | 7.6 → 10.7 |
| Kibana | 425 | 636 | 3.0 → 3.7 |
| Sentry | 517 | 770 | 7.0 → 7.7 |
| Supabase | 113 | 255 | 2.6 → 3.8 |
| Grafana | 314 | 309 | 3.2 → 2.9 |
| PostHog | 175 | 851+ (search capped at 1000) | 6.0 → 8.5 |

Monthly merged-PR counts 2022–2026 (incl. some bots): `data/pr_*.tsv`. Growth is mostly more contributors; per-author throughput +10–40%.

Commits with AI co-author trailers (rough commit search, Sep 1–14 2025 → 2026): VS Code 6% → ~63%; Kibana 38% → 57%; PostHog 25% → 34%; Grafana 16% → 36%; Sentry 8% → 27%; Supabase 30% → 30%.

AWS "What's New" posts per year: 2021 2,074; 2022 2,101; 2023 2,715; 2024 2,345; 2025 2,328; 2026 YTD (to Oct 14) 1,883 ≈ 2,400 annualised. Flat.

## (b) Games

Steam announcements for the 3,000 most-owned games (SteamSpy), Jan–Sep windows (`data/steam_news.tgz`, `scripts/steam.py`):

| Year | Share of ~pre-2018 games (appid<700k, n=1,845) with any patch/update post | Dormant ≥2y games that posted (all 3,000) |
|---|---|---|
| 2021 | 25.7% | 70/567 |
| 2022 | 23.5% | 68/641 |
| 2023 | 20.6% | 81/754 |
| 2024 | 18.5% | 92/861 |
| 2025 | 19.5% | 103/926 |
| 2026 | 18.9% | 100/966 |

→ No sign studios are touching old codebases more (on Steam, among popular games). Caveats: popular-game sample; announcements ≠ builds; appid is a proxy for age.

Hobbyist side: big step-change (see `02-game-hobbyist-catalogue.md`).

## (c) Reliability — flat to slightly worse; AI-hit services much worse

~30 Atlassian Statuspage histories, Jan–Sep incident counts indexed to 2022–24 mean (`data/statuspages.json`, `scripts/sp.py`):

| | 2025 | 2026 |
|---|---|---|
| Non-AI median, all incidents | 0.87 | 1.00 |
| Non-AI median, major+critical | 0.85 | 1.09 |
| Non-AI mean, major+critical | 1.16 | 1.30 |
| GitHub (all / major) | — | 2.1× / 3.8× |
| Claude (all) | — | ~7× |

Mozilla Bugzilla (Firefox+Core+Toolkit), bugs filed Jan–Sep (`data/bz.tsv`): all 2022–24 ≈ 25.7k/yr → 2026 36.2k (+40%); regressions ≈ 2.7k → 3.7k (+37%); sec-high/critical ≈ 150 → 728 (likely AI-assisted bug finding; Aug–Sep show 0 because security bugs stay hidden until fixed). Ambiguous: more bugs *found* ≠ less reliable.

## (d) Niche communities — clear surge

| Registry | Before | 2026 | Change |
|---|---|---|---|
| NVDA add-on store, new add-ons/month (`data/nvda_addon_datastore_monthly.csv`) | ~6 (2024–H1 2025) | ~27 (Jan–Sep) | ~4× |
| HACS (Home Assistant) merged PRs, Jan–Sep | 265 (2024) | 1,704 | 6.4×; 1,953 PRs open (review backlog) |
| Raycast new extensions merged, Jan–Sep | 435 (2024) | 857 | 2× |

## Bottom line (round 1)

AI output is visible where results are mechanically checkable (decomp byte-match, recomp boots) and where amateurs were previously blocked (niche registries 2–6×, fan ports ~20×). Not visible in reliability, AWS feature announcements, or popular-game patch rates.
