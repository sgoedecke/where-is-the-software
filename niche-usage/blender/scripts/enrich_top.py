#!/usr/bin/env python3
import csv, json, subprocess, re, sys
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent))
import collect_blender as cb
OUT=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/blender')
DATA=OUT/'data'; CACHE=OUT/'cache'; PAGES=CACHE/'pages'; GH=CACHE/'github'; GH.mkdir(exist_ok=True)
rows=list(csv.DictReader((DATA/'extensions_current.csv').open(encoding='utf-8')))
addons=[r for r in rows if r['type']=='add-on' and r['first_listed']]
# top recent: AI-era/recent add-ons listed from 2025H2 through 2026Q3, top 50 by current downloads.
recent=[r for r in addons if r['first_listed'] >= '2025-07-01' and r['first_listed'] <= '2026-09-30']
top=sorted(recent, key=lambda r:int(r['downloads_current']), reverse=True)[:60]

def gh_repo_info(repo):
    if not repo: return {}
    safe=repo.replace('/','__')+'.json'
    p=GH/('repo_'+safe)
    if p.exists():
        try: return json.loads(p.read_text())
        except Exception: pass
    cp=subprocess.run(['gh','api',f'repos/{repo}'], text=True, capture_output=True)
    if cp.returncode!=0:
        p.write_text(json.dumps({'error':cp.stderr[:300]})); return {}
    obj=json.loads(cp.stdout); p.write_text(json.dumps(obj), encoding='utf-8'); return obj

out=[]
for r in top:
    slug=r['slug']; t=r['type']; about_path=PAGES/cb.safe_name(t, slug, 'about')
    if not about_path.exists():
        cb.fetch_url(r['website'], about_path, False, 20)
    about=cb.parse_about(about_path.read_text(encoding='utf-8', errors='replace'))
    repo=about.get('github_repo') or r.get('github_repo')
    info=gh_repo_info(repo)
    created=info.get('created_at','')[:10]
    stars=info.get('stargazers_count','') if info else ''
    pushed=info.get('pushed_at','')[:10] if info else ''
    age_before=''
    migrated='unknown'
    if created and r['first_listed']:
        delta=(date.fromisoformat(r['first_listed'])-date.fromisoformat(created)).days
        age_before=delta
        migrated='yes' if delta>=180 else 'no'
    text=' '.join([r['name'],r['tagline'],r['tags'],repo or '']).lower()
    ai=bool(re.search(r'\b(ai|llm|gpt|chatgpt|claude|openai|mcp|comfyui|stable diffusion|diffusion|generative|agent)\b', text))
    rr=dict(r)
    rr.update({'github_repo':repo,'repo_created_at':created,'repo_stars':stars,'repo_pushed_at':pushed,'repo_age_days_before_listing':age_before,'likely_migrated_old_project':migrated,'ai_related_manual':int(ai)})
    out.append(rr)
fields=['name','slug','first_listed','cohort_quarter','downloads_current','versions_count','tags','tagline','github_repo','repo_created_at','repo_age_days_before_listing','likely_migrated_old_project','repo_stars','repo_pushed_at','ai_related_manual','website']
with (DATA/'top_recent_addons_enriched.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fields); w.writeheader(); w.writerows([{k:r.get(k,'') for k in fields} for r in out])
print(f'wrote {len(out)} top recent add-ons')
