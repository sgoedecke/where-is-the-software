#!/usr/bin/env python3
"""Build Chrome Web Store active-extension cohort counts from Chrome-Stats advanced-search API."""
from __future__ import annotations
import csv, hashlib, json, time
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

OUT = Path('/Users/seangoedecke/Code/where-is-the-software/market-usage/chrome')
CACHE = OUT / 'cache'
DATA = OUT / 'data'
API = 'https://chrome-stats.com/api/chrome/advanced-search?client=web'
CACHE.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

BASE_ACTIVE_EXT = [
    {"column":"itemCategory","operator":"=","value":"extension"},
    {"column":"obsolete","operator":"!=","value":True},
]

def post(body: dict) -> dict:
    raw = json.dumps(body, sort_keys=True, separators=(',', ':')).encode()
    key = hashlib.sha256(raw).hexdigest()[:20]
    path = CACHE / f'advanced_search_{key}.json'
    body_path = CACHE / f'advanced_search_{key}.body.json'
    if path.exists():
        return json.loads(path.read_text())
    body_path.write_bytes(raw)
    req = Request(API, data=raw, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 cohort research; contact via chrome-stats public site',
    })
    for attempt in range(6):
        try:
            with urlopen(req, timeout=45) as resp:
                data = resp.read()
            break
        except HTTPError as e:
            data = e.read()
            if e.code == 429 and attempt < 5:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f'API HTTP {e.code}: {data[:500]!r}') from e
    path.write_bytes(data)
    time.sleep(0.35)
    return json.loads(data)

def count(conditions: list[dict]) -> int:
    body = {
        "index":"extension",
        "page":None,
        "exportData":False,
        "col":["name","userCount","creationDate","itemCategory","obsolete"],
        "sorting":"userCount",
        "sortDirection":"desc",
        "fields":{"operator":"AND","conditions":conditions},
    }
    d = post(body)
    if 'total' not in d:
        raise RuntimeError(d)
    return int(d['total'])

def top_items(start: str, end: str|None, limit_desc: str) -> list[dict]:
    conds = BASE_ACTIVE_EXT + [{"column":"creationDate","operator":">=","value":start}]
    if end:
        conds.append({"column":"creationDate","operator":"<","value":end})
    body = {
        "index":"extension",
        "page":None,
        "exportData":False,
        "col":["name","userCount","creationDate","ratingValue","ratingCount","metaCategories","author","url","website","isFeatured","overallRank"],
        "sorting":"userCount",
        "sortDirection":"desc",
        "fields":{"operator":"AND","conditions":conds},
    }
    d = post(body)
    out=[]
    for rank, it in enumerate(d.get('items', []), 1):
        cats = it.get('metaCategories') or []
        blob = ' '.join([it.get('name') or '', it.get('description') or '', ' '.join(cats)]).lower()
        
        import re
        ai = bool(re.search(r'\b(ai|chatgpt|gpt|claude|copilot|llm|gemini|deepseek|genai|kimi|manus|codex|browser operator)\b', blob))
        ai = ai or any(cat.lower() in {'ai','genai','bots'} for cat in cats)
        out.append({
            'slice': limit_desc,
            'slice_rank': rank,
            'id': it.get('id'),
            'name': it.get('name'),
            'creationDate': it.get('creationDate'),
            'userCount': it.get('userCount') or 0,
            'ratingValue': it.get('ratingValue'),
            'ratingCount': it.get('ratingCount') or 0,
            'author': it.get('author'),
            'website': it.get('website'),
            'isFeatured': it.get('isFeatured'),
            'overallRank': it.get('overallRank'),
            'metaCategories': ';'.join(cats),
            'ai_flag': ai,
            'url': it.get('url'),
        })
    return out

# Half-year cohorts from 2021 through current partial H2 2026.
cohorts=[]
for y in range(2021, 2027):
    cohorts.append((f'{y}H1', f'{y}-01-01', f'{y}-07-01'))
    cohorts.append((f'{y}H2', f'{y}-07-01', f'{y+1}-01-01'))
# truncate after current partial cohort, but keep end bound beyond current date.
cohorts = [c for c in cohorts if c[1] < '2027-01-01']
thresholds=[0,100,1000,10000,100000]
rows=[]
for label,start,end in cohorts:
    base = BASE_ACTIVE_EXT + [
        {"column":"creationDate","operator":">=","value":start},
        {"column":"creationDate","operator":"<","value":end},
    ]
    vals={}
    for th in thresholds:
        conds=list(base)
        if th>0:
            conds.append({"column":"userCount","operator":">=","value":th})
        vals[f'ge_{th}_users' if th else 'supply_active_extensions'] = count(conds)
    supply=vals['supply_active_extensions']
    rows.append({
        'cohort':label, 'start':start, 'end_exclusive':end,
        **vals,
        'pct_ge_100': round(vals['ge_100_users']/supply*100, 2) if supply else 0,
        'pct_ge_1000': round(vals['ge_1000_users']/supply*100, 2) if supply else 0,
        'pct_ge_10000': round(vals['ge_10000_users']/supply*100, 2) if supply else 0,
        'pct_ge_100000': round(vals['ge_100000_users']/supply*100, 3) if supply else 0,
    })

with (DATA/'cohort_counts.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

summary={
    'generated_at':'2026-10-15',
    'source':'Chrome-Stats /api/chrome/advanced-search?client=web, active extensions filter itemCategory=extension and obsolete!=true',
    'total_active_extensions': count(BASE_ACTIVE_EXT),
    'all_active_user_thresholds': {str(th): count(BASE_ACTIVE_EXT + ([{"column":"userCount","operator":">=","value":th}] if th else [])) for th in thresholds},
}
(DATA/'api_counts_summary.json').write_text(json.dumps(summary, indent=2))

recent_slices=[
    ('2025Q3','2025-07-01','2025-10-01'),('2025Q4','2025-10-01','2026-01-01'),
    ('2026Q1','2026-01-01','2026-04-01'),('2026Q2','2026-04-01','2026-07-01'),
    ('2026Q3','2026-07-01','2026-10-01'),('2026Q4_partial','2026-10-01','2027-01-01'),
]
tops=[]
for label,start,end in recent_slices:
    tops.extend(top_items(start,end,label))
with (DATA/'top_recent_items.csv').open('w', newline='') as f:
    fields=['slice','slice_rank','id','name','creationDate','userCount','ratingValue','ratingCount','author','website','isFeatured','overallRank','metaCategories','ai_flag','url']
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(tops)
print('wrote', DATA/'cohort_counts.csv', DATA/'top_recent_items.csv')
print(json.dumps(summary, indent=2))
