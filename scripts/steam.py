import json, urllib.request, time, concurrent.futures as cf, os
apps=[]
for p in (0,1,2):
    apps+= [int(k) for k in json.load(open(f"spy{p}.json")).keys()]
apps=list(dict.fromkeys(apps))
os.makedirs("news",exist_ok=True)
def fetch(a):
    f=f"news/{a}.json"
    if os.path.exists(f): return
    items=[]; end=None
    for _ in range(6):
        u=f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={a}&count=1000&maxlength=1&feeds=steam_community_announcements"+(f"&enddate={end}" if end else "")
        for t in range(3):
            try: d=json.load(urllib.request.urlopen(u,timeout=30))["appnews"]; break
            except Exception as e: time.sleep(5); d=None
        if not d: break
        ni=[{"date":i["date"],"tags":i.get("tags"),"title":i["title"]} for i in d.get("newsitems",[])]
        items+=ni
        if len(ni)<1000 or ni[-1]["date"]<1609459200: break
        end=ni[-1]["date"]-1
    json.dump(items,open(f,"w"))
with cf.ThreadPoolExecutor(4) as ex: list(ex.map(fetch,apps))
print("done",len(apps))
