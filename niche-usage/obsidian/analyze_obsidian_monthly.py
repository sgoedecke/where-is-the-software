#!/usr/bin/env python3
import calendar, csv, datetime as dt, json, math, os, re, subprocess, sys, urllib.parse, urllib.request, time
from collections import Counter, defaultdict

REPO = os.path.join(os.getcwd(), 'obsidian-releases')
OUT = os.getcwd()

def git(*args):
    return subprocess.check_output(['git','-C',REPO,*args], text=True, stderr=subprocess.DEVNULL)

def git_maybe(*args):
    try:
        return git(*args)
    except subprocess.CalledProcessError:
        return ''

def add_months(d, months):
    y = d.year + (d.month - 1 + months)//12
    m = (d.month - 1 + months)%12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y,m)[1]))

def month_ends(start, end):
    y, m = start.year, start.month
    while (y,m) <= (end.year,end.month):
        last = calendar.monthrange(y,m)[1]
        yield dt.date(y,m, min(last, end.day if (y,m)==(end.year,end.month) else last))
        if m == 12: y += 1; m = 1
        else: m += 1

def first_commit_date(path):
    s = git('log','--reverse','--format=%cs','--',path).splitlines()
    return dt.date.fromisoformat(s[0]) if s else None

def rev_before(path, d):
    return git_maybe('rev-list','-n','1',f'--before={d.isoformat()} 23:59:59','HEAD','--',path).strip()

def load_json_at(commit, path):
    return json.loads(git('show', f'{commit}:{path}'))

def median(vals):
    vals=sorted(vals); n=len(vals)
    if not n: return None
    return vals[n//2] if n%2 else (vals[n//2-1]+vals[n//2])/2

def percentile(vals, p):
    vals=sorted(vals); n=len(vals)
    if not n: return None
    k=(n-1)*p/100; lo=math.floor(k); hi=math.ceil(k)
    return vals[lo] if lo==hi else vals[lo]*(hi-k)+vals[hi]*(k-lo)

def build_snapshots(path, extractor, start, end, label):
    snaps=[]; prev_commit=None
    for d in month_ends(start,end):
        c=rev_before(path,d)
        if not c or c == prev_commit:
            continue
        data=load_json_at(c,path)
        vals=extractor(data)
        snaps.append({'date':d, 'commit':c, 'values':vals, 'count':len(vals)})
        prev_commit=c
        print(f'{label} {d}: {len(vals)}', file=sys.stderr)
    return snaps

def main():
    head_date = dt.date.fromisoformat(git('log','-1','--format=%cs').strip())
    head_commit = git('rev-parse','HEAD').strip()
    current_plugins_list=json.load(open(os.path.join(REPO,'community-plugins.json')))
    current_plugins={p['id']:p for p in current_plugins_list}
    current_themes_list=json.load(open(os.path.join(REPO,'community-css-themes.json')))
    current_themes={t['name']:t for t in current_themes_list}

    p_start=first_commit_date('community-plugins.json')
    s_start=first_commit_date('community-plugin-stats.json')
    t_start=first_commit_date('community-css-themes.json')
    start=min(d for d in [p_start,s_start,t_start] if d)

    print('Loading monthly plugin-list snapshots...', file=sys.stderr)
    plugin_snaps=build_snapshots('community-plugins.json', lambda data: {p['id']:p for p in data}, p_start, head_date, 'plugins')
    print('Loading monthly theme-list snapshots...', file=sys.stderr)
    theme_snaps=build_snapshots('community-css-themes.json', lambda data: {t['name']:t for t in data}, t_start, head_date, 'themes')
    print('Loading monthly plugin-stats snapshots...', file=sys.stderr)
    stats_snaps=build_snapshots('community-plugin-stats.json', lambda data: {k:(v.get('downloads') or 0) for k,v in data.items()}, s_start, head_date, 'stats')
    for s in stats_snaps:
        s['total']=sum(s['values'].values())
    latest_stats=stats_snaps[-1]; current_total=latest_stats['total']

    # First-seen month from monthly snapshots.
    first_seen={}
    prev=set()
    for snap in plugin_snaps:
        ids=set(snap['values'])
        for pid in sorted(ids - prev):
            first_seen[pid]={'first_seen_monthly':snap['date'], 'first_seen_commit':snap['commit']}
        prev=ids
    theme_first={}
    prev=set()
    for snap in theme_snaps:
        names=set(snap['values'])
        for name in sorted(names - prev):
            theme_first[name]={'first_seen_monthly':snap['date'], 'first_seen_commit':snap['commit']}
        prev=names

    rows=[]
    for pid, fs in first_seen.items():
        add=fs['first_seen_monthly']
        target=add_months(add,6)
        snap=next((s for s in stats_snaps if s['date'] >= target), None)
        dl6 = snap['values'].get(pid,0) if snap else None
        total_at=snap['total'] if snap else None
        rows.append({
            'id':pid, 'name':current_plugins.get(pid,{}).get('name',''), 'repo':current_plugins.get(pid,{}).get('repo',''),
            'first_seen_monthly':add.isoformat(), 'target_6mo':target.isoformat(), 'stats_snapshot_date':snap['date'].isoformat() if snap else '',
            'age_days_at_snapshot':(snap['date']-add).days if snap else '', 'downloads_6mo':dl6 if dl6 is not None else '',
            'ecosystem_downloads_at_snapshot':total_at if total_at is not None else '', 'current_downloads':latest_stats['values'].get(pid,''),
            'is_current':pid in current_plugins,
        })

    thresholds=[1000,10000,100000]
    eligible=[r for r in rows if r['is_current'] and r['downloads_6mo']!='']
    summary={}
    cohorts={
        'all_measurable_current_plugins': lambda r: True,
        'pre_2026_05_added': lambda r: r['first_seen_monthly'] < '2026-05-01',
        'pre_2024_added': lambda r: r['first_seen_monthly'] < '2024-01-01',
        '2024_added': lambda r: r['first_seen_monthly'].startswith('2024-'),
        '2025_added': lambda r: r['first_seen_monthly'].startswith('2025-'),
        '2026_jan_apr_added': lambda r: '2026-01-01' <= r['first_seen_monthly'] < '2026-05-01',
    }
    for name,f in cohorts.items():
        cohort=[r for r in eligible if f(r)]
        if not cohort: continue
        vals=[int(r['downloads_6mo']) for r in cohort]
        raw_counts={str(t):sum(v>=t for v in vals) for t in thresholds}
        scaled_counts={}
        for t in thresholds:
            scaled_counts[str(t)] = sum(int(r['downloads_6mo']) >= t*(int(r['ecosystem_downloads_at_snapshot'])/current_total) for r in cohort)
        summary[name]={
            'n':len(cohort), 'median_6mo_downloads':median(vals), 'p75_6mo_downloads':percentile(vals,75), 'p90_6mo_downloads':percentile(vals,90), 'p99_6mo_downloads':percentile(vals,99),
            'raw_threshold_counts':raw_counts, 'raw_threshold_rates':{str(t):raw_counts[str(t)]/len(cohort) for t in thresholds},
            'scaled_to_2026_10_15_total_counts':scaled_counts, 'scaled_to_2026_10_15_total_rates':{str(t):scaled_counts[str(t)]/len(cohort) for t in thresholds},
        }

    plugin_add_month=Counter(r['first_seen_monthly'][:7] for r in rows if r['is_current'])
    theme_add_month=Counter(v['first_seen_monthly'].isoformat()[:7] for k,v in theme_first.items() if k in current_themes)
    monthly=[]
    all_months=sorted(set(plugin_add_month)|set(theme_add_month)|{s['date'].isoformat()[:7] for s in stats_snaps})
    for ym in all_months:
        cohort=[r for r in rows if r['is_current'] and r['first_seen_monthly'].startswith(ym)]
        measured=[r for r in cohort if r['downloads_6mo']!='']
        rec={'month':ym, 'plugin_additions_current_survivors':len(cohort), 'theme_additions_current_survivors':theme_add_month.get(ym,0)}
        stat=next((s for s in stats_snaps if s['date'].isoformat()[:7]==ym),None)
        if stat: rec.update({'ecosystem_downloads_month_end':stat['total'], 'stats_plugins_month_end':stat['count']})
        if measured:
            vals=[int(r['downloads_6mo']) for r in measured]
            rec.update({'measured_6mo_plugins':len(measured), 'median_6mo_downloads':median(vals), 'ge_1k_raw':sum(v>=1000 for v in vals), 'ge_10k_raw':sum(v>=10000 for v in vals), 'ge_100k_raw':sum(v>=100000 for v in vals)})
        monthly.append(rec)

    # Accepted PR-ish counts from local git subjects touching list files.
    log=git('log','--date=short','--format=%cs%x09%s','--','community-plugins.json','community-css-themes.json')
    pr_month=Counter(); mirror_added=Counter(); commits_month=Counter()
    mirror_re=re.compile(r'\+([0-9]+) plugins.*\+([0-9]+) themes')
    for line in log.splitlines():
        date,subj=line.split('\t',1); ym=date[:7]; commits_month[ym]+=1
        if re.search(r'\(#\d+\)',subj): pr_month[ym]+=1
        m=mirror_re.search(subj)
        if m: mirror_added[ym]+=int(m.group(1))+int(m.group(2))
    for rec in monthly:
        rec['git_commits_touching_lists']=commits_month.get(rec['month'],0)
        rec['git_pr_numbered_commits_touching_lists']=pr_month.get(rec['month'],0)
        rec['git_mirror_message_added_plugins_plus_themes']=mirror_added.get(rec['month'],0)

    # GitHub search API all PRs created by month, 2025-2026. This is submission pressure, not acceptance.
    pr_created={}
    for y in [2025,2026]:
        max_m=12 if y<head_date.year else head_date.month
        for m in range(1,max_m+1):
            start=dt.date(y,m,1); end=dt.date(y,m,calendar.monthrange(y,m)[1])
            q=f'repo:obsidianmd/obsidian-releases is:pr created:{start.isoformat()}..{end.isoformat()}'
            url='https://api.github.com/search/issues?'+urllib.parse.urlencode({'q':q,'per_page':1})
            req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'copilot-analysis'})
            try:
                with urllib.request.urlopen(req,timeout=20) as resp:
                    data=json.load(resp); pr_created[f'{y:04d}-{m:02d}']=data.get('total_count')
            except Exception as e:
                pr_created[f'{y:04d}-{m:02d}']=None
                print(f'PR created API failed {y}-{m:02d}: {e}', file=sys.stderr)
            time.sleep(0.25)
    for rec in monthly:
        if rec['month'] in pr_created: rec['github_prs_created_all_repo']=pr_created[rec['month']]

    top6=sorted(eligible,key=lambda r:int(r['downloads_6mo']),reverse=True)[:30]
    os.makedirs(os.path.join(OUT,'results'),exist_ok=True)
    with open(os.path.join(OUT,'results','plugin_6mo_downloads.csv'),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    fields=sorted(set().union(*(r.keys() for r in monthly)))
    with open(os.path.join(OUT,'results','monthly_summary.csv'),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(monthly)
    result={'method_note':'first-added date and stats are reconstructed at month-end granularity from git history; six-month downloads use the first month-end stats snapshot on/after first_seen+6 months.',
            'head_date':head_date.isoformat(),'head_commit':head_commit,'current_plugins':len(current_plugins),'current_themes':len(current_themes),
            'current_total_plugin_downloads':current_total,'stats_snapshot_count':len(stats_snaps),'summary':summary,'monthly':monthly,
            'top_6mo_plugins':top6,'github_pr_created_counts_2025_2026':pr_created}
    with open(os.path.join(OUT,'results','summary.json'),'w') as f: json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ['head_date','current_plugins','current_themes','current_total_plugin_downloads','summary','github_pr_created_counts_2025_2026']}, indent=2))

if __name__=='__main__': main()
