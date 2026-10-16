#!/usr/bin/env python3
import csv, json, os, re, subprocess, urllib.parse, urllib.request
OUT='/Users/seangoedecke/Code/where-is-the-software/niche-usage/flathub'
DATA=os.path.join(OUT,'data'); CACHE=os.path.join(OUT,'cache')
os.makedirs(CACHE,exist_ok=True)

def fetch_appstream(app):
    p=os.path.join(CACHE,'appstream_'+app.replace('/','_')+'.json')
    if os.path.exists(p): return json.load(open(p))
    with urllib.request.urlopen('https://flathub.org/api/v2/appstream/'+urllib.parse.quote(app,safe=''), timeout=30) as r:
        d=json.load(r)
    json.dump(d,open(p,'w'))
    return d

def gh_repo_meta(full):
    safe=full.replace('/','_')
    p=os.path.join(CACHE,'ghrepo_'+safe+'.json')
    if os.path.exists(p): return json.load(open(p))
    try:
        out=subprocess.check_output(['gh','api','repos/'+full], text=True, timeout=30)
        d=json.loads(out)
    except Exception as e:
        d={'error':str(e)}
    json.dump(d,open(p,'w'))
    return d

def github_repo_from_url(url):
    if not url: return ''
    m=re.search(r'github\.com[:/]+([^/\s]+)/([^/#?\s]+)', url)
    if not m: return ''
    owner=m.group(1); repo=m.group(2).replace('.git','')
    if repo in ('issues','pull','tree','releases'): return ''
    return owner+'/'+repo

rows=list(csv.DictReader(open(os.path.join(DATA,'top_recent_by_last_month.csv'))))
out=[]
for row in rows:
    app=row['app_id']
    try: ast=fetch_appstream(app)
    except Exception as e: ast={'urls':{},'error':str(e)}
    urls=ast.get('urls') or {}
    gh=''
    for key in ['vcs_browser','homepage','bugtracker','contribute']:
        gh=github_repo_from_url(urls.get(key));
        if gh: break
    up=gh_repo_meta(gh) if gh else {}
    flat=gh_repo_meta('flathub/'+app)
    row.update({
        'homepage':urls.get('homepage',''),
        'vcs_browser':urls.get('vcs_browser',''),
        'bugtracker':urls.get('bugtracker',''),
        'github_repo':gh,
        'github_created_at':up.get('created_at',''),
        'github_pushed_at':up.get('pushed_at',''),
        'github_stars':up.get('stargazers_count',''),
        'flathub_repo_created_at':flat.get('created_at',''),
        'flathub_repo_pushed_at':flat.get('pushed_at',''),
        'is_ai_keyword': bool(re.search(r'\b(ai|llm|gpt|chatbot|model|ollama|openai|claude|mcp)\b', ' '.join([row.get('app_id',''),row.get('name',''),row.get('summary',''),ast.get('description','')]), re.I)),
    })
    out.append(row)
fields=list(out[0].keys())
with open(os.path.join(DATA,'top_recent_enriched.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
