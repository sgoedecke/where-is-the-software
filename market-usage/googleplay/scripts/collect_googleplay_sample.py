#!/usr/bin/env python3
import csv, json, re, time, signal
from datetime import datetime, date
from pathlib import Path
from email.utils import parsedate_to_datetime
from google_play_scraper import app, search

ROOT=Path('/Users/seangoedecke/Code/where-is-the-software/market-usage/googleplay')
CACHE=ROOT/'cache'/'googleplay'
DATA=ROOT/'data'
CACHE.mkdir(parents=True, exist_ok=True); DATA.mkdir(exist_ok=True)

SEARCH_TERMS = [
    # broad app intents/categories
    'ai assistant','ai chat','chatbot','photo editor','video editor','camera filter','pdf scanner','document scanner','notes app','todo list','calendar planner','habit tracker','budget planner','expense tracker','crypto wallet','stock trading','banking','fitness tracker','workout planner','calorie counter','meal planner','meditation','sleep tracker','period tracker','telehealth','language learning','math solver','homework helper','kids learning','weather radar','local news','sports scores','music player','podcast player','ebook reader','audiobook','file manager','vpn','password manager','launcher','keyboard','wallpaper','icon pack','qr scanner','translator','travel planner','flight tracker','hotel booking','food delivery','grocery delivery','ride sharing','dating','social network','messenger','video call','email client','job search','resume builder','real estate','rental homes','shopping deals','coupon','ticket booking','event planner','recipe','plant identifier','pet care','baby tracker','pregnancy','car maintenance','ev charging','parking','public transit','map navigation','delivery driver','small business','invoice maker','pos system','time tracking','team chat','project management',
    # games and genres
    'new puzzle game','word game','merge game','idle rpg','battle royale','casual game','solitaire','sudoku','coloring book','brain training','escape room game','kids game','ai game',
    # explicit recent-year probes, intentionally biased toward recent launches
    '2026 app','2025 app','new ai app 2026','new android app','new productivity app','new fitness app','new finance app','new photo app','new game 2026',
    # named AI entrants/newer products
    'chatgpt','gemini ai','perplexity ai','claude ai','grok ai','copilot ai','character ai','ai image generator','ai video generator','ai photo editor','ai girlfriend','ai music generator'
]

def parse_released(s):
    if not s: return None
    for fmt in ('%b %d, %Y','%b %Y','%Y'):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass
    try:
        return parsedate_to_datetime(s).date().isoformat()
    except Exception:
        return None

def cohort_half(ds):
    if not ds: return 'unknown'
    d=date.fromisoformat(ds)
    return f"{d.year}H{1 if d.month<=6 else 2}"

def is_ai(row):
    text=' '.join(str(row.get(k,'') or '') for k in ['title','summary','description','developer','genre']).lower()
    pats=[' ai','ai ','artificial intelligence','chatgpt','gpt','gemini','claude','perplexity','grok','chatbot','image generator','voice generator','llm','character ai','copilot','stable diffusion','midjourney']
    return any(p in text for p in pats)

class Timeout(Exception): pass
def _alarm(signum, frame): raise Timeout('request timeout')
signal.signal(signal.SIGALRM, _alarm)

def search_cache(term):
    safe=re.sub(r'[^a-zA-Z0-9]+','_',term).strip('_')[:80]
    p=CACHE/f'search_{safe}.json'
    if p.exists():
        return json.loads(p.read_text())
    try:
        signal.alarm(20)
        res=search(term, n_hits=40, lang='en', country='us')
        signal.alarm(0)
    except Exception as e:
        signal.alarm(0)
        print('SEARCH_FAIL', term, type(e).__name__, e, flush=True); res=[]
    p.write_text(json.dumps(res, ensure_ascii=False, indent=2))
    time.sleep(0.15)
    return res

def app_cache(app_id):
    p=CACHE/f'app_{app_id}.json'
    if p.exists():
        return json.loads(p.read_text())
    try:
        signal.alarm(20)
        res=app(app_id, lang='en', country='us')
        signal.alarm(0)
    except Exception as e:
        signal.alarm(0)
        print('APP_FAIL', app_id, type(e).__name__, e, flush=True); return None
    p.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    time.sleep(0.08)
    return res

def main():
    discovery={}
    for term in SEARCH_TERMS:
        for rank, item in enumerate(search_cache(term), start=1):
            aid=item.get('appId')
            if aid and aid not in discovery:
                discovery[aid]={'first_term':term,'first_rank':rank,'search_installs':item.get('installs')}
    print('unique search apps', len(discovery), flush=True)
    rows=[]
    for i,(aid,meta) in enumerate(discovery.items(), start=1):
        det=app_cache(aid)
        if not det: continue
        released=parse_released(det.get('released'))
        row={
            'appId': aid,
            'title': det.get('title'),
            'developer': det.get('developer'),
            'genre': det.get('genre'),
            'released_raw': det.get('released'),
            'released': released,
            'cohort': cohort_half(released),
            'installs': det.get('installs'),
            'minInstalls': det.get('minInstalls'),
            'realInstalls': det.get('realInstalls'),
            'ratings': det.get('ratings'),
            'reviews': det.get('reviews'),
            'score': det.get('score'),
            'free': det.get('free'),
            'offersIAP': det.get('offersIAP'),
            'adSupported': det.get('adSupported'),
            'developerWebsite': det.get('developerWebsite'),
            'url': det.get('url'),
            'first_term': meta['first_term'],
            'first_rank': meta['first_rank'],
            'summary': det.get('summary'),
            'description': (det.get('description') or '')[:1000],
        }
        row['ai_flag']=is_ai(row)
        rows.append(row)
        if i%100==0: print('details', i, 'rows', len(rows), flush=True)
    rows.sort(key=lambda r:(r['released'] or '', int(r.get('realInstalls') or 0)), reverse=True)
    keys=list(rows[0].keys())
    with (DATA/'googleplay_search_sample_apps.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    # cohort summary for currently surviving/search-visible sample
    cohorts={}
    for r in rows:
        c=r['cohort']
        if c=='unknown': continue
        cohorts.setdefault(c, {'cohort':c,'sample_n':0,'ge_500':0,'ge_5000':0,'ge_50000':0,'ge_1000000':0,'ai_n':0})
        rec=cohorts[c]; rec['sample_n']+=1
        inst=int(r.get('realInstalls') or 0)
        for t in [500,5000,50000,1000000]:
            if inst>=t: rec[f'ge_{t}']+=1
        if r['ai_flag']: rec['ai_n']+=1
    for rec in cohorts.values():
        for k in ['ge_500','ge_5000','ge_50000','ge_1000000','ai_n']:
            rec[k+'_pct']=rec[k]/rec['sample_n'] if rec['sample_n'] else 0
    out=[cohorts[k] for k in sorted(cohorts)]
    with (DATA/'googleplay_search_sample_cohorts.csv').open('w', newline='') as f:
        keys=list(out[0].keys()); w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
    recent=[r for r in rows if r['released'] and r['released']>='2025-01-01']
    recent.sort(key=lambda r:int(r.get('realInstalls') or 0), reverse=True)
    top=recent[:50]
    top_keys=['title','appId','developer','genre','released','realInstalls','ratings','score','ai_flag','first_term','developerWebsite','url']
    with (DATA/'googleplay_top_recent_search_sample.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=top_keys); w.writeheader(); w.writerows([{k:r.get(k) for k in top_keys} for r in top])
    print('rows', len(rows), 'recent', len(recent), 'top_ai', sum(1 for r in top if r['ai_flag']), flush=True)

if __name__ == '__main__':
    main()
