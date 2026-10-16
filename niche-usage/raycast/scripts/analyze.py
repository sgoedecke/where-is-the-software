import csv, json, re, statistics
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path
BASE=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/raycast')
DATA=BASE/'data'
def read_csv(p):
    with open(p,newline='') as f: return list(csv.DictReader(f))
first=read_csv(DATA/'extension_first_listed_git.csv')
store=read_csv(DATA/'store_extensions_current.csv')
store_by_rel={r['relative_path']:r for r in store}

def cohort_q(date):
    y=int(date[:4]); m=int(date[5:7]); q=(m-1)//3+1; return f'{y}Q{q}'
def cohort_h(date):
    y=int(date[:4]); m=int(date[5:7]); return f'{y}H{1 if m<=6 else 2}'
def ai_flag(r):
    text=' '.join([r.get('title',''),r.get('description',''),r.get('categories',''),r.get('prompt_examples',''),r.get('slug','')]).lower()
    pats=['ai','llm','gpt','openai','anthropic','claude','gemini','ollama','mcp','model context protocol','prompt','chatgpt','cursor','agent','deepseek','deep seek','whisper','copilot','antigravity','cursor','comet']
    return any(re.search(r'\b'+re.escape(p)+r'\b', text) for p in pats) or 'AI Extensions'.lower() in text

def int0(x):
    try: return int(float(x))
    except: return 0
thresholds=[1000,10000,100000]
rows=[]
for fr in first:
    sr=store_by_rel.get(fr['relative_path'])
    dl=int0(sr['download_count']) if sr else None
    rows.append({**fr, 'quarter':cohort_q(fr['date']), 'half':cohort_h(fr['date']), 'active': bool(sr), 'downloads': dl,
                 'title': sr.get('title') if sr else '', 'store_url': sr.get('store_url') if sr else '',
                 'owner': sr.get('owner_handle') if sr else '', 'categories': sr.get('categories') if sr else '',
                 'description': sr.get('description') if sr else '', 'ai_related': ai_flag(sr) if sr else False,
                 'platforms': sr.get('platforms') if sr else ''})
# unmatched active store (package exists in current store but no git add record, e.g. renamed path anomaly)
unmatched=[r for r in store if r['relative_path'] not in {f['relative_path'] for f in first}]
print('first',len(first),'store',len(store),'joined_active',sum(r['active'] for r in rows),'unmatched_store',len(unmatched))
# cohort tables
def cohort_table(key):
    groups=defaultdict(list)
    for r in rows: groups[r[key]].append(r)
    out=[]
    for c in sorted(groups):
        gs=groups[c]; active=[r for r in gs if r['active']]; dls=[r['downloads'] for r in active if r['downloads'] is not None]
        out.append({
            'cohort':c,'supply_git_adds':len(gs),'active_with_downloads':len(active),
            'active_share': round(len(active)/len(gs),3) if gs else None,
            'downloads_median_active': int(statistics.median(dls)) if dls else 0,
            'downloads_p90_active': int(statistics.quantiles(dls,n=10)[8]) if len(dls)>=10 else (max(dls) if dls else 0),
            'downloads_total_active': sum(dls),
            'ge_1k':sum(1 for r in active if r['downloads']>=1000),
            'ge_10k':sum(1 for r in active if r['downloads']>=10000),
            'ge_100k':sum(1 for r in active if r['downloads']>=100000),
            'ai_related_active':sum(1 for r in active if r['ai_related']),
            'ai_ge_10k':sum(1 for r in active if r['ai_related'] and r['downloads']>=10000),
        })
    return out
for name,key in [('quarter','quarter'),('half','half')]:
    out=cohort_table(key)
    with open(DATA/f'cohorts_{name}.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
# top recent: 2025+ active
recent=[r for r in rows if r['active'] and r['date']>='2025-01-01']
recent.sort(key=lambda r:r['downloads'] or 0, reverse=True)
with open(DATA/'top_recent_2025plus.csv','w',newline='') as f:
    fields=['date','quarter','slug','title','downloads','ai_related','categories','platforms','owner','description','store_url']
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows([{k:r.get(k) for k in fields} for r in recent[:75]])
# distribution
with open(DATA/'summary.json','w') as f:
    json.dump({
        'git_supply_total':len(first),'store_active_total':len(store),'joined_active':sum(r['active'] for r in rows),
        'unmatched_store':len(unmatched),
        'download_thresholds':thresholds,
        'current_download_distribution':{str(p): int(statistics.quantiles([int0(s['download_count']) for s in store],n=100)[p-1]) for p in [10,25,50,75,90,95,99]},
        'max_downloads':max(int0(s['download_count']) for s in store),
    }, f, indent=2)
print(open(DATA/'summary.json').read())
print('\nHalf cohorts')
for r in cohort_table('half'):
    print(r)
print('\nTop recent')
for r in recent[:30]:
    print(r['date'], r['title'], r['downloads'], 'AI' if r['ai_related'] else '', r['owner'], r['categories'], r['store_url'])
