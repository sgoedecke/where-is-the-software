import csv,json,subprocess
from pathlib import Path
BASE=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/raycast')
rows=list(csv.DictReader(open(BASE/'data/top_recent_2025plus.csv')))
out=[]
for r in rows[:75]:
    rel=f"extensions/{r['slug']}/package.json"
    p=subprocess.run(['git','-C',str(BASE/'cache/extensions-repo'),'show','origin/main:'+rel],text=True,capture_output=True,timeout=30)
    pkg={}
    if p.returncode==0:
        try: pkg=json.loads(p.stdout)
        except Exception: pkg={}
    owner_field=pkg.get('owner','') if isinstance(pkg,dict) else ''
    title=r['title'].lower(); desc=r['description'].lower(); owner=(owner_field or r['owner']).lower()
    official = bool(owner_field) or owner in {'github','raycast','the-browser-company','anysphere','firecrawl'}
    if any(x in title+' '+desc for x in ['mcp','claude','copilot','cursor','deepseek','whisper','agent','llm','comet','antigravity','chatgpt','gpt']): ai='yes'
    else: ai='yes' if r['ai_related']=='True' else 'no'
    # coarse classification from title/description, not external repo creation dates
    if official: kind='official/company-owned integration'
    elif any(x in title for x in ['calendar','ghostty','siri','youtube','instagram','everything','obsidian','bartender','betterdisplay','google lens','slack','notion']): kind='third-party wrapper for existing app/service'
    elif ai=='yes': kind='AI/agent utility or wrapper'
    else: kind='standalone Raycast utility'
    r.update({'manifest_owner':owner_field,'official_or_company_owned':official,'top_item_kind':kind,'ai_manual':ai})
    out.append(r)
with open(BASE/'data/top_recent_2025plus_annotated.csv','w',newline='') as f:
    fields=list(out[0].keys())
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
for r in out[:30]: print(r['title'], r['downloads'], r['ai_manual'], r['manifest_owner'], r['top_item_kind'])
