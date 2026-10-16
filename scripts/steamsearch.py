import json, urllib.request, urllib.parse, re, time, collections, html
terms=["remastered","remaster","remake","definitive edition","enhanced edition","anniversary edition","HD","classic","collection","reloaded","redux","director's cut","complete edition","trilogy","legacy","port"]
seen={}
for t in terms:
    for start in range(0,5000,100):
        u="https://store.steampowered.com/search/results/?"+urllib.parse.urlencode({"term":t,"sort_by":"Released_DESC","category1":"998","infinite":"1","start":start,"count":"100","cc":"us","l":"english"})
        for k in range(3):
            try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60)); break
            except Exception: time.sleep(5); d=None
        if not d: break
        h=d["results_html"]
        rows=re.findall(r'data-ds-appid="(\d+)".*?<span class="title">(.*?)</span>.*?search_released[^>]*>\s*(.*?)\s*</div>',h,re.S)
        if not rows: break
        stop=False
        for a,title,date in rows:
            seen[a]=(html.unescape(title),date.strip())
            m=re.search(r"(20\d\d)",date)
            if m and int(m.group(1))<2020: stop=True
        if stop: break
        time.sleep(0.4)
    print(t,len(seen),flush=True)
json.dump(seen,open("steam_remasters.json","w"))
