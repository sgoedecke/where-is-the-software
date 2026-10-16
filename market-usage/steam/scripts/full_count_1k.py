"""Full (unsampled) count of games reaching >=1k / >=5k reviews in first 90 days.
Candidates: every game in the supply crawl whose current review total (from search tooltip) is >=1000."""
import csv, json, time, datetime as dt, urllib.request, collections, calendar
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
CACHE = Path('cache/hist'); CACHE.mkdir(parents=True, exist_ok=True)
rows = [r for r in csv.DictReader(open('data/steam_supply_apps.csv'))
        if r['current_reviews_search'] and int(r['current_reviews_search'].replace(',', '')) >= 1000]
def get(appid):
    p = CACHE / f'{appid}.json'
    if p.exists():
        try: return json.load(open(p))
        except Exception: pass
    url = f'https://store.steampowered.com/appreviewhistogram/{appid}?l=english&review_score_preference=0&review_type=all&purchase_type=all'
    for i in range(5):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30))
            json.dump(d, open(p, 'w')); return d
        except Exception:
            time.sleep(5 * (i + 1))
    return None
def early(h, rd, days):
    if not h or h.get('success') != 1: return None
    res = h['results']; cutoff = rd + dt.timedelta(days=days); tot = 0
    for it in res.get('rollups', []):
        s = dt.datetime.utcfromtimestamp(int(it['date'])).date()
        if res.get('rollup_type') == 'week': e = s + dt.timedelta(days=7)
        else: e = dt.date(s.year, s.month, calendar.monthrange(s.year, s.month)[1]) + dt.timedelta(days=1)
        if e <= rd or s >= cutoff: continue
        tot += int(it.get('recommendations_up') or 0) + int(it.get('recommendations_down') or 0)
    return tot
def work(r):
    h = get(r['appid']); return r, (early(h, dt.date.fromisoformat(r['release_date']), 90) if h else None), (h or {}).get('results', {}).get('rollup_type')
with ThreadPoolExecutor(6) as ex: out = list(ex.map(work, rows))
c = collections.defaultdict(collections.Counter)
with open('data/full_count_90d_candidates.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['appid', 'title', 'release_date', 'cohort', 'current_reviews', 'reviews_90d', 'rollup_type'])
    for r, v, rt in out:
        w.writerow([r['appid'], r['title'], r['release_date'], r['cohort'], r['current_reviews_search'], v, rt])
        k = r['cohort']; c[k]['cand'] += 1
        if v is None: c[k]['err'] += 1; continue
        for t in (1000, 2000, 5000):
            if v >= t: c[k][t] += 1
print('cohort cand err >=1k >=2k >=5k')
for k in sorted(c): print(k, c[k]['cand'], c[k]['err'], c[k][1000], c[k][2000], c[k][5000])
