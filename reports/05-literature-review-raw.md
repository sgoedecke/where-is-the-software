Agent is idle (waiting for messages). agent_id: dac8f199-5f35-49f2-8e54-52f38daf6482, agent_type: research, status: idle, description: Research AI software output evidence, elapsed: 13868s, total_turns: 2

[Turn 0]
I found no evidence that more good software is reaching users. There is strong evidence that much more software is being released, starting around late 2025 and accelerating in 2026. Mike Judge's "no shovelware" finding matched the data up to roughly mid/late 2025; the flood has arrived since.

Every measure of success I could check stayed flat or fell per item:
- **Demand:** App Store downloads rose only 2–3% a year.
- **Revenue:** apps launched in 2025 or later earn 3% of subscription revenue.
- **Hits:** the number of hits (≥10k-install VS Code extensions, ≥10-star repos) stayed flat or fell.
- **Steam:** games that disclose AI use reach ~100 reviews at about 55% of the rate of other games.
- **Firms:** controlled studies show per-developer gains that are small, temporary, or uncertain. Nine in ten executives report no AI effect on their firm's productivity.

The direct evidence for Meyvis's hypotheses is thin. The best support is for review/quality-assurance bottlenecks and for "AI-made software that never ships publicly"; I found almost nothing on leisure capture.

How I sourced this: web search engines were bot-blocked from this machine, so I fetched primary URLs directly and ran my own GitHub API and NVD (the US National Vulnerability Database) queries. Two of three research sub-agents returned results; the third (studies and economics) failed and I redid that area myself. **[V]** = I read or computed it myself; **[SA]** = a sub-agent reported it and I didn't re-check it.

---

## 1. Mike Judge, "Where's the Shovelware?" (2025-09-03)
https://mikelovesrobots.substack.com/p/wheres-the-shovelware-why-ai-coding **[V]**

**What he measured.** Each chart's caption names its source:
- **Steam game releases:** SteamDB.
- **New iOS and Android app releases:** Statista (statista.com/statistics/1020964, /1020956).
- **New domain registrations:** Verisign's Domain Name Industry Brief.
- **New public GitHub repos:** GH Archive, processed with about $70 of BigQuery.

**Other evidence in the post:**
- He ran a personal 6-week randomized self-test. The result wasn't significant, but the median was 21% slower with AI.
- He cites the Qodo survey finding that 14% of developers claim a 10× output gain.

**His conclusion:** the charts are "flat at best… you could not tell looking at these charts when AI-assisted coding became widely adopted." He argued that if 14% of developers were really 10×, worldwide new-software output would more than double.

**His follow-up, "The AI Shovelware Question: One Month Later" (2025-09-28)** **[V]**, https://mikelovesrobots.substack.com/p/the-ai-shovelware-question-one-month
- He added a GH Archive chart of pull requests: "There's no AI coding bump."
- He responded to "coding isn't the bottleneck": if coding were really 10× faster, firms that failed to exploit it "would be fucking fools."

**No 2026 update from him.** His Substack archive API shows only these two posts **[V]**.

**2026 analyses by others that follow up on the same question:**
- **Answer.AI, "So where are all the AI apps?"** (2026-03-12, updated Apr 2026) **[V]**, https://www.answer.ai/posts/2026-03-12-so-where-are-all-the-ai-apps.html
  - Originally found no post-ChatGPT inflection in new PyPI packages.
  - Update: "In March 2026, new package creation on PyPI increased to over 25,000… nearly double March 2025."
  - Release frequency among the top 15k packages: packages *not about AI* look like their pre-ChatGPT cohorts. Only AI-topic packages show a big jump.
- **Sulka Haro on Steam, Product Hunt analyses, RevenueCat** — covered in sections 2–3 and 6.
- **A discrepancy with Judge's PR chart.** Today's GitHub search index already shows public PRs up 63% from Sep 2024 (4.68M) to Sep 2025 (7.61M) **[V]**, which conflicts with his PR chart. The methods differ: the search index counts surviving objects including bot PRs, while GH Archive counts events. I can't reconcile the two.

## 2. App stores

### Volume

| Metric | Value | Source | Reliability |
|---|---|---|---|
| New iOS apps, Q1 2026 | 235,800, **+84% YoY**. New iOS apps fell about 48% between 2016 and 2024 | The Information via Gizmodo (2026-04-06) **[V]** https://gizmodo.com/apple-app-store-experiences-surge-in-new-apps-amid-vibe-coding-boom-2000742653 | Sensor Tower estimate, reported secondhand; the original is paywalled |
| All stores, Q1 2026 | **+60% YoY**; iOS +80%. April 2026 to date: +104% (iOS +89%) | Appfigures via TechCrunch (2026-04-18) **[V]** https://techcrunch.com/2026/04/18/the-app-store-is-booming-again-and-ai-may-be-why/ | Vendor estimate |
| New iOS apps, 2025 and H1 2026 | About **600k in 2025 (+30%)**; about **560k in H1 2026 alone** (roughly double) | Sensor Tower via NYT, "'Vibecoded' apps are flooding the App Store" (2026-07-20) **[V via 9to5Mac]** https://9to5mac.com/2026/07/20/report-app-store-added-nearly-as-many-new-apps-in-h1-2026-as-in-all-of-2025/ | Vendor estimate |
| Appfigures, new iOS apps | 448k (2024) → 557k (2025, +24%) | Appfigures (2025-12-05) **[SA]** | Vendor; the 2025 figure was published in December, so it is likely partial |
| 42matters, new iOS apps per month | 52.6k (Sep 2025) → **144.6k (Sep 2026)**. Google Play: 50.7k → 83.8k | https://42matters.com/ios-apple-app-store-statistics-and-trends **[SA]** | Vendor; method undisclosed |
| Apple, submissions reviewed | 7.77M (2024) → **9.10M (2025)**. 2025 rejections: 1.2M+ new apps rejected; 371k rejected as copycat/spam (vs 320k in 2024); bait-and-switch removals ~59k (vs ~17k) | Apple Newsroom (2026-05-20), https://www.apple.com/newsroom/2026/05/the-app-store-stopped-over-2-point-2-billion-usd-in-fraudulent-transactions-in-2025/; Transparency Report **[SA]** | **Primary.** Apple itself says "powerful AI development tools drive a surge in app submissions." |
| Apple, apps removed | 82.5k (2024) → **166.9k (2025)** | Apple Transparency Reports **[SA]** | Primary |

### Are the new apps succeeding?
- **Downloads are flat.** App Store downloads were 35.4B in 2025 (+3%) and 17.6B in H1 2026 (+2%) — Sensor Tower via NYT **[V]**. Supply roughly doubled while demand grew 2–3%.
- **Global downloads fell.** Appfigures puts 2025 downloads across both stores at 106.9B (−2.7%), while consumer spending rose to $155.8B (+21.6%) — TechCrunch 2026-01-14 **[SA]**.
- **RevenueCat, State of Subscription Apps 2026** (~Mar 2026) **[V]**, https://www.revenuecat.com/state-of-subscription-apps
  - New subscription apps per month went from about 2,000 (Jan 2022) to **14,700+ (Jan 2026)**.
  - Apps launched before 2020 earn **69%** of subscription revenue.
  - "Apps launched in 2025 or later (aka, the vibe coding era) account for just **3%**."
  - Only **17.3%** of new apps reach $1k monthly revenue, and **4.6%** reach $10k.
  - Caveat: newer cohorts have had less time to grow, which biases this against them.
- **AI apps churn faster.** Annual retention is 21.1% for AI apps versus 30.7% for others (TechCrunch 2026-03-10) **[SA]**.
- **Apple is pushing back:**
  - It blocked updates for the vibe-coding apps Replit and Vibecode (reported 2026-03-18).
  - It removed the app Anything (2026-03-26).
  - At WWDC (2026-06-09) it said it may remove apps that "do not attract customers" — https://techcrunch.com/2026/06/09/apple-says-it-may-remove-apps-from-the-app-store-if-they-dont-attract-users/ **[SA]**.

**Assessment.** Volume is up (independent trackers agree on direction, but their levels differ a lot). The quality and success data are vendor-sourced but consistent: the surge is landing almost entirely in the long tail.

## 3. Steam

**New releases per year** (SteamDB via a Wayback Machine snapshot from 2026-10-12) **[SA]**:

| Year | Releases | YoY |
|---|---|---|
| 2022 | 12,236 | — |
| 2023 | 14,020 | — |
| 2024 | 18,447 | — |
| 2025 | 21,253 | +15% |
| 2026, to Oct 12 | 20,947 | already about equal to all of 2025 |

- SteamDB revised its 2025 count upward by about 7.6% in spring 2026, so only compare figures from the same snapshot.
- GameDiscoverCo in Dec 2025 had 2025 at only about +2%.

**AI disclosure, from Sulka Haro's "Three years of AI on Steam"** (2026-07-13) **[V]**, https://fragwyz.substack.com/p/three-years-of-ai-on-steam. It is a census of 53,597 games released July 2023 to July 2026.
- **Who is adding the volume:** non-AI launches rose only from about 1,030 to about 1,320 per month. AI-flagged launches went from about 13 to about 530 per month. "60–90% of the growth in monthly Steam releases is AI-flagged games." About a third of launches now carry the AI flag.
- **AI share of sales:** about 10–27% in late 2025–2026, below its roughly 33% share of launches.
- **Concentration:** the top 1% of titles earn about 94% of revenue, the median reviewed game makes about $300, and 28% of games get zero reviews.
- From Haro's Part 2 **[SA]**: AI-flagged games reach ≥100 reviews at about **55%** of the non-AI rate, and average 77% positive reviews versus 81%.

**Caveat:** in January 2026 Valve narrowed disclosure to player-facing AI content, so AI *coding* is effectively exempt (PC Gamer 2026-01-16) **[SA]**. Steam's flag measures AI art, audio and text, not AI coding.

**Success:** GameDiscoverCo (2026-09-15) **[SA]** found that of 1,230 paid games released in January 2026, only 16 (1.3%) grossed more than $1M.

## 4. GitHub

**Octoverse 2025** (2025-10-28; covers roughly the 12 months to Aug/Sep 2025) **[SA]**, https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/
- 36.2M new developers (+23%).
- 121M new repos (630M total).
- 986M commits (+25%).
- 518.7M PRs merged (+29%).
- The Copilot coding agent produced more than 1M PRs between May and Sep 2025.
- **Octoverse 2026 is not yet published.** Last year's came out on Oct 28.

**My own GitHub search counts** (run 2026-10-14) **[V]**:

| September of… | Public PRs | New repos | Repos with ≥10 stars |
|---|---|---|---|
| 2023 | — | 3.37M | 17,245 |
| 2024 | 4.68M | 3.82M | 15,518 |
| 2025 | 7.61M | 5.34M | 15,109 |
| 2026 | **22.98M** | **11.86M** | 17,493 |

- **Claude Code's share of PRs:** PRs containing "Generated with Claude Code" numbered **4.23M in Sep 2026, about 18% of all public PRs** **[V]**.
- **Stars:** repos have tripled, but the absolute number with ≥10 stars is roughly flat. Older cohorts have had longer to gather stars, so per-repo star rates are confounded, but the absolute hit count has not tripled.
- **Commits with "Co-authored-by: Claude"** **[SA]**: about 0.5M/month in Sep 2025, rising to about 10M/month by mid-2026. The search API flags these results as incomplete, so treat them as rough.
- **SemiAnalysis** (2026-02-05) claims 4% of public commits are by Claude Code. The post is paywalled and its method is unseen.
- **Merge rates are not a quality signal.** Agent PRs merge at 89–94%, which mostly reflects people self-merging in personal repos.

**Academic studies of agent PRs** **[SA]**:
- AIDev (arXiv 2507.15003): agent PR acceptance of 35–64%, lagging humans by 15–40 percentage points on feature work.
- arXiv 2609.26847: merged agent PRs attract later fixes at 1.62× the odds of human PRs.

## 5. Package registries
- **PyPI:**
  - 130k+ new projects in 2025 (https://blog.pypi.org/posts/2025-12-31-pypi-2025-in-review/) **[SA]**.
  - March 2026 was more than 25k new packages, about 2× March 2025 (Answer.AI) **[V]**.
  - Net project growth: +93k in 2024, +122k in 2025, +196k in 2026 so far **[SA]**.
- **crates.io:** new crates were 35.7k (2024), 49.8k (2025), and **140.3k from Jan 1 to Oct 13, 2026** (from the crates.io database dump) **[SA]**. The lib.rs maintainer describes a "slopstorm" **[SA]**.
- **npm:** net growth went from about 27k/month (2025) to about 88k/month (Mar–Oct 2026). The counting method changed, so this series is not clean **[SA]**.
- **Spam and slop:**
  - The tea.xyz token spam campaign: 150k+ packages (Nov 2025).
  - Sonatype counted 454.6k malicious packages in 2025.
  - Slopsquatting: commercial models hallucinate package names at least 5.2% of the time (USENIX Security 2025).
  - All **[SA]**.

## 6. Product Hunt, extensions and startups
- **Product Hunt launches** (asanchez.dev, 2026-02-10, 267k launches with spam filtered) **[V]**: 41,380 (2024) → **80,791 (2025)**. January 2026 was +139% YoY.
- **Product Hunt, community post** (not official, ~Aug 2026) **[SA]**: 147k submissions so far in 2026, but only about 4.9k featured. Curation slots are flat while submissions surge.
- **VS Code Marketplace** (sub-agent's own API pull) **[SA]**:
  - New extensions per year: 12.6k (2023), 13.8k (2024), 22.0k (2025), and 32.9k in Jan–Sep 2026.
  - Extensions per quarterly cohort reaching ≥10k installs: **113 (Q1 2024) → 97 (Q1 2025) → 75 (Q1 2026)**, while cohort size tripled. Younger cohorts have had less time, which confounds this.
- **Chrome Web Store and Shopify:** not verified (blocked).
- **Stripe 2025 annual letter** (2026-02-24) **[SA]**:
  - Stripe Atlas incorporations +41%.
  - 20% of Atlas startups charged their first customer within 30 days (vs 8% in 2020).
  - The number of companies reaching $10M ARR within 3 months doubled versus 2024 (no absolute number given).
- **Census Business Formation Statistics**, Jan–Aug 2026 vs 2025 (my sub-agent's sums from census.gov/econ/bfs) **[SA]**:
  - All business applications: +13.5%.
  - Information sector (NAICS 51): **+34.7%**.
  - Information sector *high-propensity* applications (the ones likely to hire): **−6.4%**. That points to more solo or micro ventures, not employers.
- **Carta:** the solo-founder share of new startups reached 36.3% in H1 2025, up from 23.7% in 2019 **[SA]**.
- **Y Combinator** (Garry Tan to CNBC, 2025-03-15): the W25 batch grew 10% per week, and for about a quarter of companies 95% of code was AI-written. Self-reported claims.
- **Company claims:** Lovable reported 1M new projects per week and $500M ARR (June 2026); Cursor reportedly reached a $3B run-rate (May 2026). Company figures.

## 7. Productivity and quality studies
- **METR RCT, 2025.** Experienced open-source developers took 19% longer with AI (95% CI +2% to +39%) while believing they were about 20% faster.
- **METR, "We are Changing our Developer Productivity Experiment Design"** (2026-02-24) **[V]**, https://metr.org/blog/2026-02-24-uplift-update/
  - Follow-up study started Aug 2025, with 10 returning and 47 new developers, at $50/hr instead of $150/hr.
  - **Returning developers:** −18% task time, i.e. faster (CI −38% to +9%).
  - **New developers:** −4% (CI −15% to +9%).
  - METR calls this an "unreliable signal": developers increasingly refused to work without AI, 30–50% held back tasks from submission, and time measurement broke down for people running several agents at once.
  - METR's view: it is "likely that developers are more sped up… now," but its data is "only very weak evidence."
- **METR AI usage survey** (2026-05-11) **[V]**, n=349 technical workers:
  - Self-reported median change in the *value* of their work: 1.4–2×; self-reported speed: 3×.
  - METR staff gave the lowest answers of any group, and METR is explicitly skeptical of the magnitudes.
- **METR transcript analysis** (2026-02-17) **[V]**: estimated time savings of 1.5×–13× on Claude Code tasks. The author calls this a "soft upper bound," citing *task substitution* (doing nice-to-have tasks you otherwise wouldn't).
- **METR, task substitution** (2026-05-08) **[V]**: argues formally that "uplift on old tasks ≤ uplift in value ≤ uplift on new tasks."
- **METR on SWE-bench** (2026-03-10) **[V]**: about half of agent PRs that pass SWE-bench tests would not be merged by maintainers. Maintainer acceptance was about 24 percentage points below the automated grader.
- **Google RCT** (arXiv 2410.12944, Oct 2024) **[V]**: 96 engineers, about 21% faster on one task, with a wide confidence interval.
- **Microsoft/Accenture field experiments** (Cui et al.): about 26% more completed tasks **[not re-verified; cited from memory/secondary]**.
- **DORA 2025** (Google, Sep 2025) **[V]**, https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
  - 90% of respondents use AI; more than 80% believe it raised their productivity; 30% have little or no trust in AI code.
  - AI adoption is now positively associated with throughput but "continue[s] to have a negative relationship with software delivery stability."
  - DORA 2026: not found.
- **Faros AI, "AI Productivity Paradox" 2025** **[V]**, https://www.faros.ai/blog/ai-software-engineering
  - High-AI teams complete 21% more tasks and merge 98% more PRs.
  - But **PR review time is +91%**, bugs per developer +9%, and PR size +154%.
  - Faros sees no measurable organization-level improvement. Vendor telemetry.
- **Cursor difference-in-differences study** (He et al., arXiv 2511.04427, revised 2026-01-26) **[V]**
  - Cursor-adopting GitHub projects saw commits +55% and lines added +281% in the first month, but the velocity gain was **transient**.
  - **Persistent** effects: static-analysis warnings +30% and code complexity +41%, which in turn drive later slowdowns.
- **GitClear 2025** **[V]**: moved (refactored) code fell from 25% of changed lines (2021) to under 10% (2024); copy-pasted lines rose from 8.3% to 12.3%. GitClear's 2026 report exists (dated 2026-09-21) but is JS-rendered and I could not read it.
- **CodeRabbit, Dec 2025** **[V]**: 470 open-source PRs; AI-co-authored PRs had 10.83 issues per PR versus 6.45 for human PRs (1.7×). Small sample, AI authorship inferred, vendor.
- **CVEs published to NVD, Jan–Sep** (my queries) **[V]**:

  | Year | CVEs, Jan–Sep |
  |---|---|
  | 2023 | 23,033 |
  | 2024 | 29,575 |
  | 2025 | 36,824 |
  | 2026 | **74,838** |

  - Monthly in 2026: Jul 9.9k, Aug 12.7k, Sep 15.1k.
  - **This is ambiguous.** It could reflect AI-assisted vulnerability *discovery*, CNA or backlog effects, or more buggy code. I found no attribution.
- **Does existing software get better?** The only direct measure I found is Answer.AI's: release cadence of non-AI PyPI packages is unchanged, and packages still slow their releases as they age. The Cursor study shows only a transient velocity gain. I found no study showing fewer bugs or faster releases in established products.
- **Not verified:** Uplevel, Veracode, Harness/Cortex/LinearB 2026 reports, and outage data.

## 8. Economics
- **MIT NANDA, "The GenAI Divide"** (July 2025) **[V, PDF]**
  - Claim: "Despite $30–40 billion in enterprise investment… 95% of organizations are getting zero return."
  - Method: about 300 public initiatives reviewed, 52 interviews, 153 conference surveys, covering Jan–Jun 2025.
  - "Success" means a "marked and sustained productivity and/or P&L impact" as remarked by users or executives. This is weak methodology: a small convenience sample with a subjective definition.
- **NBER w34836, "Firm Data on AI"** (2026-02-24) **[V]**
  - About 6,000 executives in the US, UK, Germany and Australia.
  - **Nine in ten report no impact on employment or productivity over the past 3 years.**
  - They expect +1.4% productivity over the next 3 years.
- **Humlum & Vestergaard** (NBER w33777, May 2025) **[V]**: Danish administrative data show "precise null effects on earnings and recorded hours," ruling out effects larger than 2%.
- **Indeed software-development job postings** (FRED series IHLIDXUSTPSOFTDEVE; Feb 2020 = 100) **[V]**:
  - Low of **61.1 on 2025-05-17**, now **78.3 (2026-10-02)**.
  - Overall postings index: 103.8.
  - Software postings are recovering but remain far below the 2022 peak of about 225.
- **BLS employment** (via FRED) **[V]**:
  - Computer systems design (CES6054150001): 2,478.6k (Jan 2023) → 2,355.4k (Sep 2026), −5%.
  - Information sector: 3,061k → 2,739k.
- **Stanford "Canaries in the Coal Mine"** **[V]**: revised Aug 2026 with ADP payroll data through June 2026. Employment of 22–25-year-olds in AI-exposed jobs is now 19% below where it would be had it tracked less-exposed peers; older workers show no comparable gap.
- **Not verified:** BEA/BLS software-publisher output or productivity series, and McKinsey/BCG 2026 surveys.

## 9. Evidence on Meyvis's hypotheses

| Hypothesis | Evidence | Strength |
|---|---|---|
| Fewer bugs and better performance in existing software (H1) and better features (H2) | Mostly *against*: DORA finds lower stability; the Cursor study finds persistent complexity and warnings; Faros finds +9% bugs; CodeRabbit finds 1.7× issues; Answer.AI finds non-AI package release cadence unchanged | Moderate against; no positive measurement found |
| Political or approval subsystems are the bottleneck (H4) | Faros: PR review time +91%. Claude Code PRs wait a median 12.6h for a first human review (arXiv 2609.17598) **[SA]**. DORA: gains appear only with "fast feedback loops." Apple's review queue strained in 2026 | Moderate support, mostly correlational |
| Software is private, internal, or never shipped (H6) | Lovable: 1M projects per week and more than 50M total, versus about 1M new iOS apps a year (scale mismatch, my inference). Anthropic internal (Dec 2025) **[V]**: "27% of Claude-assisted work consists of tasks that wouldn't have been done otherwise… nice-to-have tools (e.g. interactive data dashboards)." GitHub: 81.5% of contributions are in private repos | Suggestive; nobody measures non-public software directly |
| More software rather than better (H7) | Strongly consistent: volume up 2–5× across app stores, Steam, PyPI, crates.io and GitHub; hits and revenue flat; METR's task-substitution framing | Strongest-supported hypothesis |
| Speedup captured as leisure (H8) | No direct evidence found. Humlum shows no change in recorded hours, which is consistent with either leisure or no gain | Unverified |
| Ephemeral software (H5) and using less software (H9) | No measurements found | Unverified |

## Reliability and gaps
- **Strongest evidence:**
  - Apple's own submission and removal numbers.
  - My GitHub, NVD and FRED queries.
  - The METR, NBER and Humlum papers.
  - Haro's Steam census.
- **Weaker evidence:**
  - Vendor app-store estimates: Sensor Tower, Appfigures and 42matters disagree on levels.
  - Vendor quality reports (Faros, CodeRabbit, GitClear).
  - MIT NANDA.
  - Company ARR claims.
- **Sub-agent items I did not re-check:** SteamDB year totals, crates.io/npm counts, the VS Code cohort numbers, the Census BFS sums, Apple Transparency Report figures, and the RevenueCat retention stat. Each is marked **[SA]** above.
- **Not found or not verified:**
  - Octoverse 2026 and DORA 2026 (neither appears to be out).
  - Readable GitClear 2026 content.
  - Chrome Web Store and Shopify series.
  - 2025–26 domain-registration data (Verisign's dnib.com was blocked).
  - St. Louis Fed time-savings figures (page returned empty).
  - Uplevel, Veracode, and McKinsey/BCG/Deloitte 2026.
  - Any measurement of what share of new apps or games are actually AI-coded.

[Turn 1]
[Message]
CHANGE OF SCOPE — drop the volume-of-new-apps angle (app store counts, Steam release counts, Product Hunt, Show HN, new repos, package counts). The user now wants evidence (2023–2026, published reports and studies, with URLs and dates) ONLY on these four questions:
(a) Are tech companies shipping more features/releases? e.g. studies of release cadence, changelog velocity, deployment frequency (DORA 2025/2026), app update frequency (Appfigures/Sensor Tower data on iOS/Android app *updates*), company statements with numbers (e.g. "X% of code written by AI", "shipped N× more"), any third-party measurement.
(b) Are game companies doing more hard technical work — more patches/bugfixes to old games, remasters/ports, engine upgrades, revived old titles, more frequent patches? Any reports (SteamDB, GDC State of the Industry 2026, press) with numbers.
(c) Is software getting more reliable? Uptime Institute annual outage analysis 2024/2025/2026, ThousandEyes outage counts, Catchpoint/IsDown/StatusGator reports, Downdetector/Ookla, crash-rate benchmarks (Embrace, Bugsnag, Instabug), CVE counts, incidents attributed to AI-generated code. Explicitly exclude or separately flag services seeing huge AI-driven traffic growth (GitHub, AI labs).
(d) Niche communities where new software is suddenly being built with AI: blindness/accessibility (AppleVis, NVDA add-ons, audio games, screen-reader users building their own tools), other disabilities (AAC), minority languages, ham radio, scientific niches, hobbyist niches. Look for articles, forum posts, podcasts with concrete examples and any counts.
Return a structured report with numbers + URLs per question, and reliability assessment. Be concise but thorough.

[Response]
# Evidence on four questions about AI coding and software output (2023–2026)

The overall picture:
- **Shipping:** code activity is up sharply, but measured delivery of features and releases is up only modestly or flat.
- **Old games:** no sign studios are doing more hard technical work on them; the surge is in fans reverse-engineering old games.
- **Reliability:** general infrastructure is flat to slightly better. Services under AI-driven load got clearly worse. The 2026 CVE surge mostly reflects AI *finding* bugs.
- **Niche communities:** the strongest positive signal. Several registries grew 2–10× in 2025–26, alongside visible backlash.

Web search engines were blocked, so this comes from direct fetches, news-site APIs, the Wayback Machine, and my own GitHub, Steam and NVD API counts. **[V]** = I re-checked it myself; everything else is from sub-agent reports.

---

## (a) Are tech companies shipping more features and releases?

**Third-party measurements (vendor telemetry and observational studies):**

| Source | Finding | Date / URL | Reliability |
|---|---|---|---|
| CircleCI 2026 State of Software Delivery (28M+ workflow runs) **[V]** | • Average daily workflow runs **+59%**, but the median team only +4% and the bottom quartile flat<br>• Median team: feature-branch throughput +15%, **main-branch (production) −7%**<br>• Main-branch success rate **70.8%**, the lowest in 5+ years | 2026-02-18, https://circleci.com/blog/five-takeaways-2026-software-delivery-report/ | Telemetry; strong |
| CircleCI Q2 2026 Pulse | Feature-branch throughput +7.7%; **main-branch flat** | 2026-07-08, https://circleci.com/blog/five-takeaways-2026-q2-pulse/ | Telemetry |
| DX longitudinal study (400+ companies, Nov 2024–Feb 2026) | • AI usage +65%; **median PR throughput +7.76%**<br>• DX concludes "5–15%" is the realistic gain | ~Mar–Apr 2026, https://getdx.com/report/ai-and-engineering-velocity-a-longitudinal-analysis/ | Telemetry; publication date approximate |
| DX Q2 2026 report | • AI-written share of code 34% → 52%<br>• **Share of time on new features ("innovation ratio") flat** | https://getdx.com/blog/the-state-of-ai-impact-in-engineering-q2-2026/ | Vendor |
| Jellyfish (1,000+ companies) | Full AI adoption ≈ **2× merged PRs**, but only **+27% feature-level ("epic") throughput** | 2026-07-27, https://jellyfish.co/blog/why-the-real-roi-from-ai-isnt-showing-up-yet/ | Telemetry |
| Faros AI (10k+ developers) | • +98% PRs merged, but review time +91%<br>• **No company-level change in throughput or DORA metrics** | 2025, https://www.faros.ai/blog/ai-software-engineering | Telemetry |
| LinearB 2026 benchmarks | • AI PRs wait **4.6× longer** for review<br>• Acceptance **32.7% for AI PRs vs 84.4%** for manual PRs | https://linearb.io/resources/software-engineering-benchmarks-report | Vendor |
| DORA 2024 → 2025 (survey) | • 2024: AI adoption associated with −1.5% throughput and −7.2% stability<br>• 2025: throughput now positively associated, stability still negative; effects small<br>• No 2026 State report yet | https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report | Cross-sectional survey |
| Answer.AI, release cadence of the top 15k PyPI packages **[V]** | Non-AI packages show an **unchanged** cadence (~10 releases/year); only AI-topic packages jumped | 2026-03-12, https://www.answer.ai/posts/2026-03-12-so-where-are-all-the-ai-apps.html | Observational, public data |
| Cursor difference-in-differences study, arXiv 2511.04427 **[V]** | • Lines added up 3–5× in month one; velocity gains gone after about 2 months<br>• Static-analysis warnings **+30%** and code complexity **+41%**, both persistent | v3 2026-01-26 | Strongest causal design here |
| Daniotti et al., arXiv 2506.08945 | AI writes ~29% of US Python functions; quarterly output only **+3.6%** | Nov 2025 | Large observational study |
| 42matters: share of the top 1,000 iOS apps updated each month (from Wayback snapshots) | ~70–78% since 2020, with **no break in the AI era**; it was 779 of 1,000 in Oct 2026 | https://42matters.com/apple-app-store-aso-with-app-update-frequency-statistics | Crude metric |
| Apple, submissions reviewed (new apps and updates combined) | 6.89M (2023) → 7.77M (2024) → 9.1M (2025) | Apple Transparency Reports; Newsroom 2026-05-20 | Primary, but updates aren't separated |

**Company claims (self-reported, no baselines):**
- **Google:**
  - >25% of new code AI-generated (Oct 2024 earnings).
  - Pichai: "10% engineering velocity increase" (Lex Fridman, Jun 2025).
- **Microsoft:** 20–30% of code AI-written (Nadella, 2025-04-29, CNBC).
- **Coinbase:** ~33% of code AI-written, target 50% (Aug 2025).
- **Anthropic internal survey:** +67% merged PRs per engineer per day; 27% of Claude-assisted work "wouldn't have been done otherwise" (2025-12-02, https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic **[V]**).
- **Spotify:** "50+ features" shipped in 2025 via Claude Code; top developers have not written code since December (TechCrunch, 2026-02-12).
- **Amazon Q:** Java upgrades saved "4,500 developer-years / $260M a year" (Jassy, Aug 2024).
- **Airbnb:** test migration in 6 weeks vs an estimated 1.5 years (2025).
- **Not verified:** Robinhood, Salesforce, Meta, OpenAI figures, and the "90% of code" claim.

**Assessment.** The best telemetry (CircleCI, DX, Jellyfish, Faros) all shows code activity up a lot, but production delivery up only about 0–27%, with a skew toward the top 5–10% of teams. Big wins are documented for **migrations and upgrades**, which are the "hard tedious work" category. Claims of shipping N× more features have no independent support.

---

## (b) Are game companies doing more hard technical work on old games?

**Industry surveys:**
- **GDC State of the Industry 2026** (2026-01-29, https://gdconf.com/article/gdc-2026-state-of-the-game-industry-reveals-impact-of-layoffs-generative-ai-and-more/):
  - 36% of respondents use generative AI. Of those, **47% use it for code assistance** and 35% for prototyping.
  - **52%** now say AI is bad for the industry (30% in 2025, 18% in 2024).
  - No data on patching or porting workloads.

**Patch frequency for old games** (sub-agent's own Steam News API count, Jan 1–Oct 13 each year; crude title regex, announcements are not builds):

| Sample | 2021 | 2023 | 2025 | 2026 |
|---|---|---|---|---|
| Top-100 games by owners, released before 2020: patch-titled posts | 607 | 481 | 526 | 548 |
| Random 300 older games: patch-titled posts | 797 | 562 | 472 | **430** |

Popular older games are back to roughly 2021 levels; the broad long tail keeps declining. **No AI-era increase.** SteamDB build counts were unobtainable because SteamDB blocks scripts.

**Remasters and remakes:** Wikipedia's list gives 34 (2020), 18 (2023), 25 (2024), 13 (2025), 12 (2026). No rise, but the list is low reliability because it is incomplete and lags.

**Steam Deck compatibility:**
- Verified games: 4,355 (Jan 2024) → **8,505** (Oct 2026).
- Playable games: 8,751 → 18,642.
- Steady growth, but largely driven by Valve's own testing and Proton work.

**Where the AI effect is visible: fan decompilation and recompilation of old games.**
- **Projects tracked on decomp.dev, by year the repo was created:**

  | Year | Projects | With AI-agent files (e.g. `CLAUDE.md`) |
  |---|---|---|
  | 2024 | 24 | 3 |
  | 2025 | 38 | 2 |
  | 2026 | **145** | **46** |

- **Examples:**
  - Snowboard Kids 2 decompilation with Claude: matched code ~25% → ~75% (https://blog.chrislewis.au/the-unexpected-effectiveness-of-one-shot-decompilation-with-claude/, 2025-11-28).
  - An unnamed FPS decompiled by ~16 agents to 99% of functions reconstructed, 83% byte-exact (https://momo5502.com/posts/2026-10-09-game-decompilation/, 2026-10-09).
  - Mario Kart Wii static recompilation (Tom's Hardware, Jul 2026).

**Mods:** Nexus Mods uploads for Jan–Oct were 97.7k (2024), 120.2k (2025), and **177.0k (2026, +47%)**. Growth was already 25–30% a year before. No AI attribution.

**Company claims:**
- **Square Enix:** wants AI handling "70% of QA and debugging by end-2027" (2025-11-06).
- **Capcom:** plans for an "AI generation" version of its RE Engine (2026-10-02).
- **Xbox Muse:** "back catalog" optimisation, aspirational (2025-02-19).
- **None of these companies has published a measured speed-up.**

**Counter-evidence:**
- Game layoffs: ~10.5k (2023), 14.6k (2024), 5.3k (2025), 4.6k (H1 2026).
- EA staff reportedly complain that its internal AI tool "wrote bad code" (PC Gamer, 2025-10-27).

**Assessment.** No evidence that studios are doing more patching, porting or remastering. There is clear evidence of a 2026 surge in **hobbyist** reverse-engineering of old games.

---

## (c) Is software getting more reliable?

**General infrastructure and apps:**
- **Uptime Institute Outage Analysis 2026** (2026-05-13): per-site outage rate fell for the **5th straight year**, but improvement is slowing; ~1 in 10 outages serious or severe (https://uptimeinstitute.com/about-ui/press-releases/uptime-announces-annual-outage-analysis-report-2026).
  - The 2025 edition: IT and network causes rose to 23% of impactful outages, driven by change management and misconfiguration.
  - AI is never cited as a cause.
- **ThousandEyes:**
  - Cloud-provider share of outages rose from 17% (2023) to 27% (2024).
  - H1 2025: 1.2k–2.1k global outages a month.
  - No clean full-year series; low comparability.
- **Catchpoint SRE Report 2025:** time spent on operations work rose for the first time in five years (median 25% → 30%).
- **StatusGator:** 2025 was "the worst year for mega-outages" in its data, with 23 major outages listed but no totals (https://statusgator.com/blog/2025-the-year-of-the-global-cloud-outage/).
- **Mega-outage root causes** (operators' own postmortems; **none attributed to AI-written code**):
  - AWS, Oct 20 2025: DynamoDB DNS race condition; 17M+ Downdetector reports.
  - Cloudflare, Nov 18 and Dec 5 2025: a feature-file size limit, then a parsing change.
  - CrowdStrike, 2024: faulty content update.
- **Mobile crash rates** (Instabug/Luciq): median crash-free sessions **99.94% (2023) → 99.95% (2024 data) → 99.95% (2026 benchmarks)**. Flat; the 2026 figures may reuse the 2025 data.

**CVEs:**
- Published CVEs: 28,817 (2023), 39,962 (2024), **48,185 (2025, +20.6%)** **[V]** (https://jerrygamblin.com/2026/01/01/2025-cve-data-review/).
- H1 2026 was 35,364, up 49.5% year on year.
- My NVD monthly counts: Jul 2026 9.9k, Aug 12.7k, Sep 15.1k.
- **Explanations point to AI-assisted discovery, not buggier code:**
  - NIST cites AI tools driving disclosure volume (CyberScoop, 2026-08-11).
  - Firefox shipped 423 bug fixes in Apr 2026 vs 31 a year earlier (TechCrunch, 2026-05-07).
  - curl's vulnerability reports ran 4–5× the 2024 rate.
  - Google paused its open-source vulnerability rewards over automated submissions (2026-10-04).
- Only 0.24% of H1 2026 CVEs are known to be exploited.

**Incidents attributed to AI-generated code or agents:**
- Replit agent deleted a production database (Jul 2025).
- Lovable CVE-2025-48757: missing database row-level security in generated sites.
- ~16k Supabase databases exposing personal data, linked to vibe-coded apps (TechCrunch, 2026-09-25).
- Amazon retail Sev-1 incidents, Mar 2026: an internal memo cited "Gen-AI assisted changes"; Amazon denies AI-written code was involved.
- **Cortex 2026 benchmark:** "incidents per PR +23.5%, change failure rate +30%". It surveyed only about 50 engineering leaders, so treat it as low reliability.

**Flagged separately: services under heavy AI-driven traffic growth.**
- **GitHub major incidents:** 32 (2023), 26 (2024), 34 (2025), **50 in Jan–Aug 2026**. That compares with 19 in Jan–Aug 2025.
  - GitHub says these were **capacity failures, not code changes**. It planned for 30× capacity, and monthly commits went from 1.4B to 2.9B (Apr–Aug 2026).
- **Anthropic status-page incidents:** 191 (2024) → 335 (2025) → 365 (Jan–Sep 2026).
- **OpenAI:** no historical count was obtainable.

**Assessment.** There is no aggregate evidence that software got more reliable because of AI. General metrics are flat or slowly improving, continuing pre-AI trends. Delivery-stability measures (DORA, CircleCI main-branch success) point slightly worse. The CVE surge reflects more bugs being found, not more bugs being created.

---

## (d) Niche communities building new software with AI

This is the strongest evidence of new, useful software. It is mostly exact registry counts; AI attribution is partly inferred from timing.

**Blind and screen-reader users:**
- **NVDA add-on store**, new add-ons per year: 65 (2024), 95 (2025), **253 (2026 YTD)**.
  - Submission issues for Jan–Oct 13: 950 (2024) → 854 (2025) → **2,345 (2026)** **[V]**.
  - An NV Access developer proposed letting users hide add-ons because the store is crowded (nvaccess/nvda#20402, 2026-06-25 **[V]**). A commenter cites "vibe-coded untested" add-ons.
- **Double Tap podcast:** episodes mentioning vibe coding or Claude went from 1 (all of 2025) to **44 (2026)**. Examples:
  - Blind RSS reader (2026-01-21).
  - NVDA add-ons the host built with Claude (Apr 2026).
  - "How Blind Developers Are Creating with AI" (2026-07-20).
  - A user with no coding experience building a Windows-on-Mac tool (2026-08-18).
- **AppleVis "Blind Developer Showcase"** podcasts (Jul–Aug 2026) describe AI-assisted iOS apps. Blind users' push for a screen-reader mode in Claude Code: anthropics/claude-code#11002, #36765.
- **Example projects:**
  - `oasis1701/msfs-blind-assist`: lets blind users fly Microsoft Flight Simulator.
  - A screen-reader mod for the game *Knights of the Old Republic*.
- **GitHub repos mentioning "NVDA add-on":** 56 (2024) → 143 (2025) → **632 (2026)**. The baseline of all repos roughly doubled.

**Home automation and note-taking (exact registry counts):**
- **Home Assistant community store (HACS) integrations:** 975 (Jan 2024) → 1,076 (Jan 2025) → 1,895 (Jan 2026) → **3,262 (Oct 2026)** **[V]**.
  - That is +101 in 2024, then +819 and +1,367.
  - How-To Geek criticises "vibe-coded" paid integrations (2026-03-16).
- **Obsidian plugins:** 2,100 → 2,705 → 8,876. Partly a process change (a new directory in May 2026), after a review backlog of 3+ months.
- **Raycast extensions:** steady growth, roughly +550–650 a year until 2026, which added +928 in 9.5 months.

**Ham radio and mesh networking:**
- IEEE Spectrum's Stephen Cass built "Spectel", ham-radio teletext, with Claude: "would never have come about without vibe coding" (https://spectrum.ieee.org/reviving-teletext-for-ham-radio, 2026-04-22).
- The MeshCore project split over undisclosed vibe coding (https://blog.meshcore.io/2026/04/23/the-split).
- Repos with the `amateur-radio` topic: 103 (2024) → **592 (2026)**.

**Science:**
- *Nature*, "How to vibe code in science" (2026-05-12).
- *Nature Methods* commentary on AI disrupting research software, citing the microscopy tool MOSS (Sep 2026).
- **Anthropic survey of 1,260 social scientists** (2026-05-27): 81% have used generative AI, but only **20% use coding agents weekly**. The sample was recruited with free Claude Max accounts, so it is self-selected.

**Other examples:**
- **AAC and other disabilities:** small projects only (AAC web apps, dyslexia tools, sign-language encyclopedia); thin evidence.
- **Minority languages:** small examples only (Māori kids' game, Hawaiian chant tutor, Welsh speech-to-text). No community keyboard or spellchecker found.
- **Pebble:** 2,120 apps and watchfaces for the new watches (Jul 2026). Confounded by the hardware revival.
- **Retro computing:** an LLM-written USB 3.0 driver for Windows 98 (Hackaday, 2026-09-23).

**Backlash:**
- Codeberg voted 358–144 to ban largely LLM-generated projects (Jul 2026).
- Panic banned AI in Playdate season 3 games.
- The MeshCore split, NVDA store crowding, and the Obsidian backlog.

**Assessment.** This is the clearest "new software exists" signal. Long-tail registries roughly flat or growing linearly before 2025 jumped 2–10× in 2025–26, with first-person accounts, especially from blind users, of people who previously couldn't build tools now building them. Quality is unmeasured, and maintainers are already pushing back on volume.

---

**Not obtained:**
- App-update counts from Appfigures or Sensor Tower.
- A DORA 2026 State report.
- SteamDB build counts.
- Uptime's 2024 outage figures.
- Crash benchmarks from Embrace, Bugsnag or Sentry.
- Reddit, AppleVis and audiogames.net search (blocked).
- Paywalled *Nature* article bodies.