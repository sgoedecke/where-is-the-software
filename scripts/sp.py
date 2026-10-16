import json, urllib.request, sys, concurrent.futures as cf, time
doms="""status.atlassian.com status.zoom.us status.dropbox.com status.twilio.com www.shopifystatus.com status.datadoghq.com status.pagerduty.com discordstatus.com www.redditstatus.com status.figma.com status.asana.com status.box.com status.digitalocean.com www.netlifystatus.com status.fastly.com www.cloudflarestatus.com status.mailchimp.com status.hubspot.com www.intercomstatus.com status.squarespace.com status.linear.app www.vercel-status.com status.sentry.io status.npmjs.org status.circleci.com status.mongodb.com status.epicgames.com status.miro.com www.canvastatus.com status.hashicorp.com status.notion.so status.gitlab.com status.twitch.tv status.zapier.com status.airtable.com status.loom.com status.newrelic.com status.sendgrid.com status.mailgun.com status.postmarkapp.com status.segment.com status.launchdarkly.com status.algolia.com status.auth0.com status.okta.com status.docker.com status.npmjs.org status.render.com status.fly.io status.supabase.com status.planetscale.com status.cloudinary.com status.contentful.com status.webflow.com status.wix.com status.godaddy.com status.trello.com status.bitbucket.org status.jira.com status.grammarly.com status.1password.com status.lastpass.com status.discord.com status.roblox.com status.playstation.com status.riotgames.com status.ea.com www.githubstatus.com status.anthropic.com status.openai.com status.cursor.com status.huggingface.co status.replicate.com status.groq.com""".split()
doms=list(dict.fromkeys(doms))
def get(u):
    req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req,timeout=30))
def scrape(d):
    rows=[]
    try:
        h=get(f"https://{d}/history.json")
    except Exception as e:
        return d,None,str(e)[:80]
    name=h["page_status"]["page"]["name"]; created=h["page_status"]["page"]["created_at"]
    for p in range(1,26):
        try: h=get(f"https://{d}/history.json?page={p}")
        except Exception as e: break
        for m in h["months"]:
            for i in m["incidents"]:
                rows.append({"dom":d,"name":name,"year":m["year"],"month":m["name"],"impact":i.get("impact"),"title":i.get("name")})
        if h["months"] and h["months"][-1]["year"]<2021: break
        time.sleep(0.3)
    return d,{"name":name,"created":created,"rows":rows},None
res={}
with cf.ThreadPoolExecutor(8) as ex:
    for d,r,err in ex.map(scrape,doms):
        if r: res[d]=r; print("OK",d,r["name"],r["created"][:10],len(r["rows"]),flush=True)
        else: print("FAIL",d,err,flush=True)
json.dump(res,open("statuspages.json","w"))
