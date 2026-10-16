import json, urllib.request, calendar
B="https://bugzilla.mozilla.org/rest/bug?count_only=1&product=Firefox&product=Core&product=Toolkit"
def c(extra,y,m):
    d=calendar.monthrange(y,m)[1]
    u=f"{B}&f1=creation_ts&o1=greaterthaneq&v1={y}-{m:02d}-01&f2=creation_ts&o2=lessthan&v2={y+(m==12)}-{m%12+1:02d}-01{extra}"
    return json.load(urllib.request.urlopen(u,timeout=60))["bug_count"]
print("month\tall\tregression\tcrash\tsec_hi_crit")
for y in range(2021,2027):
    for m in range(1,13):
        if (y,m)>(2026,9): break
        r=[c("",y,m),c("&keywords=regression&keywords_type=allwords",y,m),c("&keywords=crash&keywords_type=allwords",y,m),c("&keywords=sec-high%20sec-critical&keywords_type=anywords",y,m)]
        print(f"{y}-{m:02d}",*r,sep="\t",flush=True)
