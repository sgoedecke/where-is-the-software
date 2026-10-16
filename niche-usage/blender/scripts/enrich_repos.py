#!/usr/bin/env python3
import csv, json, subprocess, sys, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
sys.path.insert(0, str(Path(__file__).parent))
import collect_blender as cb
OUT=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/blender')
DATA=OUT/'data'; CACHE=OUT/'cache'; PAGES=CACHE/'pages'; GH=CACHE/'github'; GH.mkdir(exist_ok=True)
rows=list(csv.DictReader((DATA/'extensions_current.csv').open(encoding='utf-8')))
# Fetch all about pages to extract source repos. Cached pages are reused.
futs=[]
with ThreadPoolExecutor(max_workers=16) as ex:
    for r in rows:
        p=PAGES/cb.safe_name(r['type'], r['slug'], 'about')
        futs.append(ex.submit(cb.fetch_url, r['website'], p, False, 18))
    done=0
    for f in as_completed(futs):
        try: f.result()
        except Exception as e: print('about fetch failed', e, file=sys.stderr)
        done+=1
        if done%300==0: print('about',done,'/',len(futs), file=sys.stderr)

def gh_repo_info(repo):
    if not repo: return {}
    p=GH/('repo_'+repo.replace('/','__')+'.json')
    if p.exists():
        try: return json.loads(p.read_text())
        except Exception: pass
    cp=subprocess.run(['gh','api',f'repos/{repo}'], text=True, capture_output=True)
    if cp.returncode!=0:
        p.write_text(json.dumps({'error':cp.stderr[:300]}), encoding='utf-8'); return {}
    obj=json.loads(cp.stdout); p.write_text(json.dumps(obj), encoding='utf-8'); return obj

enriched=[]; repos=set()
for r in rows:
    p=PAGES/cb.safe_name(r['type'], r['slug'], 'about')
    about=cb.parse_about(p.read_text(encoding='utf-8', errors='replace')) if p.exists() else {'github_repo':''}
    repo=about.get('github_repo','')
    if repo: repos.add(repo)
    rr=dict(r); rr['github_repo']=repo; enriched.append(rr)
print('unique github repos',len(repos), file=sys.stderr)
repo_infos={}
for i,repo in enumerate(sorted(repos),1):
    repo_infos[repo]=gh_repo_info(repo)
    if i%100==0: print('gh',i,'/',len(repos), file=sys.stderr)

fields=list(enriched[0].keys())+['repo_created_at','repo_stars','repo_age_days_before_listing','likely_migrated_old_project']
with (DATA/'extensions_with_github_repos.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fields); w.writeheader()
    for r in enriched:
        repo=r.get('github_repo',''); info=repo_infos.get(repo,{}) if repo else {}
        created=info.get('created_at','')[:10]
        age=''; migrated='unknown'
        if created and r.get('first_listed'):
            delta=(date.fromisoformat(r['first_listed'])-date.fromisoformat(created)).days
            age=delta; migrated='yes' if delta>=180 else 'no'
        out=dict(r); out.update({'repo_created_at':created,'repo_stars':info.get('stargazers_count',''),'repo_age_days_before_listing':age,'likely_migrated_old_project':migrated})
        w.writerow(out)
print('wrote extensions_with_github_repos.csv')
