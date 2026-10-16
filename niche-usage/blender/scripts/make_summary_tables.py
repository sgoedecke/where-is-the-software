#!/usr/bin/env python3
import csv, json, statistics, collections
from pathlib import Path
D=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/blender/data')
rows=list(csv.DictReader((D/'extensions_current.csv').open()))
addons=[r for r in rows if r['type']=='add-on' and r['first_listed']]
fields=['cohort_quarter','supply','median_age_days','median_downloads','downloads_ge_100','downloads_ge_1000','downloads_ge_10000','top_downloads']
out=[]
for q in sorted(set(r['cohort_quarter'] for r in addons)):
    rs=[r for r in addons if r['cohort_quarter']==q]
    ds=[int(r['downloads_current']) for r in rs]
    out.append({'cohort_quarter':q,'supply':len(rs),'median_age_days':int(statistics.median(int(r['age_days']) for r in rs)),'median_downloads':int(statistics.median(ds)),'downloads_ge_100':sum(d>=100 for d in ds),'downloads_ge_1000':sum(d>=1000 for d in ds),'downloads_ge_10000':sum(d>=10000 for d in ds),'top_downloads':max(ds)})
with (D/'addon_cohort_quarter_summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fields); w.writeheader(); w.writerows(out)
# GitHub-new quarter summary
r2=list(csv.DictReader((D/'extensions_with_github_repos.csv').open()))
out2=[]; fields2=['cohort_quarter','addon_supply','github_repo_count','repo_created_known','new_project_count','old_project_count','new_share_known']
for q in ['2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2','2026Q3']:
    rs=[r for r in r2 if r['type']=='add-on' and r['cohort_quarter']==q]
    wr=[r for r in rs if r['github_repo']]
    known=[r for r in wr if r['likely_migrated_old_project']!='unknown']
    new=[r for r in known if r['likely_migrated_old_project']=='no']
    old=[r for r in known if r['likely_migrated_old_project']=='yes']
    out2.append({'cohort_quarter':q,'addon_supply':len(rs),'github_repo_count':len(wr),'repo_created_known':len(known),'new_project_count':len(new),'old_project_count':len(old),'new_share_known':round(len(new)/len(known),2) if known else ''})
with (D/'addon_github_new_project_quarter_summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fields2); w.writeheader(); w.writerows(out2)
# theme half summary
themes=[r for r in rows if r['type']=='theme' and r['first_listed']]
out3=[]; fields3=['cohort_half','theme_supply','downloads_ge_100','downloads_ge_1000','downloads_ge_10000','top_downloads']
for h in sorted(set(r['cohort_half'] for r in themes)):
    rs=[r for r in themes if r['cohort_half']==h]; ds=[int(r['downloads_current']) for r in rs]
    out3.append({'cohort_half':h,'theme_supply':len(rs),'downloads_ge_100':sum(d>=100 for d in ds),'downloads_ge_1000':sum(d>=1000 for d in ds),'downloads_ge_10000':sum(d>=10000 for d in ds),'top_downloads':max(ds)})
with (D/'theme_cohort_half_summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fields3); w.writeheader(); w.writerows(out3)
print('wrote summaries')
