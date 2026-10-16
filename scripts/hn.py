# Show HN monthly counts via HN Algolia API, total and by points threshold. Output: data/hn_show_monthly.tsv
import json,urllib.request,urllib.parse,datetime as dt
from concurrent.futures import ThreadPoolExecutor
def rng(y,m):
    s=int(dt.datetime(y,m,1,tzinfo=dt.timezone.utc).timestamp()); y2,m2=(y+1,1) if m==12 else (y,m+1)
    return s,int(dt.datetime(y2,m2,1,tzinfo=dt.timezone.utc).timestamp())
def cnt(y,m,tags,extra=""):
    s,e=rng(y,m); q=urllib.parse.urlencode({"tags":tags,"hitsPerPage":0,"numericFilters":f"created_at_i>={s},created_at_i<{e}"+extra})
    return json.load(urllib.request.urlopen("https://hn.algolia.com/api/v1/search?"+q))["nbHits"]
months=[(y,m) for y in range(2022,2027) for m in range(1,13) if (y,m)<=(2026,9)]
def row(ym):
    y,m=ym
    return (f"{y}-{m:02d}",cnt(y,m,"story"),cnt(y,m,"show_hn,story"),*[cnt(y,m,"show_hn,story",f",points>={p}") for p in (10,50,100)],cnt(y,m,"story",",points>=100"))
with ThreadPoolExecutor(8) as ex: rows=list(ex.map(row,months))
print("month\tall_stories\tshow_hn\tshow_hn_pts10\tshow_hn_pts50\tshow_hn_pts100\tall_stories_pts100")
for r in rows: print("\t".join(map(str,r)))
