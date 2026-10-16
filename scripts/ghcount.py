import json, subprocess, sys, calendar, time
def count(q):
    for _ in range(4):
        r=subprocess.run(["gh","api","graphql","-f",f'query=query{{search(query:"{q}",type:ISSUE,first:0){{issueCount}}}}'],capture_output=True,text=True)
        if r.returncode==0: return json.loads(r.stdout)["data"]["search"]["issueCount"]
        time.sleep(10)
    return None
def months():
    for y in range(2022,2027):
        for m in range(1,13):
            if (y,m)>(2026,9): return
            yield y,m
name,base=sys.argv[1],sys.argv[2]
out=open(f"{name}.tsv","w")
for y,m in months():
    d=calendar.monthrange(y,m)[1]
    c=count(f"{base} {sys.argv[3] if len(sys.argv)>3 else 'created'}:{y}-{m:02d}-01..{y}-{m:02d}-{d}")
    print(f"{y}-{m:02d}\t{c}",file=out,flush=True)
