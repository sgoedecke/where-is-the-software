#!/usr/bin/env python3
import csv, math, pathlib, statistics
from collections import defaultdict
ROOT=pathlib.Path.home()/"Code/where-is-the-software/stalled-projects"; DATA=ROOT/'data'

def readcsv(name):
    with (DATA/name).open() as f: return list(csv.DictReader(f))

def writecsv(name, rows):
    if not rows: return
    with (DATA/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def q_index(q):
    y=int(q[:4]); qq=int(q[-1]); return (y-2022)*4+(qq-1)

def linfit(xs, ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    den=sum((x-mx)**2 for x in xs)
    b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den if den else 0
    a=my-b*mx
    return a,b

# GitHub aggregate by quarter and repo-level pre/post.
gh=readcsv('github_old_issue_closures_quarterly.csv')
agg=[]
byq=defaultdict(lambda: {'old':0,'all':0})
byrepo=defaultdict(lambda: {'pre_old':0,'pre_all':0,'post_old':0,'post_all':0})
for r in gh:
    old=int(r['adjusted_completed_old_ge3y']); allc=int(r['adjusted_completed_all'])
    byq[r['quarter']]['old']+=old; byq[r['quarter']]['all']+=allc
    bucket='pre' if r['start']<'2025-01-01' else 'post'
    byrepo[r['repo']][bucket+'_old']+=old; byrepo[r['repo']][bucket+'_all']+=allc
for q in sorted(byq, key=q_index):
    old=byq[q]['old']; allc=byq[q]['all']
    agg.append({'quarter':q,'old_completed_ge3y':old,'completed_all':allc,'old_share':old/allc if allc else ''})
writecsv('summary_github_quarterly_aggregate.csv', agg)
repo_rows=[]
for repo,d in sorted(byrepo.items()):
    pre_s=d['pre_old']/d['pre_all'] if d['pre_all'] else 0; post_s=d['post_old']/d['post_all'] if d['post_all'] else 0
    repo_rows.append({'repo':repo, **d, 'pre_old_share':pre_s, 'post_old_share':post_s, 'post_minus_pre_pp':(post_s-pre_s)*100, 'post_vs_pre_ratio':(post_s/pre_s if pre_s else '')})
writecsv('summary_github_repo_pre_post.csv', repo_rows)
# trend break fit on 2022-24 aggregate old count and share
pre=[r for r in agg if r['quarter']<'2025Q1']; post=[r for r in agg if r['quarter']>='2025Q1']
for metric in ['old_completed_ge3y','old_share']:
    xs=[q_index(r['quarter']) for r in pre]; ys=[float(r[metric]) for r in pre]
    a,b=linfit(xs,ys)
    pred=sum(a+b*q_index(r['quarter']) for r in post); actual=sum(float(r[metric]) for r in post)
    print('github trend', metric, 'baseline_slope_per_q', b, 'post_actual_sum', actual, 'post_pred_sum', pred, 'actual_minus_pred_pct', (actual-pred)/pred*100 if pred else None)
pre_old=sum(int(r['old_completed_ge3y']) for r in pre); pre_all=sum(int(r['completed_all']) for r in pre)
post_old=sum(int(r['old_completed_ge3y']) for r in post); post_all=sum(int(r['completed_all']) for r in post)
print('github pre/post totals', pre_old, pre_all, pre_old/pre_all, post_old, post_all, post_old/post_all)
# Top issue hazard aggregate
top=readcsv('github_top_reacted_hazard.csv')
years=defaultdict(lambda:{'risk':0,'closed':0})
for r in top:
    years[r['year']]['risk'] += int(r['top50_at_risk_start'])
    years[r['year']]['closed'] += int(r['closed_completed_during_year'])
hrows=[]
for y in sorted(years):
    d=years[y]; h=d['closed']/d['risk'] if d['risk'] else ''
    hrows.append({'year':y,'top50_at_risk_start':d['risk'],'closed_completed':d['closed'],'hazard':h})
writecsv('summary_top_reacted_hazard_aggregate.csv', hrows)
print('top hazard', hrows)
# Bugzilla aggregate trend
bz=readcsv('mozilla_bugzilla_fixed_quarterly.csv')
prebz=[r for r in bz if r['start']<'2025-01-01']; postbz=[r for r in bz if r['start']>='2025-01-01']
for label,rs in [('bugzilla pre',prebz),('bugzilla post',postbz)]:
    old=sum(int(r['fixed_old_ge5y']) for r in rs); allc=sum(int(r['fixed_all']) for r in rs)
    print(label, old, allc, old/allc)
# Qualitative
qual=readcsv('qualitative_stalled_projects.csv')
preq=sum(int(r['major_milestone_2023_04_to_2024_12']) for r in qual); postq=sum(int(r['major_milestone_2025_01_to_2026_10']) for r in qual)
print('qual milestones', len(qual), preq, postq, preq/len(qual), postq/len(qual))
