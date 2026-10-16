# Follow-up link-rot audit: AI-built Show HN projects

Generated on 2026-10-15. Fixed random seed: `20261015`. Files: `sample_treatment.csv`, `sample_control.csv`, `sample_baseline.csv`, `handcheck_20.csv`, `cache/*.json`.

## Headline table

Wilson 95% intervals in brackets. "Maintained" is a GitHub push in the last 90 days for current rows, and a default-branch commit between months 6 and 12 for the baseline same-age row. "External-user signal" is ≥10 current GitHub stars or at least one issue/PR opened by a user other than the repo owner; the baseline same-age value is a lower bound using only non-owner issues/PRs opened by month 12 because historical stars are not available from the lightweight REST audit.

| Cohort | n | Alive | Maintained | External-user signal |
|---|---:|---:|---:|---:|
| AI-build mention (2025-26), current | 200 | 81.5% [75.5, 86.3] | 11.0% [7.4, 16.1] | 27.5% [21.8, 34.1] |
| No-mention control (2025-26), current | 200 | 84.5% [78.8, 88.9] | 7.5% [4.6, 12.0] | 15.5% [11.1, 21.2] |
| Pre-AI baseline (2022-23), current | 200 | 69.0% [62.3, 75.0] | 4.5% [2.4, 8.3] | 27.0% [21.3, 33.5] |
| Pre-AI baseline at same age | 200 | 16.5% [12.0, 22.3] | 14.5% [10.3, 20.0] | 19.0% [14.2, 25.0] |

## By HN points bucket

| Cohort | Points bucket | n | Alive | Maintained | External-user signal |
|---|---|---:|---:|---:|---:|
| AI-build mention current | <5 | 168 | 80.4% [73.7, 85.7] | 10.7% [6.9, 16.3] | 26.2% [20.1, 33.3] |
| AI-build mention current | 5-49 | 27 | 85.2% [67.5, 94.1] | 7.4% [2.1, 23.4] | 29.6% [15.9, 48.5] |
| AI-build mention current | >=50 | 5 | 100.0% [56.6, 100.0] | 40.0% [11.8, 76.9] | 60.0% [23.1, 88.2] |
| No-mention control current | <5 | 165 | 83.6% [77.2, 88.5] | 6.7% [3.8, 11.5] | 15.2% [10.5, 21.4] |
| No-mention control current | 5-49 | 31 | 90.3% [75.1, 96.7] | 12.9% [5.1, 28.9] | 19.4% [9.2, 36.3] |
| No-mention control current | >=50 | 4 | 75.0% [30.1, 95.4] | 0.0% [0.0, 49.0] | 0.0% [0.0, 49.0] |
| Pre-AI baseline current | <5 | 125 | 64.0% [55.3, 71.9] | 4.0% [1.7, 9.0] | 21.6% [15.3, 29.6] |
| Pre-AI baseline current | 5-49 | 54 | 79.6% [67.1, 88.2] | 5.6% [1.9, 15.1] | 33.3% [22.2, 46.6] |
| Pre-AI baseline current | >=50 | 21 | 71.4% [50.0, 86.2] | 4.8% [0.8, 22.7] | 42.9% [24.5, 63.5] |
| Pre-AI baseline same-age | <5 | 125 | 12.8% [8.0, 19.8] | 11.2% [6.8, 17.9] | 17.6% [11.9, 25.2] |
| Pre-AI baseline same-age | 5-49 | 54 | 14.8% [7.7, 26.6] | 14.8% [7.7, 26.6] | 18.5% [10.4, 30.8] |
| Pre-AI baseline same-age | >=50 | 21 | 42.9% [24.5, 63.5] | 33.3% [17.2, 54.6] | 28.6% [13.8, 50.0] |

## Treatment AI-product share

165/200 treatment items (82.5% [76.6, 87.1]) look like the product itself is AI/LLM/agent-related by a title/early-description heuristic. I did not exclude them because distinguishing "built with AI" from "is an AI product" is unreliable at scale from HN text alone.

## Classifier hand-check

A deterministic 20-item cross-cohort hand-check is in `handcheck_20.csv`. I reviewed the final URLs, status codes, body excerpts and curl probes for network-error cases; this disagreed with the automated alive/dead classifier on 0/20 items (0.0% [0.0, 16.1]). Most possible missed disagreements are automated-fetch access blocks (403/401/anti-bot) that may be live for a browser but counted dead by the primary classifier.

## Method

1. Pulled Show HN stories from the HN Algolia `search_by_date` API day-by-day for 2025-10-01 through 2026-04-15 and 2022-10-01 through 2023-04-15. The current window yielded 4388 AI-build-mention candidates and 22453 no-mention candidates; the baseline pool had 6674 posts.
2. Treatment was title/story text matching: `claude`, `claude code`, `cursor`, `vibe`, `vibe-coded`, `codex`, `copilot`, `built with AI`, `AI-built`, `lovable`, `bolt`, `v0`, `windsurf`, or `agent wrote`. Controls had no such match. Each cohort was sampled with seed `20261015` at up to 200 rows.
3. Current survival fetched each URL with a ≤20s timeout, a research User-Agent and concurrency 8. A page is alive if it returns HTTP 2xx/3xx and does not match parked-domain, expired deployment, soft-404 or Cloudflare-error heuristics.
4. GitHub repositories were detected from the submitted URL, final URL, and landing-page links. Since `gh auth status` was authenticated, the script used the GitHub REST API with the local `gh auth token` for stars, forks, archived/deleted status, pushed date, issue/PR counts and commit probes.
5. For the 2022-23 baseline, equal-age survival used the Wayback CDX API for 200 captures with real-looking content around month 9; if none were found it expanded to months 6-12. For GitHub repos, a default-branch commit between months 6 and 12 also counted as equal-age alive/maintained.

## Caveats

- Selection into mentioning AI is severe: treatment items are projects whose authors chose to mention AI tools, not all AI-assisted projects.
- Current-link survival mixes true abandonment with changed domains, private projects, login walls, geoblocks and bot protection.
- The AI-product flag is heuristic; AI products are common in this treatment and may survive differently from non-AI apps.
- Wayback coverage is uneven and biased toward more-linked public pages; same-age baseline alive rates are therefore approximate.
- GitHub maintenance is a proxy, misses non-GitHub/private work and uses default-branch commits for the historical baseline.
- External-user signals are GitHub-centric; non-GitHub usage, revenue and private customer usage are unobserved.

## Three-sentence bottom line

In this Show HN sample, AI-build-mention projects are not obviously more durable: 82% are currently alive versus 84% for contemporaneous no-mention controls and 69% for the older baseline today. External-user signals are similarly scarce (28% for treatment versus 16% for controls), while the pre-AI baseline's equal-age alive estimate is 16%. The cleanest read is that AI appears to have increased launch volume more than it increased the share of projects that remain maintained or visibly used, with substantial uncertainty from self-selection and link/Wayback measurement error.
