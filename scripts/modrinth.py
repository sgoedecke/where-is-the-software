# Modrinth mod listings created Jan-Sep by year, by download threshold and AI-code disclosure.
import json,urllib.request,urllib.parse,datetime as dt
def st(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())
def hits(f):
    u='https://api.modrinth.com/v2/search?'+urllib.parse.urlencode({'limit':1,'facets':json.dumps(f)})
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research/1.0'})))['total_hits']
for y in range(2021,2027):
    b=[['project_type:mod'],[f'created_timestamp>={st(f"{y}-01-01")}'],[f'created_timestamp<{st(f"{y}-10-01")}']]
    print(y,*[hits(b+([[f'downloads>={t}']] if t else [])) for t in (0,1000,10000,100000)],hits(b+[['disclosure_types:ai_content_code']]))
