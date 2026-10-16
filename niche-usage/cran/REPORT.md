# CRAN new-package usage cohorts

Analysis date: 2026-10-15. Source folder: `cran`. Inputs are cached under `cache/`; derived tables are under `data/`; the reproducible script is `cran_analysis.py`.

## Method

- Creation cohorts use every package in `https://crandb.r-pkg.org/-/allall`, including archived packages present in CRAN DB. First publication is the earliest non-`archived` timestamp in each package timeline. This recovers current plus archived packages; packages fully removed from CRAN DB, if any, are not recoverable.
- Downloads use cranlogs package totals for days 31-180 after first publication (`first_date + 31` through `first_date + 180`, 150 calendar days), skipping the first 30 days.
- The latest cranlogs day available was `2026-10-13`. Therefore complete equal-age usage is available only for packages first published through `2026-04-16`; 2026Q2 is partial and 2026Q3 has supply only.
- To adjust for the changing RStudio/Posit mirror share and overall mirror traffic, each package's count is scaled to the median 2022-2024 150-day total mirror traffic: `851,097,408` downloads. Tables below apply the requested 500 / 2k / 20k thresholds to these scaled counts. Raw counts are retained in `data/cohorts_*.csv`.
- Threshold note: after looking at the distribution, 500 is mostly a cranlogs/bot floor: roughly 98% of mature packages clear it in most baseline cohorts. I keep it because it was requested, but treat 2k as the modest bar and 20k as the high bar.
- Bioconductor was not included in this CRAN run. Its package download stats are cheap to fetch, but reconstructing first-publication dates for current plus archived Bioconductor packages is a separate, non-cheap provenance problem compared with CRAN DB timelines.

## Cohort table, half-years

|cohort|created|eligible|≥500 n/%|≥2k n/%|≥20k n/%|archived|
|---|---|---|---|---|---|---|
|2021H1|1293|1293|1279 / 98.9%|726 / 56.1%|12 / 0.9%|264|
|2021H2|1077|1077|1067 / 99.1%|336 / 31.2%|5 / 0.5%|198|
|2022H1|1102|1102|1084 / 98.4%|102 / 9.3%|5 / 0.4%|170|
|2022H2|954|954|936 / 98.1%|64 / 6.7%|6 / 0.6%|119|
|2023H1|1064|1064|1036 / 97.4%|96 / 9.0%|3 / 0.3%|104|
|2023H2|942|942|926 / 98.3%|103 / 10.9%|17 / 1.8%|69|
|2024H1|1053|1053|1037 / 98.5%|295 / 28.0%|9 / 0.9%|52|
|2024H2|975|975|958 / 98.3%|248 / 25.4%|5 / 0.5%|69|
|2025H1|1074|1074|1057 / 98.4%|228 / 21.2%|10 / 0.9%|37|
|2025H2|1151|1151|1010 / 87.8%|56 / 4.9%|10 / 0.9%|23|
|2026H1|1991|1040|1015 / 97.6%|43 / 4.1%|7 / 0.7%|27|

Baseline 2022-2024 mean per half-year: 1,015 created; 996 above 500, 151 above 2k, and 7.5 above 20k after mirror normalization. 2025H2 had 1,151 created but only 56 above 2k and 10 above 20k. 2026H1 supply jumped to 1,991 created, but only 1,040 packages had complete usage windows; among those, 43 cleared 2k and 7 cleared 20k.

## New packages per quarter / supply growth

|quarter|created|eligible|≥2k scaled|≥20k scaled|archived|
|---|---|---|---|---|---|
|2021Q1|707|707|345|10|141|
|2021Q2|586|586|381|2|123|
|2021Q3|579|579|272|5|114|
|2021Q4|498|498|64|0|84|
|2022Q1|618|618|64|3|88|
|2022Q2|484|484|38|2|82|
|2022Q3|489|489|31|2|61|
|2022Q4|465|465|33|4|58|
|2023Q1|524|524|42|2|55|
|2023Q2|540|540|54|1|49|
|2023Q3|478|478|44|8|35|
|2023Q4|464|464|59|9|34|
|2024Q1|522|522|95|5|26|
|2024Q2|531|531|200|4|26|
|2024Q3|471|471|72|4|27|
|2024Q4|504|504|176|1|42|
|2025Q1|528|528|80|7|19|
|2025Q2|546|546|148|3|18|
|2025Q3|562|562|21|5|14|
|2025Q4|589|589|35|5|9|
|2026Q1|879|879|38|5|18|
|2026Q2|1112|161|5|2|9|
|2026Q3|1158|0|0|0|5|

CRAN supply growth is the clear signal: the 2022-2024 quarterly average was about 508 new packages, while 2026Q1/Q2/Q3 were 879, 1,112 and 1,158. Usage cannot yet be judged for most of 2026Q2 and all of 2026Q3 because their day-180 windows have not elapsed.

## Top recent packages by day-31-to-180 downloads

Recent means first publication in 2025H2 or later. `scaled` is downloads normalized to 2022-2024 median mirror traffic.

|#|pkg|first|raw|scaled|judgement|AI?|AI-built?|
|---|---|---|---|---|---|---|---|
|1|otel|2025-07-31|2265905|1615914|New R implementation of the established OpenTelemetry observability standard, by r-lib; more platform plumbing than a standalone niche end-user tool|No|No statement found in CRAN description or README|
|2|tailor|2025-08-25|180527|126879|New package in the established tidymodels ecosystem for ML post-processing/calibration|No|No statement found in CRAN description or README|
|3|linreg|2026-04-16|105375|78914|Apparently new generic statistics/teaching-style package; no project URL in CRAN metadata|No|No statement found in CRAN description|
|4|contentanalysis|2025-10-30|96901|69921|Genuine niche research/bibliometrics tool for PDF citation/content analysis|No|No statement found in CRAN description|
|5|metabook|2026-03-04|89441|66393|Companion data/code for an established book/new edition, not a standalone new software hit|No|No statement found in CRAN description|
|6|aisdk|2026-03-31|80759|60549|Genuine AI/LLM infrastructure package for R; provider-neutral runtime, tools and agents|Yes|No AI-built claim found in CRAN description or README|
|7|otelsdk|2025-09-10|75274|53526|New R SDK/exporter for the established OpenTelemetry standard; paired with otel|No|No statement found in CRAN description|
|8|arg|2026-04-09|74055|55375|Genuine small R developer-utility package|No|No statement found in CRAN description|
|9|autoann|2026-01-15|71805|53312|Genuine statistical/ML forecasting package; neural-network method rather than LLM/AI-coding themed|Borderline ML|No statement found in CRAN description|
|10|readepi|2025-10-01|65310|46810|Genuine niche epidemiology/data-import tool in the Epiverse-TRACE ecosystem|No|No statement found in CRAN description|
|11|fluxtools|2025-07-09|62605|47718|Genuine niche environmental-science/flux-tower QA tool|No|No statement found in CRAN description|
|12|mini007|2025-09-05|58004|40890|Genuine AI/LLM multi-agent package for R|Yes|No AI-built claim found in CRAN description or README|

Spot checks used CRAN descriptions and READMEs where linked for `otel`, `tailor`, `aisdk`, and `mini007`. `aisdk` and `mini007` are explicitly AI/LLM-themed, but I found no claim that any top package was itself AI-built.

## Confounders

- Cranlogs measures one mirror, not all CRAN downloads. Its share and bot traffic change over time; normalization by total mirror traffic is necessary and materially changes the 2k counts in 2025-2026.
- The 500-download threshold appears dominated by background/bot/check traffic: it is too low to identify real adoption on CRAN.
- CRAN review policy, queue length, reverse-dependency checks and acceptance practices may affect creation timing independently of AI coding.
- Archived packages are recoverable through CRAN DB here, but completely removed packages would be missed.
- Some top packages are new CRAN listings for established standards, books or ecosystems rather than wholly new grassroots tools.
- Recent cohorts are right-censored: 2026Q2 is partial and 2026Q3 has no complete equal-age windows.

## Verdict

CRAN shows a large 2026 supply shock: quarterly new-package counts roughly doubled versus 2022-2024. After equal-age measurement and mirror-traffic normalization, this did not translate into more modestly used packages: the 2k-download count fell in 2025H2/eligible 2026H1, while 20k-download hits stayed flat at roughly baseline levels. For CRAN, the evidence supports "more software is being published" and "no more big hits," but not the stronger claim that AI has already produced many more genuinely adopted niche R packages.
