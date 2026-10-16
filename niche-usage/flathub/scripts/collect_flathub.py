#!/usr/bin/env python3
import csv, datetime as dt, gzip, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT='/Users/seangoedecke/Code/where-is-the-software/niche-usage/flathub'
CACHE=os.path.join(OUT,'cache')
DATA=os.path.join(OUT,'data')
os.makedirs(CACHE,exist_ok=True); os.makedirs(DATA,exist_ok=True)
TODAY=dt.date(2026,10,15)
UA='flathub-cohort-analysis/1.0'

def fetch_json(url, data=None, retries=4, accept_gzip=False):
    body=None
    headers={'User-Agent':UA}
    if data is not None:
        body=json.dumps(data).encode()
        headers['Content-Type']='application/json'
    if accept_gzip:
        headers['Accept-Encoding']='gzip'
    for i in range(retries):
        try:
            req=urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                raw=r.read()
                if r.headers.get('Content-Encoding')=='gzip' or raw[:2]==b'\x1f\x8b':
                    raw=gzip.decompress(raw)
                return json.loads(raw)
        except Exception as e:
            if i==retries-1:
                raise
            time.sleep(1.5*(i+1))

def iso_date(ts):
    if ts is None: return ''
    try: return dt.datetime.utcfromtimestamp(int(ts)).date().isoformat()
    except Exception: return ''

def cohort_half(date_s):
    if not date_s: return 'unknown'
    y,m=map(int,date_s.split('-')[:2])
    return f'{y}-H{1 if m<=6 else 2}'

def exclude_app(app_id, typ=''):
    if not app_id: return True
    bad_suffix=('.Debug','.Locale','.Sources','.BaseApp')
    if app_id.endswith(bad_suffix): return True
    if '.Debug.' in app_id or '.Locale.' in app_id or '.Sources.' in app_id: return True
    if app_id.endswith('.BaseApp') or app_id.endswith('.Sdk') or app_id.endswith('.Platform'):
        return True
    if app_id.startswith(('org.freedesktop.Platform','org.gnome.Platform','org.kde.Platform','org.freedesktop.Sdk','org.gnome.Sdk','org.kde.Sdk')):
        return True
    if typ and typ.lower() in {'runtime','addon','localization','generic'}:
        return True
    return False

def collect_search():
    path=os.path.join(CACHE,'search_all.json')
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    hits=[]; page=1; total_pages=None
    while True:
        d=fetch_json('https://flathub.org/api/v2/search', {'query':'','page':page})
        if total_pages is None: total_pages=d.get('totalPages')
        hits.extend(d['hits'])
        print(f'page {page}/{total_pages}: {len(hits)}', file=sys.stderr, flush=True)
        if page>=d.get('totalPages',page): break
        page+=1
    with open(path,'w') as f: json.dump(hits,f)
    return hits

def collect_stats(apps, max_workers=20):
    path=os.path.join(CACHE,'current_stats.json')
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    stats={}
    def one(app_id):
        try:
            return app_id, fetch_json('https://flathub.org/api/v2/stats/'+urllib.parse.quote(app_id,safe=''))
        except Exception as e:
            return app_id, {'error':str(e)}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs=[ex.submit(one,a['app_id']) for a in apps]
        for i,fut in enumerate(as_completed(futs),1):
            app_id,d=fut.result(); stats[app_id]=d
            if i%100==0: print(f'stats {i}/{len(futs)}', file=sys.stderr, flush=True)
    with open(path,'w') as f: json.dump(stats,f)
    return stats

def save_apps(hits, stats):
    rows=[]
    for h in hits:
        app_id=h.get('app_id') or h.get('id','').replace('_','.')
        typ=h.get('type','')
        if exclude_app(app_id, typ):
            continue
        added=iso_date(h.get('added_at'))
        s=stats.get(app_id,{})
        rows.append({
            'app_id':app_id,
            'name':h.get('name',''),
            'type':typ,
            'added_at':added,
            'cohort':cohort_half(added),
            'installs_total':s.get('installs_total',''),
            'installs_last_month':h.get('installs_last_month',''),
            'verification_verified':h.get('verification_verified',''),
            'developer_name':h.get('developer_name',''),
            'summary':h.get('summary',''),
            'runtime':h.get('runtime',''),
            'categories':'|'.join(h.get('sub_categories') or []),
        })
    with open(os.path.join(DATA,'apps.csv'),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows

def daily_new_from_refs(refs, app_id):
    arches=refs.get(app_id)
    if not arches: return 0
    total=0
    for vals in arches.values():
        if isinstance(vals, list) and len(vals)>=2:
            total += max(0, int(vals[0])-int(vals[1]))
    return total

def collect_equal_age(apps):
    # Builds first-90/180-day new install counts by extracting app new installs from daily stat files.
    # Cache stores daily sparse rows, not raw JSON, to keep disk use reasonable.
    daily_path=os.path.join(DATA,'daily_new_installs.csv')
    need_apps={a['app_id']: dt.date.fromisoformat(a['added_at']) for a in apps if a['added_at'] and a['added_at']>='2021-01-01'}
    app_ids=set(need_apps)
    if not os.path.exists(daily_path):
        start=dt.date(2021,1,1); end=TODAY-dt.timedelta(days=1)
        dates=[]; d=start
        while d<=end:
            dates.append(d); d+=dt.timedelta(days=1)
        def one(day):
            url=f'https://flathub.org/stats/{day.year:04d}/{day.month:02d}/{day.day:02d}.json'
            try:
                j=fetch_json(url, accept_gzip=True, retries=3)
                refs=j.get('refs',{})
                rows=[]
                for app_id in app_ids.intersection(refs.keys()):
                    n=daily_new_from_refs(refs, app_id)
                    if n:
                        rows.append((day.isoformat(), app_id, n))
                ecosystem_new=max(0,int(j.get('downloads',0))-int(j.get('updates',0)))
                return day, ecosystem_new, rows, None
            except Exception as e:
                return day, 0, [], str(e)
        with open(daily_path,'w',newline='') as frows, open(os.path.join(DATA,'ecosystem_daily.csv'),'w',newline='') as feco:
            w=csv.writer(frows); w.writerow(['date','app_id','new_installs'])
            we=csv.writer(feco); we.writerow(['date','ecosystem_new_installs','error'])
            with ThreadPoolExecutor(max_workers=14) as ex:
                futs=[ex.submit(one,d) for d in dates]
                done=0
                for fut in as_completed(futs):
                    day, eco, rows, err=fut.result()
                    we.writerow([day.isoformat(), eco, err or ''])
                    for r in rows: w.writerow(r)
                    done+=1
                    if done%50==0: print(f'daily {done}/{len(dates)}', file=sys.stderr, flush=True)
    # aggregate sparse rows
    per={a['app_id']:{'first90':0,'first180':0,'observed90':False,'observed180':False} for a in apps}
    cutoff=TODAY-dt.timedelta(days=1)
    for app_id, added in need_apps.items():
        per.setdefault(app_id,{'first90':0,'first180':0,'observed90':False,'observed180':False})
        per[app_id]['observed90']= added+dt.timedelta(days=89) <= cutoff
        per[app_id]['observed180']= added+dt.timedelta(days=179) <= cutoff
    with open(daily_path) as f:
        r=csv.DictReader(f)
        for row in r:
            app_id=row['app_id']; d=dt.date.fromisoformat(row['date']); added=need_apps.get(app_id)
            if not added: continue
            age=(d-added).days
            n=int(row['new_installs'])
            if 0 <= age < 90: per[app_id]['first90'] += n
            if 0 <= age < 180: per[app_id]['first180'] += n
    out=[]
    for a in apps:
        p=per.get(a['app_id'],{})
        rr=dict(a)
        rr.update({k:p.get(k,'') for k in ['first90','first180','observed90','observed180']})
        out.append(rr)
    with open(os.path.join(DATA,'apps_with_equal_age.csv'),'w',newline='') as f:
        fields=list(out[0].keys())
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    return out

def summarize(apps):
    thresholds=[('low',100),('modest',1000),('high',10000)]
    cohorts=sorted(set(a['cohort'] for a in apps if a['cohort']!='unknown'))
    with open(os.path.join(DATA,'cohort_summary.csv'),'w',newline='') as f:
        fields=['cohort','supply','verified','current_ge_1k_total','current_ge_10k_total','current_ge_100k_total','last_month_ge_100','last_month_ge_1k','last_month_ge_10k','first90_observed','first90_ge_100','first90_ge_1k','first90_ge_10k','first180_observed','first180_ge_100','first180_ge_1k','first180_ge_10k','median_first180_observed']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for c in cohorts:
            rows=[a for a in apps if a['cohort']==c]
            obs90=[a for a in rows if str(a.get('observed90'))=='True']
            obs180=[a for a in rows if str(a.get('observed180'))=='True']
            f180=sorted(int(a.get('first180') or 0) for a in obs180)
            med=f180[len(f180)//2] if f180 else ''
            def ge(field,t, source=rows):
                return sum(1 for a in source if int(float(a.get(field) or 0))>=t)
            w.writerow({
                'cohort':c,'supply':len(rows),'verified':sum(1 for a in rows if str(a.get('verification_verified')).lower()=='true'),
                'current_ge_1k_total':ge('installs_total',1000),'current_ge_10k_total':ge('installs_total',10000),'current_ge_100k_total':ge('installs_total',100000),
                'last_month_ge_100':ge('installs_last_month',100),'last_month_ge_1k':ge('installs_last_month',1000),'last_month_ge_10k':ge('installs_last_month',10000),
                'first90_observed':len(obs90),'first90_ge_100':ge('first90',100,obs90),'first90_ge_1k':ge('first90',1000,obs90),'first90_ge_10k':ge('first90',10000,obs90),
                'first180_observed':len(obs180),'first180_ge_100':ge('first180',100,obs180),'first180_ge_1k':ge('first180',1000,obs180),'first180_ge_10k':ge('first180',10000,obs180),'median_first180_observed':med,
            })
    recent=[a for a in apps if a['added_at']>='2025-01-01']
    recent=sorted(recent,key=lambda a:int(float(a.get('installs_last_month') or 0)), reverse=True)[:50]
    with open(os.path.join(DATA,'top_recent_by_last_month.csv'),'w',newline='') as f:
        fields=['app_id','name','added_at','cohort','installs_last_month','installs_total','first180','observed180','verification_verified','developer_name','summary','categories']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows([{k:a.get(k,'') for k in fields} for a in recent])

def main():
    hits=collect_search()
    # preliminary filter before stats
    prelim=[]
    for h in hits:
        app_id=h.get('app_id') or h.get('id','').replace('_','.')
        if not exclude_app(app_id,h.get('type','')):
            h['app_id']=app_id; prelim.append(h)
    print(f'hits={len(hits)} prelim_apps={len(prelim)}', file=sys.stderr)
    stats=collect_stats(prelim)
    apps=save_apps(hits,stats)
    print(f'apps={len(apps)}', file=sys.stderr)
    apps2=collect_equal_age(apps)
    summarize(apps2)

if __name__=='__main__': main()
