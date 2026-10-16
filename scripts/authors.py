import json, subprocess, collections, re
BOTRE=re.compile(r"(\[bot\]$|^kibanamachine$|bot$|-bot$|^github-actions)",re.I)
repos="PostHog/posthog microsoft/vscode elastic/kibana grafana/grafana getsentry/sentry supabase/supabase mattermost/mattermost vercel/next.js".split()
def fetch(q):
    items=[]
    for p in range(1,11):
        r=subprocess.run(["gh","api","-X","GET","search/issues","-f",f"q={q}","-f","per_page=100","-f",f"page={p}"],capture_output=True,text=True)
        if r.returncode: break
        d=json.loads(r.stdout); items+=d["items"]
        if len(d["items"])<100: break
    return items
print("repo\twindow\tPRs_human\tbot_PRs\thuman_authors\tPRs_per_author")
for repo in repos:
    for y in range(2022,2027):
        for (a,b) in [("09-01","09-14")]:
            it=fetch(f"repo:{repo} is:pr is:merged merged:{y}-{a}..{y}-{b}")
            hum=[i for i in it if not BOTRE.search(i["user"]["login"]) and i["user"]["type"]!="Bot"]
            au=collections.Counter(i["user"]["login"] for i in hum)
            print(repo,f"{y}-{a}",len(hum),len(it)-len(hum),len(au),round(len(hum)/max(len(au),1),2),sep="\t",flush=True)
