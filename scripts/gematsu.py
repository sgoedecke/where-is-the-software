import json, urllib.request, os, time, calendar
for y in range(2021,2027):
    for m in range(1,13):
        if (y,m)>(2026,10): break
        f=f"gematsu/{y}-{m:02d}.json"
        if os.path.exists(f): continue
        posts=[]; p=1
        a=f"{y}-{m:02d}-01T00:00:00"; ny,nm=(y+(m==12),m%12+1); b=f"{ny}-{nm:02d}-01T00:00:00"
        while True:
            u=f"https://www.gematsu.com/wp-json/wp/v2/posts?per_page=100&page={p}&after={a}&before={b}&_fields=date,title,link"
            try:
                r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60)
                d=json.load(r); tp=int(r.headers.get("X-WP-TotalPages","1"))
            except Exception as e:
                print("err",u,e); time.sleep(5); 
                if p>tp if 'tp' in dir() else False: break
                continue
            posts+=d
            if p>=tp: break
            p+=1; time.sleep(0.3)
        json.dump(posts,open(f,"w")); print(y,m,len(posts),flush=True)
