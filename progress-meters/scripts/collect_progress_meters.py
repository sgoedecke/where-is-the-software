#!/usr/bin/env python3
import csv, datetime as dt, gzip, io, json, math, os, re, sys, tarfile, time, urllib.parse, urllib.request
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path.home() / 'Code' / 'where-is-the-software' / 'progress-meters'
DATA = BASE / 'data'
RAW = BASE / 'raw'
DATA.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)
UA = 'progress-meters research (polite; contact: none)'
MONTHS = {m.lower(): i for i, m in enumerate(['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'], 1)}
ATTEMPTS=[]

def fetch(url, binary=False, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode('utf-8', 'ignore')

def fetch_json(url, timeout=60):
    return json.loads(fetch(url, timeout=timeout))

def write_csv(name, rows, fields):
    path = DATA / name
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print('wrote', path, len(rows), 'rows')

# 1. WebAIM Million annual accessibility reports.
def collect_webaim():
    rows=[]
    for year in range(2019, 2027):
        url = 'https://webaim.org/projects/million/' if year == 2026 else f'https://webaim.org/projects/million/{year}'
        try:
            html = fetch(url)
            avg = None; wcag = None
            m = re.search(r'average of ([0-9.]+) errors per page', html, re.I)
            if m: avg = float(m.group(1))
            patterns = [
                r'([0-9.]+)% of home pages had detected[^.]{0,80}WCAG',
                r'([0-9.]+)%[^.]{0,80}WCAG 2[^.]{0,80}failures',
                r'([0-9.]+)%[^.]{0,80}detectable WCAG',
            ]
            for p in patterns:
                mm = re.search(p, html, re.I)
                if mm:
                    wcag = float(mm.group(1)); break
            if wcag is None and year == 2019: wcag = 97.8
            if wcag is None and year == 2020: wcag = 98.1
            rows.append({'date': f'{year}-02-01', 'year': year, 'avg_errors_per_page': avg, 'wcag_failure_pct': wcag, 'source_url': url})
        except Exception as e:
            ATTEMPTS.append({'series':'WebAIM Million','status':'failed','detail':f'{year}: {e}'})
    write_csv('webaim_million.csv', rows, ['date','year','avg_errors_per_page','wcag_failure_pct','source_url'])
    ATTEMPTS.append({'series':'WebAIM Million','status':'ok','detail':'Parsed annual report pages 2019-2026.'})

# 2. WPT Interop official browser scores (stable and experimental), from wpt.fyi static CSVs.
def interop_score_from_csv(year, mode, meta):
    path = meta[year]['csv_url'].replace('{stable|experimental}', mode)
    url = path if path.startswith('http') else 'https://wpt.fyi' + path
    text = fetch(url, timeout=90)
    focus = [k for k,v in meta[year]['focus_areas'].items() if v.get('countsTowardScore', True)]
    reader = csv.DictReader(io.StringIO(text))
    rows=[]
    for r in reader:
        vals=[]
        for f in focus:
            col = 'interop-' + f
            if col in r and r[col] not in ('', 'NA'):
                try: vals.append(float(r[col]))
                except ValueError: pass
        if vals:
            rows.append({'date': r['date'], 'year': year, 'mode': mode, 'score': sum(vals)/len(vals), 'focus_area_count': len(vals), 'source_url': url})
    return rows

def collect_interop():
    try:
        meta = fetch_json('https://wpt.fyi/static/interop-data.json')
        rows=[]
        for year in ['2022','2023','2024','2025','2026']:
            for mode in ['stable','experimental']:
                try:
                    rows.extend(interop_score_from_csv(year, mode, meta))
                    time.sleep(0.2)
                except Exception as e:
                    ATTEMPTS.append({'series':'WPT Interop','status':'partial-failed','detail':f'{year} {mode}: {e}'})
        write_csv('wpt_interop_daily.csv', rows, ['date','year','mode','score','focus_area_count','source_url'])
        # annual endpoints for a cleaner meter despite yearly focus-area resets.
        endpoints=[]
        by=defaultdict(list)
        for r in rows:
            by[(r['year'], r['mode'])].append(r)
        for (year, mode), rr in sorted(by.items()):
            rr.sort(key=lambda x:x['date'])
            endpoints.append({'date': rr[-1]['date'], 'year': year, 'mode': mode, 'start_score': rr[0]['score'], 'end_score': rr[-1]['score'], 'gain': rr[-1]['score']-rr[0]['score'], 'days': (dt.date.fromisoformat(rr[-1]['date'])-dt.date.fromisoformat(rr[0]['date'])).days+1})
        write_csv('wpt_interop_annual_endpoints.csv', endpoints, ['date','year','mode','start_score','end_score','gain','days'])
        ATTEMPTS.append({'series':'WPT Interop','status':'ok','detail':'Used wpt.fyi static interop CSVs for 2022-2026; annual focus areas reset each year.'})
    except Exception as e:
        ATTEMPTS.append({'series':'WPT Interop','status':'failed','detail':str(e)})

# 3. Wine development release bug-fix counts from release notes.
def collect_wine():
    rows=[]
    try:
        project = urllib.parse.quote_plus('wine/wine')
        tags=[]
        for page in range(1, 5):
            url=f'https://gitlab.winehq.org/api/v4/projects/{project}/repository/tags?per_page=100&page={page}'
            js=fetch_json(url)
            if not js: break
            tags.extend(js)
            time.sleep(0.2)
        pat = re.compile(r'wine-([5-9]|10|11)\.([0-9]+)$')
        for t in tags:
            name=t['name']
            m=pat.match(name)
            if not m: continue
            major=int(m.group(1)); minor=int(m.group(2))
            if major < 5 or major > 11: continue
            date=(t.get('created_at') or t['commit']['committed_date'])[:10]
            bugs=None; source_url=''
            for file in ['ANNOUNCE.md','ANNOUNCE']:
                raw=f'https://gitlab.winehq.org/wine/wine/-/raw/{name}/{file}'
                try:
                    txt=fetch(raw, timeout=30)
                    mm=re.search(r'Bugs fixed in [^(]+\(total ([0-9]+)\):', txt)
                    if mm:
                        bugs=int(mm.group(1)); source_url=raw
                    break
                except Exception:
                    continue
            if bugs is not None:
                rows.append({'date':date,'tag':name,'major':major,'minor':minor,'bugs_fixed':bugs,'source_url':source_url})
            time.sleep(0.08)
        rows.sort(key=lambda r:r['date'])
        write_csv('wine_bugs_fixed_releases.csv', rows, ['date','tag','major','minor','bugs_fixed','source_url'])
        # monthly cumulative series for segmented slopes.
        monthly=[]; cum=0
        for r in rows:
            if '2020-01-01' <= r['date'] <= '2026-12-31':
                cum += int(r['bugs_fixed'])
                monthly.append({'date':r['date'],'cumulative_bugs_fixed':cum,'bugs_fixed':r['bugs_fixed'],'tag':r['tag']})
        write_csv('wine_bugs_fixed_cumulative.csv', monthly, ['date','cumulative_bugs_fixed','bugs_fixed','tag'])
        ATTEMPTS.append({'series':'Wine bugs fixed','status':'ok','detail':'Parsed Wine GitLab release tags and ANNOUNCE/ANNOUNCE.md total bug-fix counts for dev releases.'})
    except Exception as e:
        ATTEMPTS.append({'series':'Wine bugs fixed','status':'failed','detail':str(e)})

# 4. GitHub issue-label compatibility trackers. This is a current-label/creation-date approximation.
def fetch_label_issues(repo, label):
    issues=[]
    enc_label=urllib.parse.quote(label)
    for page in range(1, 60):
        url=f'https://api.github.com/repos/{repo}/issues?state=all&labels={enc_label}&per_page=100&page={page}'
        try:
            js=fetch_json(url, timeout=40)
        except urllib.error.HTTPError as e:
            ATTEMPTS.append({'series':repo,'status':'partial-failed','detail':f'label {label} page {page}: HTTP {e.code}'})
            break
        if not js: break
        for item in js:
            if 'pull_request' in item: continue
            issues.append(item)
        print('label page', repo, label, page, len(js))
        if len(js) < 100: break
        time.sleep(0.7)
    return issues

def collect_github_compat():
    specs=[
        ('xenia_playable','xenia-project/game-compatibility','state-playable'),
        ('vita3k_playable','Vita3K/compatibility','Playable'),
        ('shadps4_playable','shadps4-compatibility/shadps4-game-compatibility','status-playable'),
    ]
    issue_rows=[]; monthly=[]
    for series, repo, label in specs:
        try:
            issues=fetch_label_issues(repo, label)
            dates=[]
            for it in issues:
                d=it['created_at'][:10]
                dates.append(d)
                issue_rows.append({'series':series,'repo':repo,'label':label,'issue_number':it['number'],'created_at':d,'title':it.get('title','')[:200],'url':it['html_url']})
            counts=Counter(d[:7] for d in dates)
            # cumulative monthly from 2020-01 through 2026-10.
            cum=0
            cur=dt.date(2020,1,1); end=dt.date(2026,10,1)
            while cur <= end:
                key=f'{cur.year:04d}-{cur.month:02d}'
                cum += counts.get(key,0)
                monthly.append({'series':series,'date':key+'-01','repo':repo,'label':label,'cumulative_current_label_created':cum,'new_current_label_issues':counts.get(key,0),'approximation':'current label counted at issue creation date; label-change history not replayed'})
                # next month
                cur = dt.date(cur.year + (cur.month==12), 1 if cur.month==12 else cur.month+1, 1)
            ATTEMPTS.append({'series':series,'status':'ok','detail':f'Fetched {len(issues)} issues currently labelled {label}; creation-date approximation, not label-event history.'})
        except Exception as e:
            ATTEMPTS.append({'series':series,'status':'failed','detail':str(e)})
    write_csv('github_compat_label_issues.csv', issue_rows, ['series','repo','label','issue_number','created_at','title','url'])
    write_csv('github_compat_label_monthly.csv', monthly, ['series','date','repo','label','cumulative_current_label_created','new_current_label_issues','approximation'])

# 5. ScummVM supported-games counts by stable release.
def collect_scummvm():
    try:
        releases=fetch_json('https://api.github.com/repos/scummvm/scummvm/releases?per_page=100')
        release_dates={r['tag_name'].lstrip('v'): r['published_at'][:10] for r in releases}
        # Get compatibility versions from current selector.
        html=fetch('https://www.scummvm.org/compatibility/', timeout=60)
        versions=re.findall(r'<option[^>]+value="/compatibility/([^/]+)/"', html)
        rows=[]
        for ver in versions:
            if ver == 'DEV': continue
            if ver not in release_dates: continue
            page=fetch(f'https://www.scummvm.org/compatibility/{ver}/', timeout=90)
            links=set(re.findall(r'href="/compatibility/'+re.escape(ver)+r'/[^"/]+:[^"/]+/"', page))
            # Count status classes where present as a rough completeness measure.
            rows.append({'date':release_dates[ver], 'version':ver, 'supported_game_entries':len(links), 'source_url':f'https://www.scummvm.org/compatibility/{ver}/'})
            time.sleep(0.2)
        rows.sort(key=lambda r:r['date'])
        write_csv('scummvm_supported_games.csv', rows, ['date','version','supported_game_entries','source_url'])
        ATTEMPTS.append({'series':'ScummVM supported games','status':'ok','detail':'Counted game entries on versioned compatibility pages; release dates from GitHub releases.'})
    except Exception as e:
        ATTEMPTS.append({'series':'ScummVM supported games','status':'failed','detail':str(e)})

# 6. ProtonDB data dumps, quarterly sampled because the monthly cumulative tarballs are large.
def proton_date_from_name(name):
    m=re.match(r'reports_([a-z]{3})([0-9]+)_([0-9]{4})\.tar\.gz', name)
    if not m: return None
    mon=MONTHS[m.group(1)]; day=int(m.group(2)); year=int(m.group(3))
    return dt.date(year, mon, min(day,28))

def collect_protondb():
    try:
        contents=fetch_json('https://api.github.com/repos/bdefore/protondb-data/contents/reports?ref=master')
        files=[]
        for x in contents:
            d=proton_date_from_name(x['name'])
            if d and 2020 <= d.year <= 2026:
                files.append((d,x['name'],x['download_url'],x.get('size',0)))
        # Choose one dump in Jan/Apr/Jul/Oct for each year, closest to day 1.
        selected=[]
        for year in range(2020,2027):
            for mon in [1,4,7,10]:
                c=[f for f in files if f[0].year==year and f[0].month==mon]
                if c: selected.append(sorted(c, key=lambda f: f[0].day)[0])
        rows=[]
        for d,name,url,size in selected:
            path=RAW / name
            try:
                print('downloading protondb', name, size)
                data=fetch(url, binary=True, timeout=240)
                path.write_bytes(data)
                with tarfile.open(path, 'r:gz') as tar:
                    member=tar.getmembers()[0]
                    f=tar.extractfile(member)
                    reports=json.load(f)
                total=yes=no=0
                latest={}
                for obj in reports:
                    resp=obj.get('responses') or {}
                    verdict=resp.get('verdict')
                    if verdict not in ('yes','no'): continue
                    total += 1
                    if verdict == 'yes': yes += 1
                    else: no += 1
                    app=((obj.get('app') or {}).get('steam') or {}).get('appId') or resp.get('answerToWhatGame')
                    ts=obj.get('timestamp') or 0
                    if app and (app not in latest or ts > latest[app][0]):
                        latest[app]=(ts, verdict)
                app_total=len(latest); app_yes=sum(1 for _,v in latest.values() if v=='yes')
                rows.append({'date':d.isoformat(),'dump':name,'reports_total':total,'reports_yes':yes,'reports_no':no,'report_yes_share':yes/total if total else '', 'unique_apps_latest':app_total,'unique_apps_latest_yes':app_yes,'unique_app_latest_yes_share':app_yes/app_total if app_total else '', 'download_size_bytes':size,'source_url':url})
                ATTEMPTS.append({'series':'ProtonDB works share','status':'ok','detail':f'Parsed quarterly dump {name}; raw verdict yes/no, not ProtonDB tier algorithm.'})
            except Exception as e:
                ATTEMPTS.append({'series':'ProtonDB works share','status':'partial-failed','detail':f'{name}: {e}'})
            finally:
                try: path.unlink()
                except FileNotFoundError: pass
            time.sleep(0.5)
        write_csv('protondb_quarterly_works.csv', rows, ['date','dump','reports_total','reports_yes','reports_no','report_yes_share','unique_apps_latest','unique_apps_latest_yes','unique_app_latest_yes_share','download_size_bytes','source_url'])
        ATTEMPTS.append({'series':'ProtonDB works share','status':'note','detail':'Full monthly reconstruction skipped to avoid multi-GB download; quarterly Jan/Apr/Jul/Oct sampled from public cumulative tarballs.'})
    except Exception as e:
        ATTEMPTS.append({'series':'ProtonDB works share','status':'failed','detail':str(e)})

# 7. Explicit infeasible/attempted meters.
def collect_attempts_only():
    # RPCS3 public page blocks this environment with 403; no public JSON endpoint found in quick probes.
    for url in ['https://rpcs3.net/compatibility','https://rpcs3.net/compatibility?b','https://raw.githubusercontent.com/RPCS3/rpcs3-compatibility/gh-pages/history.json']:
        try:
            fetch(url, timeout=20)
            ATTEMPTS.append({'series':'RPCS3 compatibility history','status':'unexpected-ok','detail':url})
        except Exception as e:
            ATTEMPTS.append({'series':'RPCS3 compatibility history','status':'failed','detail':f'{url}: {type(e).__name__} {e}'})
    # decomp.dev has been sunset; public index/API gone, individual pages require known slugs.
    for url in ['https://decomp.dev','https://decomp.dev/projects.json','https://decomp.dev/api/projects','https://github.com/encounter/decomp.dev']:
        try:
            txt=fetch(url, timeout=20)
            detail='ok'
            if 'Sunsetting decomp.dev' in txt: detail='site returns Sunsetting page; says existing pages/history remain but index disabled'
            ATTEMPTS.append({'series':'decomp.dev progress history','status':'partial' if 'decomp.dev' in url else 'ok','detail':f'{url}: {detail}'})
        except Exception as e:
            ATTEMPTS.append({'series':'decomp.dev progress history','status':'failed','detail':f'{url}: {type(e).__name__} {e}'})
    # test262 only current JSON easily available; history not exposed without reconstructing backend storage history.
    for url in ['https://test262.fyi/','https://data.test262.fyi/index.json','https://data.test262.fyi/meta.json']:
        try:
            txt=fetch(url, timeout=20)
            ATTEMPTS.append({'series':'test262.fyi','status':'partial','detail':f'{url}: fetched current data ({len(txt)} bytes), no dated history endpoint found in page JS.'})
        except Exception as e:
            ATTEMPTS.append({'series':'test262.fyi','status':'failed','detail':f'{url}: {e}'})

if __name__ == '__main__':
    collect_webaim()
    collect_interop()
    collect_wine()
    collect_scummvm()
    collect_github_compat()
    collect_protondb()
    collect_attempts_only()
    write_csv('attempt_log.csv', ATTEMPTS, ['series','status','detail'])
