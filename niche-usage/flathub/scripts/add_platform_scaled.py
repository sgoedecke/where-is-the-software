#!/usr/bin/env python3
import csv, datetime as dt, os
OUT='/Users/seangoedecke/Code/where-is-the-software/niche-usage/flathub'
DATA=os.path.join(OUT,'data')
eco={}
with open(os.path.join(DATA,'ecosystem_daily.csv')) as f:
    r=csv.DictReader(f)
    for row in r:
        if not row['error']:
            eco[dt.date.fromisoformat(row['date'])]=int(row['ecosystem_new_installs'])
# prefix sums
start=min(eco); end=max(eco)
prefix={start-dt.timedelta(days=1):0}
d=start; total=0
while d<=end:
    total += eco.get(d,0)
    prefix[d]=total
    d += dt.timedelta(days=1)
def sum_eco(s,e):
    if e>end: e=end
    if s<start: s=start
    return prefix.get(e,0)-prefix.get(s-dt.timedelta(days=1),0)
rows=list(csv.DictReader(open(os.path.join(DATA,'apps_with_equal_age.csv'))))
for row in rows:
    if row['added_at'] and row['observed180']=='True':
        a=dt.date.fromisoformat(row['added_at'])
        eco180=sum_eco(a,a+dt.timedelta(days=179))
        row['ecosystem_first180_new_installs']=eco180
        row['first180_per_100m_ecosystem']=round(int(row['first180'])/eco180*100_000_000,2) if eco180 else ''
    else:
        row['ecosystem_first180_new_installs']=''; row['first180_per_100m_ecosystem']=''
fields=list(rows[0].keys())
if 'ecosystem_first180_new_installs' not in fields: fields += ['ecosystem_first180_new_installs','first180_per_100m_ecosystem']
with open(os.path.join(DATA,'apps_with_equal_age_scaled.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
# cohort scaled summary from 2021+
coh=sorted(set(r['cohort'] for r in rows if r['cohort']!='unknown'))
with open(os.path.join(DATA,'cohort_summary_scaled.csv'),'w',newline='') as f:
    fields2=['cohort','first180_observed','scaled_ge_100_per_100m','scaled_ge_1k_per_100m','scaled_ge_10k_per_100m','median_first180_per_100m']
    w=csv.DictWriter(f,fieldnames=fields2); w.writeheader()
    for c in coh:
        obs=[r for r in rows if r['cohort']==c and r.get('first180_per_100m_ecosystem')]
        vals=sorted(float(r['first180_per_100m_ecosystem']) for r in obs)
        med=vals[len(vals)//2] if vals else ''
        w.writerow({'cohort':c,'first180_observed':len(obs),'scaled_ge_100_per_100m':sum(v>=100 for v in vals),'scaled_ge_1k_per_100m':sum(v>=1000 for v in vals),'scaled_ge_10k_per_100m':sum(v>=10000 for v in vals),'median_first180_per_100m':med})
