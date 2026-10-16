#!/usr/bin/env python3
import csv, datetime as dt, json, math, re, html
from pathlib import Path
from statistics import mean, median

ROOT = Path('/Users/seangoedecke/Code/where-is-the-software/market-usage/googleplay')
CACHE = ROOT/'cache'
DATA = ROOT/'data'
DATA.mkdir(exist_ok=True)


def cohort_half(d: dt.date):
    return f"{d.year}H{1 if d.month <= 6 else 2}"

def month_date(s):
    y,m,_ = map(int, s.split('-'))
    return dt.date(y,m,1)

def parse_current_number():
    s=(CACHE/'appbrain_number_of_apps.html').read_text(errors='ignore')
    d=json.loads(re.search(r'var appsData = (.*?);\n', s, re.S).group(1))
    rows=[]
    for date_s, launched in d['launchedMonthly']['datapoints']:
        m=month_date(date_s)
        if m == dt.date(2026,10,1):
            partial=True
        else:
            partial=False
        unpublished = dict(d['unpublishedMonthly']['datapoints']).get(date_s)
        net = dict(d['appsMonthly']['datapoints']).get(date_s)
        rows.append({'month': m.isoformat(), 'cohort': cohort_half(m), 'launched': launched, 'unpublished': unpublished, 'net_growth': net, 'partial': partial})
    with (DATA/'appbrain_monthly_supply.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    agg={}
    for r in rows:
        if r['partial']: continue
        c=r['cohort']; agg.setdefault(c, {'cohort':c,'months':0,'launched':0,'unpublished':0,'net_growth':0})
        agg[c]['months'] += 1; agg[c]['launched'] += r['launched']; agg[c]['unpublished'] += r['unpublished']; agg[c]['net_growth'] += r['net_growth']
    return agg, rows


def parse_download_snapshot(path: Path, snap_date: dt.date):
    s=path.read_text(errors='ignore')
    # Current 2026 format: { name: '> 500 downloads', data: [...] }
    out=[]
    for m in re.finditer(r"\{\s*name:\s*'([^']+)',\s*data:\s*(\[.*?\])\s*\}", s, re.S):
        name=m.group(1).replace(',', '')
        for age, pct in json.loads(m.group(2)):
            out.append((name, int(age), float(pct)))
    # Older AppBrain format: { key: "> 500 downloads", values: [...] }
    for m in re.finditer(r"\{\s*key:\s*\"([^\"]+)\",\s*values:\s*(\[.*?\])\s*\}", s, re.S):
        name=m.group(1).replace(',', '')
        for age, pct in json.loads(m.group(2)):
            out.append((name, int(age), float(pct)))
    # distribution
    dist=[]
    md=re.search(r'var distData = (\[.*?\]);', s, re.S) or re.search(r'let distData = (\[.*?\]);', s, re.S)
    if md:
        dist=json.loads(md.group(1))
    return out, dist


def parse_download_history():
    snap_paths=list((CACHE/'wayback').glob('appbrain_downloads_*.html'))
    # Add live page as a current snapshot.
    if (CACHE/'appbrain_downloads.html').exists():
        snap_paths.append(CACHE/'appbrain_downloads.html')
    rows=[]; dist_rows=[]
    for p in snap_paths:
        if p.name == 'appbrain_downloads.html':
            snap_date=dt.date(2026,10,14); ts='20261014live'
        else:
            ts=p.stem.split('_')[-1]
            snap_date=dt.datetime.strptime(ts[:8], '%Y%m%d').date()
        series, dist=parse_download_snapshot(p, snap_date)
        if not series: continue
        for threshold, age_weeks, pct in series:
            launch_week = snap_date - dt.timedelta(weeks=age_weeks)
            rows.append({'snapshot':ts,'snapshot_date':snap_date.isoformat(),'age_weeks':age_weeks,'launch_week':launch_week.isoformat(),'cohort':cohort_half(launch_week),'threshold':threshold,'pct':pct})
        for d in dist:
            d=dict(d); d['snapshot']=ts; d['snapshot_date']=snap_date.isoformat(); dist_rows.append(d)
    rows.sort(key=lambda r:(r['snapshot_date'], r['threshold'], r['age_weeks']))
    with (DATA/'appbrain_launch_age_thresholds.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=['snapshot','snapshot_date','age_weeks','launch_week','cohort','threshold','pct']); w.writeheader(); w.writerows(rows)
    if dist_rows:
        keys=sorted(set().union(*(r.keys() for r in dist_rows)))
        with (DATA/'appbrain_download_distribution_snapshots.csv').open('w', newline='') as f:
            w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(dist_rows)
    return rows, dist_rows


def summarize(agg, thresh_rows):
    # Equal-age: age 23 weeks (oldest AppBrain exposes); combine exact age-23 weekly cohorts by half-year.
    by={}
    for r in thresh_rows:
        if r['age_weeks'] != 23: continue
        c=r['cohort']; by.setdefault(c, {}).setdefault(r['threshold'], []).append(r['pct'])
    # Fallback/current recent: for current live snapshot, all ages 0-23 in last ~6 months and actual supply by launch month.
    summary=[]
    thresholds=['> 500 downloads','> 5000 downloads','> 50000 downloads']
    for c in sorted(agg):
        rec=dict(agg[c])
        for t in thresholds:
            vals=by.get(c,{}).get(t,[])
            rec[f'appbrain_23wk_{t}_pct_mean']=mean(vals) if vals else None
            rec[f'appbrain_23wk_{t}_pct_median']=median(vals) if vals else None
            rec[f'appbrain_23wk_{t}_n_weeks']=len(vals)
            rec[f'est_23wk_{t}_count']=round(rec['launched']*mean(vals)) if vals else None
        summary.append(rec)
    with (DATA/'cohort_appbrain_summary.csv').open('w', newline='') as f:
        keys=list(summary[0].keys()); w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(summary)
    return summary

if __name__ == '__main__':
    agg, monthly = parse_current_number()
    thresh, dist = parse_download_history()
    summary = summarize(agg, thresh)
    print('monthly rows', len(monthly), 'threshold rows', len(thresh), 'summary cohorts', len(summary))
    print('latest distribution rows', dist[-7:] if dist else [])
