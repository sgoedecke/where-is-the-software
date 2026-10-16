#!/usr/bin/env python3
import csv, json, urllib.request, urllib.parse, re, sys
from pathlib import Path
from datetime import date, timedelta
sys.path.insert(0, str(Path(__file__).parent))
import collect_blender as cb
OUT=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/blender')
DATA=OUT/'data'; CACHE=OUT/'cache'/'wayback'; CACHE.mkdir(exist_ok=True)
rows=list(csv.DictReader((DATA/'extensions_current.csv').open()))
want_names=['Ucupaint','MMD Tools','VRM format','3MF Import/Export','Easy Tree','Modern Primitive','STEP Importer','Blender MCP','ComfyUI-BlenderAI-node']
# add top recent items and a few AI-keyword items if present
samples=[]
for r in rows:
    if r['type']=='add-on' and (r['name'] in want_names or re.search(r'\b(MCP|Comfy|LLM|GPT|AI)\b', r['name']+' '+r['tagline'], re.I)):
        samples.append(r)
# unique, limit
seen=set(); samples=[r for r in samples if not (r['slug'] in seen or seen.add(r['slug']))][:30]

def fetch(url, path):
    if path.exists(): return path.read_text(encoding='utf-8', errors='replace')
    req=urllib.request.Request(url, headers={'User-Agent':cb.UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw=resp.read()
    text=raw.decode('utf-8','replace')
    path.write_text(text, encoding='utf-8')
    return text
out=[]
for r in samples:
    first=date.fromisoformat(r['first_listed'])
    for age in [90,180]:
        if first+timedelta(days=age) > cb.TODAY: continue
        ts=(first+timedelta(days=age)).strftime('%Y%m%d')
        wb='https://web.archive.org/web/'+ts+'id_/'+r['website']
        p=CACHE/(r['slug']+f'_{age}.html')
        try:
            html=fetch(wb,p)
            about=cb.parse_about(html)
            # wayback actual capture timestamp is in banner/canonical; leave target when unavailable.
            status='ok' if about['downloads'] else 'no_download_parse'
            downloads=about['downloads']
        except Exception as e:
            status='error:'+str(e)[:80]; downloads=''
        out.append({'name':r['name'],'slug':r['slug'],'first_listed':r['first_listed'],'target_age_days':age,'target_date':ts,'current_downloads':r['downloads_current'],'wayback_downloads':downloads,'status':status,'url':wb})
with (DATA/'wayback_equal_age_sample.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ['name']); w.writeheader(); w.writerows(out)
print('wrote',len(out),'wayback sample rows')
