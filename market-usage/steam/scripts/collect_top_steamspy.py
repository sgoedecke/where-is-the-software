#!/usr/bin/env python3
import csv, json, time, urllib.request
from pathlib import Path
import sys
sys.path.insert(0, '/Users/seangoedecke/Code/where-is-the-software/market-usage/steam/scripts')
import collect_steam as cs
BASE=cs.BASE; CACHE=cs.CACHE; DATA=cs.DATA
(CACHE/'steamspy').mkdir(exist_ok=True)

def steamspy_page(page):
    url=f'https://steamspy.com/api.php?request=all&page={page}'
    path=CACHE/'steamspy'/f'all_page_{page}.json'
    return cs.fetch_json_cached(url,path)

def main():
    apps=cs.read_supply_csv(); by={int(a['appid']):a for a in apps}
    rows=[]
    empty=0
    for page in range(0,80):
        try: data=steamspy_page(page)
        except Exception as e:
            print('steamspy error',page,e); break
        if not data:
            empty+=1
            if empty>=2: break
            continue
        for k,v in data.items():
            try: appid=int(v.get('appid') or k)
            except Exception: continue
            if appid in by:
                a=by[appid]
                if a['release_date']>='2025-01-01':
                    cur=int(v.get('positive') or 0)+int(v.get('negative') or 0)
                    rr=dict(a)
                    rr.update({'steamspy_positive':v.get('positive',0),'steamspy_negative':v.get('negative',0),'steamspy_reviews':cur,'owners':v.get('owners',''),'ccu':v.get('ccu',''),'steamspy_developer':v.get('developer',''),'steamspy_publisher':v.get('publisher','')})
                    rows.append(rr)
        print('page',page,'recent candidates',len(rows))
        time.sleep(1.1)
    rows.sort(key=lambda r:int(r.get('steamspy_reviews') or 0), reverse=True)
    recent=rows[:80]
    hist={}
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for rr in ex.map(cs.fetch_hist_one, recent): hist[int(rr['appid'])]=rr
    ai={}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for rr in ex.map(cs.fetch_ai_one, recent): ai[int(rr['appid'])]=rr
    details={}
    for a in recent:
        appid=int(a['appid']); url=f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=US&l=english'
        try:
            d=cs.fetch_json_cached(url, CACHE/'appdetails'/f'{appid}.json').get(str(appid),{}).get('data',{})
            details[appid]={'developers':'; '.join(d.get('developers') or []),'publishers':'; '.join(d.get('publishers') or []),'genres':'; '.join(g.get('description','') for g in (d.get('genres') or [])),'is_free':d.get('is_free')}
        except Exception as e: details[appid]={'developers':'','publishers':'','genres':'','is_free':'','details_error':str(e)}
        time.sleep(.3)
    out=[]
    for a in recent:
        appid=int(a['appid']); r=dict(a); r.update(hist.get(appid,{})); r.update(ai.get(appid,{})); r.update(details.get(appid,{})); out.append(r)
    out.sort(key=lambda r:int(r.get('reviews_90d') or -1), reverse=True)
    fields=['appid','title','release_date','cohort','reviews_90d','reviews_365d','reviews_current_hist','steamspy_reviews','steamspy_positive','steamspy_negative','owners','ccu','developers','publishers','steamspy_developer','steamspy_publisher','genres','is_free','ai_disclosure','ai_disclosure_text']
    cs.write_csv(DATA/'top_recent_by_90d_reviews.csv', out[:50], fields)
    print('wrote', DATA/'top_recent_by_90d_reviews.csv')
if __name__=='__main__': main()
