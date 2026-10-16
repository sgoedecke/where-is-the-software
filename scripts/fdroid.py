# F-Droid first-admission dates: union of main + archive index-v1, earliest 'added' per package.
# curl -LO https://f-droid.org/repo/index-v1.jar (-> main.jar) ; https://f-droid.org/archive/index-v1.jar (-> archive.jar); unzip index-v1.json from each
import json,datetime as dt,collections,sys
by={}
for f in sys.argv[1:]:
    for a in json.load(open(f))['apps']:
        k=a['packageName']
        if k not in by or a['added']<by[k]['added']: by[k]=a
cm=collections.Counter(dt.datetime.fromtimestamp(a['added']/1000,dt.timezone.utc).strftime('%Y-%m') for a in by.values())
for k in sorted(cm): print(k,cm[k],sep='\t')
# Submission demand: GitLab API x-total header, e.g.
# curl -sI "https://gitlab.com/api/v4/projects/fdroid%2Ffdroiddata/merge_requests?state=all&created_after=2026-09-01T00:00:00Z&created_before=2026-10-01T00:00:00Z&per_page=1&search=new%20app&in=title"
