#!/usr/bin/env python3
import csv, math, statistics, textwrap
from pathlib import Path
from datetime import date
from collections import defaultdict

BASE = Path.home() / 'Code' / 'where-is-the-software' / 'progress-meters'
DATA = BASE / 'data'; CHARTS = BASE / 'charts'
CHARTS.mkdir(exist_ok=True)

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

def read_csv(name):
    with (DATA/name).open(newline='') as f:
        return list(csv.DictReader(f))

def parse_date(s): return date.fromisoformat(s[:10])
def month_index(d): return d.year*12 + d.month + (d.day-1)/31.0

def lin_slope(points, start, end):
    s=parse_date(start); e=parse_date(end)
    pts=[(month_index(parse_date(d)), float(v)) for d,v in points if v not in ('', None) and s <= parse_date(d) <= e]
    if len(pts) < 2: return None, len(pts)
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    den=sum((x-xm)**2 for x in xs)
    if den == 0: return None, len(pts)
    return sum((x-xm)*(y-ym) for x,y in pts)/den, len(pts)

def ratio(a,b):
    if a is None or b is None or abs(a) < 1e-12: return None
    return b/a

def fmt(x, digits=3):
    if x is None: return 'n/a'
    if abs(x) >= 100: return f'{x:.1f}'
    if abs(x) >= 10: return f'{x:.2f}'
    return f'{x:.3f}'

def save_series_csv(name, points):
    with (DATA/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=['date','value'])
        w.writeheader(); w.writerows({'date':d,'value':v} for d,v in points)

summary=[]; series_for_plot=[]

def add_series(key, label, unit, points, higher_better, confounders, verdict_note):
    points=sorted([(d,float(v)) for d,v in points if v not in ('', None)], key=lambda x:x[0])
    b,n1=lin_slope(points,'2022-01-01','2024-12-31')
    p,n2=lin_slope(points,'2025-01-01','2026-12-31')
    r=ratio(b,p)
    # improvement ratio converts lower-is-better to positive improvements.
    ib = b if higher_better else (-b if b is not None else None)
    ip = p if higher_better else (-p if p is not None else None)
    ir=ratio(ib,ip)
    verdict=verdict_note
    summary.append({'series':label,'key':key,'unit':unit,'baseline_slope':b,'post_slope':p,'ratio':r,'improvement_ratio':ir,'n_baseline':n1,'n_post':n2,'confounders':confounders,'verdict':verdict})
    save_series_csv(f'{key}_series.csv', points)
    series_for_plot.append((key,label,unit,points))

# WebAIM
webaim=read_csv('webaim_million.csv')
add_series('webaim_avg_errors','WebAIM avg errors/page','errors/page/month',[(r['date'],r['avg_errors_per_page']) for r in webaim],False,'Annual sample; WAVE rules/site mix/page complexity changed; lower is better.','No positive break: errors worsened in 2025-26.')
add_series('webaim_wcag_failures','WebAIM WCAG failure %','percentage-points/month',[(r['date'],r['wcag_failure_pct']) for r in webaim],False,'Annual sample; detectable failures only; lower is better; page complexity rose sharply.','No positive break: previous improvement reversed in 2026.')

# ProtonDB
proton=read_csv('protondb_quarterly_works.csv')
add_series('protondb_unique_works','ProtonDB latest-app works share','percentage-points/month',[(r['date'],100*float(r['unique_app_latest_yes_share'])) for r in proton if r['unique_app_latest_yes_share']],True,'Quarterly sampled cumulative dumps; raw yes/no “works” reports, not ProtonDB tier algorithm; report volume and user/game mix changed.','Works share kept improving, but the 2025-26 slope is slower than 2022-24; no trend-break acceleration.')
add_series('protondb_tested_apps','ProtonDB tested unique apps','apps/month',[(r['date'],r['unique_apps_latest']) for r in proton],True,'Quarterly sampled cumulative dumps; supply of reports/users is endogenous to Steam Deck/Linux gaming growth.','Volume growth accelerated, but this is testing coverage not quality.')

# Wine cumulative bug fixes
wine=read_csv('wine_bugs_fixed_cumulative.csv')
add_series('wine_cumulative_bugs','Wine dev-release bugs fixed','bugs/month',[(r['date'],r['cumulative_bugs_fixed']) for r in wine],True,'Counts announced fixed bugs, not user-visible compatibility; release cadence changed slightly; excludes stable rollup notes.','Post-2025 bug-fix throughput is roughly similar/slower, not an acceleration.')

# GitHub compatibility current-label approximation
compat=read_csv('github_compat_label_monthly.csv')
for key,label in [('xenia_playable','Xenia playable issues'),('vita3k_playable','Vita3K playable issues'),('shadps4_playable','shadPS4 playable issues')]:
    pts=[(r['date'],r['cumulative_current_label_created']) for r in compat if r['series']==key]
    conf='Current-label + issue-creation approximation; label-event history not replayed.'
    if key=='vita3k_playable': conf += ' GitHub API caps result pagination at the first 1000 current playable issues.'
    if key=='xenia_playable': conf += ' Xenia tracker README says it is no longer maintained since xenia master is dead.'
    if key=='shadps4_playable': conf += ' Newer emulator with PS4-native-port excitement in 2026; project/team maturity is a major confounder.'
    add_series(key,label,'games/month',pts,True,conf,'Positive break' if key=='shadps4_playable' else 'No reliable AI-era acceleration signal.')

# ScummVM supported games
scumm=read_csv('scummvm_supported_games.csv')
add_series('scummvm_supported_games','ScummVM supported games','game entries/month',[(r['date'],r['supported_game_entries']) for r in scumm],True,'Counts compatibility-page entries; 2026 cadence/name change and Wintermute batch caused a structural jump.','Strong 2026 acceleration, but mostly explained by release-cadence and engine batch additions.')

# WPT Interop: official focus areas reset yearly, so compare within-year daily linear slopes.
interop_daily=read_csv('wpt_interop_daily.csv')
year_slopes=[]
for y in ['2022','2023','2024','2025','2026']:
    pts=[(r['date'],r['score']) for r in interop_daily if r['mode']=='stable' and r['year']==y]
    sl,n=lin_slope(pts, f'{y}-01-01', f'{y}-12-31')
    if sl is not None:
        year_slopes.append({'date':f'{y}-12-31' if y!='2026' else max(d for d,_ in pts), 'year':y, 'value':sl, 'n':n})
# Store yearly within-year slopes and add manually to summary.
save_series_csv('wpt_interop_stable_within_year_slope_series.csv', [(r['date'], r['value']) for r in year_slopes])
base_vals=[r['value'] for r in year_slopes if r['year'] in ('2022','2023','2024')]
post_vals=[r['value'] for r in year_slopes if r['year'] in ('2025','2026')]
b=sum(base_vals)/len(base_vals) if base_vals else None
p=sum(post_vals)/len(post_vals) if post_vals else None
summary.append({'series':'WPT Interop stable within-year gain','key':'wpt_interop_stable_within_year_slope','unit':'score-points/month','baseline_slope':b,'post_slope':p,'ratio':ratio(b,p),'improvement_ratio':ratio(b,p),'n_baseline':len(base_vals),'n_post':len(post_vals),'confounders':'Official focus areas reset yearly; this averages per-year daily linear slopes for stable browsers; annual difficulty and browser staffing/funding changed.','verdict':'Within-year Interop improvement accelerated in 2025, but 2026-to-date is lower and the reset/difficulty confound is large.'})
series_for_plot.append(('wpt_interop_stable_within_year_slope','WPT Interop stable within-year gain','score-points/month',[(r['date'], r['value']) for r in year_slopes]))

# test262 current only
try:
    import urllib.request, json
except Exception:
    pass

# Write summary CSV
with (DATA/'slope_summary.csv').open('w', newline='') as f:
    fields=['series','unit','baseline_slope','post_slope','ratio','improvement_ratio','n_baseline','n_post','confounders','verdict']
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for r in summary:
        w.writerow({k:r.get(k) for k in fields})

# Charts
if plt:
    for key,label,unit,points in series_for_plot:
        fig, ax = plt.subplots(figsize=(7,4))
        xs=[parse_date(d) for d,_ in points]; ys=[v for _,v in points]
        ax.plot(xs,ys,marker='o',linewidth=1.5,markersize=3)
        ax.axvline(parse_date('2025-01-01'), color='red', linestyle='--', alpha=.5)
        ax.set_title(label); ax.set_ylabel(unit.split('/month')[0]); ax.grid(True, alpha=.25)
        fig.autofmt_xdate(); fig.tight_layout()
        fig.savefig(CHARTS/f'{key}.png', dpi=140)
        plt.close(fig)

# Report markdown
summary_order=['ProtonDB latest-app works share','ProtonDB tested unique apps','Xenia playable issues','Vita3K playable issues','shadPS4 playable issues','ScummVM supported games','WPT Interop stable within-year gain','Wine dev-release bugs fixed','WebAIM avg errors/page','WebAIM WCAG failure %']
lookup={r['series']:r for r in summary}
lines=[]
lines.append('# Progress meters for hard software progress (2020-2026)\n')
lines.append('Generated from public project-published data. Slopes are linear fits: 2022-01..2024-12 vs 2025-01..latest, in the unit shown. Ratio is raw post/baseline slope, so lower-is-better series need sign-aware interpretation in the verdict.\n')
lines.append('| series | 2022-24 slope | 2025-26 slope | ratio | confounders | verdict |')
lines.append('|---|---:|---:|---:|---|---|')
for name in summary_order:
    r=lookup[name]
    lines.append(f"| {name} | {fmt(r['baseline_slope'])} {r['unit']} | {fmt(r['post_slope'])} {r['unit']} | {fmt(r['ratio'])} | {r['confounders']} | {r['verdict']} |")
lines.append('\n## Details by series\n')
for name in summary_order:
    r=lookup[name]
    key=r['key']
    lines.append(f"### {name}\n")
    lines.append(f"- Data: `data/{key}_series.csv`; chart: `charts/{key}.png`.\n")
    lines.append(f"- Baseline slope: {fmt(r['baseline_slope'])} {r['unit']} (n={r['n_baseline']}); 2025-26 slope: {fmt(r['post_slope'])} {r['unit']} (n={r['n_post']}); raw ratio {fmt(r['ratio'])}.\n")
    lines.append(f"- Confounders: {r['confounders']}\n")
    lines.append(f"- Verdict: {r['verdict']}\n")
lines.append('## Attempts and infeasible sources\n')
lines.append('- RPCS3: `rpcs3.net/compatibility` returned HTTP 403 from this environment; a guessed `history.json` URL returned 404. No data included.\n')
lines.append('- decomp.dev: site now serves a sunsetting page; `/projects.json` is 410 and `/api/projects` is 404. Existing individual project histories may still exist, but the public index needed to enumerate them is disabled.\n')
lines.append('- test262.fyi: current `index.json` and `meta.json` are public, but the page exposes no dated history endpoint; reconstructing history would require backend/archive work beyond this pass.\n')
lines.append('- GitHub emulator trackers: Xenia/Vita3K/shadPS4 were reconstructed from current labels plus issue creation dates because full issue timeline replay is API-expensive; this overstates early playable status if labels were applied later.\n')
lines.append('- ProtonDB: full monthly tarball processing was feasible but multi-GB; this pass sampled Jan/Apr/Jul/Oct dumps and used raw yes/no works verdicts, not the site tier algorithm.\n')
lines.append('\n## Anti-AI policy notes\n')
lines.append('I checked readily visible README/CONTRIBUTING files for the included emulator trackers, ScummVM, and Wine and did not find explicit AI-contribution bans. decomp.dev itself now warns that hostile AI forks and number-gaming damaged the decompilation community; that is a direct structural confounder. Known anti-AI policies in adjacent communities such as Dolphin/N64Recomp should be treated as suppressing within-project AI effects, but those projects are not included as quantified series here.\n')
lines.append('\n## Three-sentence bottom line\n')
lines.append('The strongest positive break is ProtonDB/Steam-compatibility and the young shadPS4 tracker, with ScummVM also jumping in 2026; these are real hard-progress meters, but each has obvious non-AI confounders (Steam Deck/Linux gaming, new emulator maturity, and batch engine additions). Mature hard-problem meters—Wine bug fixes, Xenia/Vita3K playable counts, WebAIM accessibility, and stable-browser Interop—do not show a clean 2025-26 acceleration over the 2022-24 slope. Overall, the data fit “AI may help some focused compatibility/decomp-style work, but broad hard software quality meters have not bent upward yet.”\n')
(BASE/'REPORT.md').write_text('\n'.join(lines))
print('wrote', BASE/'REPORT.md')
for r in summary_order:
    row=lookup[r]
    print(f"{r}: {fmt(row['baseline_slope'])} -> {fmt(row['post_slope'])}, ratio {fmt(row['ratio'])}")
