import csv, json, subprocess, time, urllib.parse
from pathlib import Path
from datetime import date, timedelta
BASE=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/raycast')
CACHE=BASE/'cache'/'gh_search'; CACHE.mkdir(parents=True,exist_ok=True)
DATA=BASE/'data'; DATA.mkdir(exist_ok=True)
quarters=[]
for y in range(2021,2027):
    for q,(m1,m2,d2) in enumerate([(1,3,31),(4,6,30),(7,9,30),(10,12,31)],1):
        start=date(y,m1,1); end=date(y,m2,d2)
        if end < date(2021,10,1): continue
        if start > date(2026,10,15): continue
        if end > date(2026,10,15): end=date(2026,10,15)
        quarters.append((f'{y}Q{q}',start.isoformat(),end.isoformat()))

def gh_count(kind, start, end):
    if kind=='created': qualifier=f'created:{start}..{end}'
    elif kind=='merged': qualifier=f'merged:{start}..{end}'
    else: raise ValueError(kind)
    q=f'repo:raycast/extensions type:pr label:"new extension" {qualifier}'
    fn=CACHE/(urllib.parse.quote_plus(q)+'.json')
    if fn.exists():
        data=json.loads(fn.read_text())
    else:
        url='search/issues?q='+urllib.parse.quote(q, safe='')
        res=subprocess.run(['gh','api',url],cwd=str(BASE),text=True,capture_output=True,timeout=60)
        if res.returncode:
            raise RuntimeError(res.stderr or res.stdout)
        fn.write_text(res.stdout)
        data=json.loads(res.stdout)
        time.sleep(2.2)
    return data.get('total_count',0)
rows=[]; cum_opened=0; cum_merged=0
for coh,start,end in quarters:
    opened=gh_count('created',start,end)
    merged=gh_count('merged',start,end)
    cum_opened += opened; cum_merged += merged
    rows.append({'quarter':coh,'start':start,'end':end,'new_extension_prs_opened':opened,'new_extension_prs_merged':merged,'cum_opened_minus_merged':cum_opened-cum_merged})
with open(DATA/'new_extension_prs_by_quarter.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
# current open backlog
q='repo:raycast/extensions type:pr label:"new extension" state:open'
url='search/issues?q='+urllib.parse.quote(q, safe='')
res=subprocess.run(['gh','api',url],cwd=str(BASE),text=True,capture_output=True,timeout=60)
open_current=json.loads(res.stdout).get('total_count',None) if res.returncode==0 else None
with open(DATA/'new_extension_prs_current_open.json','w') as f: json.dump({'query':q,'current_open':open_current},f,indent=2)
for r in rows: print(r)
print('current_open', open_current)
