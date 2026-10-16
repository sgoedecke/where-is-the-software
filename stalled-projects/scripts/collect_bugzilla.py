#!/usr/bin/env python3
import csv, datetime as dt, json, time, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path.home()/"Code/where-is-the-software/stalled-projects"
DATA = ROOT/"data"; CACHE=DATA/"cache_bugzilla"; CACHE.mkdir(parents=True, exist_ok=True)
PRODUCTS=["Core","Firefox","Toolkit"]
START=dt.date(2022,1,1); END_EXCL=dt.date(2026,10,1)
def iso(d): return d.isoformat()
def minus_years(d,n):
    try: return d.replace(year=d.year-n)
    except ValueError: return d.replace(year=d.year-n, day=28)
def quarters():
    d=START
    while d<END_EXCL:
        nm=d.month+3; ny=d.year+(nm-1)//12; nm=((nm-1)%12)+1; nxt=dt.date(ny,nm,1)
        yield d,min(nxt,END_EXCL); d=nxt
def qlabel(d): return f"{d.year}Q{((d.month-1)//3)+1}"
def count(params):
    key=urllib.parse.urlencode(params, doseq=True)
    p=CACHE/(str(abs(hash(key)))+".json")
    if p.exists(): return json.loads(p.read_text())["count"]
    url="https://bugzilla.mozilla.org/rest/bug?"+key
    req=urllib.request.Request(url, headers={"User-Agent":"stalled-projects-research"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data=json.loads(resp.read())
    p.write_text(json.dumps(data, indent=2, sort_keys=True))
    time.sleep(0.25)
    return int(data["bug_count"] if "bug_count" in data else data.get("count",0))
rows=[]
for qs, qe in quarters():
    end_inc=qe-dt.timedelta(days=1); cutoff=minus_years(qs,5)
    base={"product":PRODUCTS,"resolution":"FIXED","chfield":"resolution","chfieldvalue":"FIXED","chfieldfrom":iso(qs),"chfieldto":iso(end_inc),"include_fields":"id","count_only":"1"}
    allc=count(base)
    old=dict(base); old.update({"f1":"creation_ts","o1":"lessthan","v1":iso(cutoff)})
    oldc=count(old)
    rows.append({"products":";".join(PRODUCTS),"quarter":qlabel(qs),"start":iso(qs),"end":iso(end_inc),"old_cutoff_created_before":iso(cutoff),"fixed_old_ge5y":oldc,"fixed_all":allc,"old_share":(oldc/allc if allc else ""),"query_all":urllib.parse.urlencode(base,doseq=True),"query_old":urllib.parse.urlencode(old,doseq=True)})
out=DATA/"mozilla_bugzilla_fixed_quarterly.csv"
with out.open("w", newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"wrote {out}")
