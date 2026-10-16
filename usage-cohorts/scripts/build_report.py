#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

BASE = Path.home() / "Code/where-is-the-software/usage-cohorts"
DATA = BASE / "data"

def read_csv(name):
    with (DATA/name).open() as f:
        return list(csv.DictReader(f))

def md_table(rows, cols, labels=None):
    labels = labels or {c:c for c in cols}
    out = ["| " + " | ".join(labels.get(c,c) for c in cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        vals=[]
        for c in cols:
            vals.append(str(r.get(c, "")))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)

def quarter_filter(rows, start="2021Q1", end="2026Q2"):
    return [r for r in rows if start <= r["cohort"] <= end]

def num(v):
    return None if v == "" or v is None else int(v)

def avg(rows, col, years=None, cohorts=None):
    xs=[]
    for r in rows:
        if years and r["cohort"][:4] not in years: continue
        if cohorts and r["cohort"] not in cohorts: continue
        v=num(r.get(col,""))
        if v is not None: xs.append(v)
    return sum(xs)/len(xs) if xs else None

def fmt(x):
    if x is None: return "n/a"
    if abs(x) >= 100: return f"{x:,.0f}"
    return f"{x:.1f}"

def main():
    hf_eq = read_csv("homebrew_formula_equal_age_30d.csv")
    hc_cur = read_csv("homebrew_cask_current_30d.csv")
    hc_eq = read_csv("homebrew_cask_equal_age_30d.csv")
    crates = read_csv("crates_cohorts.csv")
    vscode = read_csv("vscode_cohorts.csv")
    summary = [
        {"ecosystem":"Homebrew formulae", "metric":"equal-age 30d installs ≥1k", "2022-24 avg/q":fmt(avg(hf_eq,"ge_1000", years={"2022","2023","2024"})), "2025 avg/q":fmt(avg(hf_eq,"ge_1000", years={"2025"})), "2026H1 avg/q":fmt(avg(hf_eq,"ge_1000", cohorts={"2026Q1","2026Q2"})), "verdict":"above trend (Q2 not mature)"},
        {"ecosystem":"Homebrew formulae", "metric":"equal-age 30d installs ≥10k", "2022-24 avg/q":fmt(avg(hf_eq,"ge_10000", years={"2022","2023","2024"})), "2025 avg/q":fmt(avg(hf_eq,"ge_10000", years={"2025"})), "2026H1 avg/q":fmt(avg(hf_eq,"ge_10000", cohorts={"2026Q1","2026Q2"})), "verdict":"above trend, small-N"},
        {"ecosystem":"Homebrew casks", "metric":"current 30d installs ≥1k", "2022-24 avg/q":fmt(avg(hc_cur,"ge_1000", years={"2022","2023","2024"})), "2025 avg/q":fmt(avg(hc_cur,"ge_1000", years={"2025"})), "2026H1 avg/q":fmt(avg(hc_cur,"ge_1000", cohorts={"2026Q1","2026Q2"})), "verdict":"2026 up, age-confounded"},
        {"ecosystem":"crates.io", "metric":"current recent downloads ≥1k", "2022-24 avg/q":fmt(avg(crates,"recent_ge_1000", years={"2022","2023","2024"})), "2025 avg/q":fmt(avg(crates,"recent_ge_1000", years={"2025"})), "2026H1 avg/q":fmt(avg(crates,"recent_ge_1000", cohorts={"2026Q1","2026Q2"})), "verdict":"yes, but bots/CI"},
        {"ecosystem":"crates.io", "metric":"total downloads ≥100k", "2022-24 avg/q":fmt(avg(crates,"total_ge_100000", years={"2022","2023","2024"})), "2025 avg/q":fmt(avg(crates,"total_ge_100000", years={"2025"})), "2026H1 avg/q":fmt(avg(crates,"total_ge_100000", cohorts={"2026Q1","2026Q2"})), "verdict":"not yet; age-confounded"},
        {"ecosystem":"VS Code Marketplace", "metric":"current installs ≥10k", "2022-24 avg/q":fmt(avg(vscode,"installs_ge_10000", years={"2022","2023","2024"})), "2025 avg/q":fmt(avg(vscode,"installs_ge_10000", years={"2025"})), "2026H1 avg/q":fmt(avg(vscode,"installs_ge_10000", cohorts={"2026Q1","2026Q2"})), "verdict":"no"},
    ]
    report = []
    report.append("# Usage cohorts: count only what people use\n")
    report.append("Generated on 2026-10-15. Data CSVs are in `data/`; reproducible collection code is in `scripts/collect_usage_cohorts.py`. Large inputs were streamed or held only transiently in the session scratch area, which was deleted after collection; no raw crates dump or cloned Homebrew repository is stored here.\n")
    report.append("## Three-sentence bottom line\n")
    report.append("Counting only items with visible usage does not produce a universal 2025–26 boom. The best positive evidence is in developer package managers: Homebrew formulae at equal-ish age and crates.io recent downloads both have more used new items than the 2022–24 trend, although Homebrew is already curated and crates downloads are heavily bot/CI-inflated. VS Code Marketplace shows the opposite pattern: new extension supply explodes, but the absolute count clearing 10k installs is below trend, so the AI-era surge is mostly not turning into widely installed extensions yet.\n")
    report.append("## At-a-glance trend comparison\n")
    report.append(md_table(summary, ["ecosystem","metric","2022-24 avg/q","2025 avg/q","2026H1 avg/q","verdict"]) + "\n")

    report.append("## Method\n")
    report.append("- **Homebrew formulae/casks.** Usage comes from `https://formulae.brew.sh/api/analytics/install/30d.json` and `.../cask-install/30d.json`; creation quarter is the first git commit adding the formula/cask file in `Homebrew/homebrew-core` or `Homebrew/homebrew-cask`, using blobless clones and rename detection so sharding moves do not count as new creations. Equal-age formula counts use Wayback snapshots nearest six months after each cohort closes; this means items are roughly 6–9 months old. Cask Wayback coverage is sparse before late 2025, so cask equal-age rows are mostly blank. Homebrew's inclusion process is itself a quality/notability filter: acceptable formulae/casks must be stable, maintained, and fit documented project rules (`docs.brew.sh/Acceptable-Formulae`, `docs.brew.sh/Acceptable-Casks`).\n")
    report.append("- **crates.io.** The official `static.crates.io/db-dump.tar.gz` was streamed, reading only `crates.csv`, `crate_downloads.csv`, `versions.csv`, and `version_downloads.csv`. Crates with no non-yanked versions were excluded; I did not apply a stronger name-squatting classifier because doing so reliably requires semantic/project inspection. `crate_downloads` is lifetime downloads; `version_downloads` covered 2026-07-16 through 2026-10-15 here and is treated as current ~90-day usage.\n")
    report.append("- **VS Code Marketplace.** The public `extensionquery` API was paged by `publishedDate` for `Microsoft.VisualStudio.Code` targets, deduped by extension id, and current install/rating statistics were counted. I found no practical equal-age historical install source.\n")
    report.append("- **Skipped PyPI/npm.** Equal-age package downloads are possible in principle, but getting unbiased random creation cohorts requires broad registry/change-feed enumeration or a third-party index; doing that cheaply and reproducibly was less feasible than completing the three higher-priority ecosystems.\n")

    report.append("## Homebrew formulae: equal-age 30-day installs\n")
    report.append(md_table(hf_eq, ["cohort","created","ge_100","ge_1000","ge_10000","target_snapshot_date","analytics_end_date","days_from_target"], {"cohort":"cohort","created":"N created","ge_100":"≥100","ge_1000":"≥1k","ge_10000":"≥10k","target_snapshot_date":"target","analytics_end_date":"snapshot 30d end","days_from_target":"days off"}) + "\n")
    report.append("**Verdict:** yes for formulae. The 2022–24 average was 10.7 new formulae per quarter reaching ≥1k installs at equal-ish age; 2025 averaged 23.3 and 2026Q1 had 31 (2026Q2 is not old enough).\n")

    report.append("## Homebrew casks: current and sparse equal-age 30-day installs\n")
    report.append("Current 30-day installs, age-confounded:\n")
    report.append(md_table(hc_cur, ["cohort","created","ge_100","ge_1000","ge_10000"], {"cohort":"cohort","created":"N created","ge_100":"≥100","ge_1000":"≥1k","ge_10000":"≥10k"}) + "\n")
    report.append("Equal-age rows where Wayback had a snapshot; blank threshold cells mean no snapshot was found:\n")
    report.append(md_table(hc_eq, ["cohort","created","ge_100","ge_1000","ge_10000","target_snapshot_date","analytics_end_date","days_from_target"], {"cohort":"cohort","created":"N created","ge_100":"≥100","ge_1000":"≥1k","ge_10000":"≥10k","target_snapshot_date":"target","analytics_end_date":"snapshot 30d end","days_from_target":"days off"}) + "\n")
    report.append("**Verdict:** weak yes only in current data. Casks with ≥1k current 30-day installs average 11.0 per quarter in 2026H1 versus 4.2 in 2022–24, but cask snapshots are too sparse for a clean equal-age test and 2024Q2 is distorted by a mass Google Fonts addition.\n")

    report.append("## crates.io: lifetime and current recent downloads\n")
    report.append(md_table(crates, ["cohort","created_non_yanked","total_ge_1000","total_ge_10000","total_ge_100000","recent_ge_100","recent_ge_1000","recent_ge_10000"], {"cohort":"cohort","created_non_yanked":"N created","total_ge_1000":"lifetime ≥1k","total_ge_10000":"lifetime ≥10k","total_ge_100000":"lifetime ≥100k","recent_ge_100":"recent ≥100","recent_ge_1000":"recent ≥1k","recent_ge_10000":"recent ≥10k"}) + "\n")
    report.append("**Verdict:** yes for current usage, no for high lifetime thresholds yet. Recent ≥1k-download crates jump from a 2022–24 average of 1,287 per quarter to 4,649 in 2026H1, but lifetime ≥100k-download crates are below trend because young crates have had little time to accumulate downloads; bot/CI traffic is a major confounder.\n")

    report.append("## VS Code Marketplace: current installs\n")
    report.append(md_table(vscode, ["cohort","published","installs_ge_1000","installs_ge_10000","installs_ge_100000","rating_count_ge_10"], {"cohort":"cohort","published":"N published","installs_ge_1000":"≥1k installs","installs_ge_10000":"≥10k installs","installs_ge_100000":"≥100k installs","rating_count_ge_10":"≥10 ratings"}) + "\n")
    report.append("**Verdict:** no. Published extensions rose sharply in 2025–26, but ≥10k-install extensions fell from a 2022–24 average of 157 per quarter to 81 in 2025 and 60 in 2026H1; this is age-confounded but still a poor sign for broad adoption.\n")

    report.append("## Confounders and caveats\n")
    report.append("- **Age:** Current install/download counts favor old cohorts; equal-age was only practical for Homebrew formulae via Wayback.\n")
    report.append("- **Bots/CI:** crates.io download counts include automated builds, dependency resolution, mirrors, and CI, so they are usage-ish rather than human adoption.\n")
    report.append("- **Curated gates:** Homebrew formulae/casks already pass notability/maintainership rules, so their creation counts are not raw software supply.\n")
    report.append("- **Marketplace noise:** VS Code has spam/import waves (notably 2022Q1–Q2) and extensions can be installed by automation; ratings are included as a second, stricter but much lower-volume signal.\n")
    report.append("- **Historical gaps:** Wayback did not have enough cask analytics snapshots for 2021–24 or several 2025–26 targets; blank cells are unknown, not zero.\n")

    (BASE/"REPORT.md").write_text("\n".join(report))

if __name__ == "__main__":
    main()
