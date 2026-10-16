import json, urllib.request, time, os
out=[]; p=1
while True:
    f=f"gog/p{p}.json"
    if not os.path.exists(f):
        u=f"https://catalog.gog.com/v1/catalog?order=desc:storeReleaseDate&limit=48&page={p}&productType=in:game,pack"
        d=json.load(urllib.request.urlopen(u,timeout=60)); json.dump(d,open(f,"w")); time.sleep(0.5)
    d=json.load(open(f))
    for x in d["products"]:
        out.append({k:x.get(k) for k in ("id","title","releaseDate","storeReleaseDate","productType","developers","publishers","genres","editions")})
    if p>=d["pages"]: break
    p+=1
json.dump(out,open("gog_all.json","w")); print(len(out), out[0], out[-1])
