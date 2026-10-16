# Analyses used in reports/04-official-ports.md. Run from repo root after extracting data/gematsu_titles.tgz into ./gematsu
import json,glob,re,collections,html,csv,datetime
PORT=re.compile(r"coming to (PC|Steam|Switch|PS5|PS4|Xbox|iOS|Android|Mac)|(now )?available (now )?for (PC|Steam|Switch|PS5|Xbox|Mac)|\bport\b|PC version|Steam version|Switch 2 (Edition|version)|for (PC|Steam) (launches|announced|coming)|Mac version|(PC|Switch 2|PS5|Xbox Series) (version|port)|heading to",re.I)
REM=re.compile(r"remaster|remake|\bHD\b|definitive edition|enhanced edition|anniversary edition|director'?s cut|collection|classics|re-release|rerelease",re.I)
by=collections.defaultdict(lambda:[0,0,0,0])
for f in sorted(glob.glob("gematsu/*.json")):
    ym=f.split("/")[-1][:7]; y=ym[:4]
    if int(ym[5:])>9: continue
    for p in json.load(open(f)):
        t=html.unescape(p["title"]["rendered"]); by[y][0]+=1
        if REM.search(t): by[y][1]+=1
        if PORT.search(t): by[y][2 if "Switch 2" in t else 3]+=1
print("Gematsu Jan-Sep: year posts remaster port_switch2 port_other"); [print(y,*v) for y,v in sorted(by.items())]
d=json.load(open("data/gog_all.json")); tot=collections.Counter(); old=collections.Counter()
for x in d:
    s,r=x["storeReleaseDate"],x["releaseDate"]
    if not s or int(s[5:7])>9: continue
    sy=int(s[:4]); tot[sy]+=1
    if r and int(r[:4])<=sy-5: old[sy]+=1
print("GOG Jan-Sep additions / original>=5y old:"); [print(y,tot[y],old[y]) for y in range(2016,2027)]
