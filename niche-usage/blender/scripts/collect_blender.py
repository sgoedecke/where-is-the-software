#!/usr/bin/env python3
import csv, json, os, re, time, html as html_lib, urllib.request, urllib.parse, urllib.error, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, timezone
from pathlib import Path

OUT = Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/blender')
CACHE = OUT/'cache'
DATA = OUT/'data'
PAGES = CACHE/'pages'
for p in [CACHE, DATA, PAGES, CACHE/'github', CACHE/'wayback']:
    p.mkdir(parents=True, exist_ok=True)
UA = 'Mozilla/5.0 (usage cohort research; contact via extensions.blender.org)'
TODAY = date(2026,10,15)

MONTHS = {m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
MONTHS_ABBR = {m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}

def fetch_url(url, path=None, force=False, timeout=30):
    if path and path.exists() and not force:
        return path.read_text(encoding='utf-8', errors='replace')
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    last = None
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
            text = raw.decode('utf-8','replace')
            if path:
                path.write_text(text, encoding='utf-8')
            return text
        except Exception as e:
            last = e
            time.sleep(0.7*(i+1))
    raise last

def strip_tags(s):
    s = re.sub(r'<script[\s\S]*?</script>', ' ', s, flags=re.I)
    s = re.sub(r'<style[\s\S]*?</style>', ' ', s, flags=re.I)
    return ' '.join(html_lib.unescape(re.sub(r'<[^>]+>', ' ', s)).split())

def parse_date_title(t):
    # Tuesday 13th, October 2026 - 06:54 OR Sunday 11th, October 2026 - 22:43
    m = re.search(r'(\d{1,2})(?:st|nd|rd|th),\s+([A-Za-z]+)\s+(\d{4})', t or '')
    if not m: return ''
    return f"{int(m.group(3)):04d}-{MONTHS.get(m.group(2),0):02d}-{int(m.group(1)):02d}"

def parse_human_date(s):
    # Oct. 11th, 2026 or October 11th, 2026
    m = re.search(r'([A-Za-z]+)\.?,?\s+(\d{1,2})(?:st|nd|rd|th),\s+(\d{4})', s or '')
    if not m: return ''
    mon = MONTHS.get(m.group(1)) or MONTHS_ABBR.get(m.group(1)[:3])
    if not mon: return ''
    return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"

def parse_int(s):
    if s is None: return 0
    return int(re.sub(r'[^0-9]', '', str(s)) or 0)

def slug_from_url(url):
    parts = urllib.parse.urlparse(url).path.strip('/').split('/')
    return parts[-1] if parts else ''

def type_dir(t):
    return 'add-ons' if t == 'add-on' else 'themes' if t == 'theme' else t+'s'

def safe_name(t, slug, suffix):
    return f"{t.replace('/','_')}__{slug.replace('/','_')}__{suffix}.html"

def parse_versions(html):
    versions=[]
    details = re.findall(r'<details\b[\s\S]*?</details>', html, flags=re.I)
    for sec in details:
        vm = re.search(r'<span class="version-string">\s*([^<]+?)\s*</span>', sec)
        tm = re.search(r'title="([^"]*\d{4}[^"]*)"', sec)
        dm = re.search(r'<dt>\s*Downloads\s*</dt>\s*<dd>\s*([\d,]+)\s*</dd>', sec, flags=re.I)
        sm = re.search(r'<dt>\s*Status\s*</dt>[\s\S]*?<span>\s*([^<]+)\s*</span>', sec, flags=re.I)
        versions.append({
            'version': html_lib.unescape(vm.group(1).strip()) if vm else '',
            'published': parse_date_title(html_lib.unescape(tm.group(1))) if tm else '',
            'downloads': parse_int(dm.group(1)) if dm else 0,
            'status': html_lib.unescape(sm.group(1).strip()) if sm else ''
        })
    return versions

def parse_about(html):
    title_date = ''
    m = re.search(r'<dt>\s*Published\s*</dt>\s*<dd[^>]*title="([^"]+)"', html, flags=re.I)
    if m: title_date = parse_date_title(html_lib.unescape(m.group(1)))
    dm = re.search(r'<dt>\s*(?:Downloads|Installs)\s*</dt>\s*<dd>\s*([\d,]+)\s*</dd>', html, flags=re.I)
    downloads = parse_int(dm.group(1)) if dm else 0
    links=[]
    for m in re.finditer(r'<a\b[^>]*href="(https?://[^"]+)"[^>]*>([\s\S]*?)</a>', html, flags=re.I):
        href=html_lib.unescape(m.group(1))
        text=strip_tags(m.group(2))[:200]
        if any(domain in href for domain in ['extensions.blender.org','www.blender.org','analytics.blender.org','builder.blender.org','opendata.blender.org','flamenco.blender.org','youtube.com','instagram.com','facebook.com','linkedin.com','mastodon.social','tiktok.com','bilibili.com']):
            continue
        if 'gnu.org/licenses' in href or 'creativecommons.org' in href or 'spdx.org' in href:
            continue
        links.append({'href':href, 'text':text})
    repo=''
    for link in links:
        hm=re.search(r'https?://github\.com/([^/#?]+/[^/#?]+)', link['href'], re.I)
        if hm:
            repo=hm.group(1).rstrip('.git')
            # exclude issues/pulls/etc
            repo='/'.join(repo.split('/')[:2])
            break
    desc = ''
    mm = re.search(r'<meta name="description" content="([^"]*)"', html)
    if mm: desc = html_lib.unescape(mm.group(1))
    return {'published': title_date, 'downloads': downloads, 'external_links': links, 'github_repo': repo, 'description': desc}

def cohort_half(d):
    if not d: return ''
    y,m = int(d[:4]), int(d[5:7])
    return f"{y}H{1 if m<=6 else 2}"

def cohort_quarter(d):
    if not d: return ''
    y,m = int(d[:4]), int(d[5:7])
    return f"{y}Q{(m-1)//3+1}"

def age_days(d):
    if not d: return ''
    return (TODAY - date.fromisoformat(d)).days

def collect_blender():
    api_path=CACHE/'api_extensions.json'
    data_raw=json.loads(fetch_url('https://extensions.blender.org/api/v1/extensions/', api_path))['data']
    seen=set(); data=[]
    for it in data_raw:
        key=(it.get('type'), it.get('website') or it.get('id'))
        if key in seen: continue
        seen.add(key); data.append(it)
    # Fetch version-history pages for every extension; about pages are fetched later only
    # for top/recent samples because dates and per-version downloads are on versions/.
    futures=[]
    with ThreadPoolExecutor(max_workers=16) as ex:
        for item in data:
            url=item['website']
            slug=slug_from_url(url)
            t=item['type']
            versions_url=url.rstrip('/')+'/versions/'
            versions_path=PAGES/safe_name(t, slug, 'versions')
            futures.append(ex.submit(fetch_url, versions_url, versions_path, False, 18))
        done=0
        for f in as_completed(futures):
            try: f.result()
            except Exception as e: print(f'fetch failed: {e}', file=sys.stderr)
            done += 1
            if done % 300 == 0: print(f'fetched versions {done}/{len(futures)}', file=sys.stderr)
    rows=[]; version_rows=[]
    for item in data:
        slug=slug_from_url(item['website']); t=item['type']
        about_path=PAGES/safe_name(t, slug, 'about')
        versions_path=PAGES/safe_name(t, slug, 'versions')
        about_html=about_path.read_text(encoding='utf-8', errors='replace') if about_path.exists() else ''
        versions_html=versions_path.read_text(encoding='utf-8', errors='replace') if versions_path.exists() else ''
        about=parse_about(about_html)
        versions=parse_versions(versions_html)
        dates=[v['published'] for v in versions if v['published']]
        first=min(dates) if dates else about['published']
        latest=max(dates) if dates else about['published']
        total_version_downloads=sum(v['downloads'] for v in versions)
        current_downloads=about['downloads'] or (versions[0]['downloads'] if versions else 0)
        if total_version_downloads and total_version_downloads > current_downloads:
            current_downloads=total_version_downloads
        text=' '.join([item.get('name',''), item.get('tagline',''), about.get('description',''), ' '.join(item.get('tags') or []), about.get('github_repo','')]).lower()
        ai_flag=bool(re.search(r'\b(ai|llm|gpt|chatgpt|claude|openai|mcp|comfyui|stable diffusion|diffusion|generative|agent)\b', text))
        rows.append({
            'id':item.get('id',''), 'slug':slug, 'name':item.get('name',''), 'type':t,
            'first_listed':first, 'latest_version_date':latest, 'cohort_half':cohort_half(first), 'cohort_quarter':cohort_quarter(first),
            'age_days':age_days(first), 'downloads_current':current_downloads, 'versions_count':len(versions),
            'api_version':item.get('version',''), 'maintainer':item.get('maintainer',''), 'tags':'|'.join(item.get('tags') or []),
            'tagline':item.get('tagline',''), 'website':item.get('website',''), 'external_links':json.dumps(about['external_links'], ensure_ascii=False),
            'github_repo':about['github_repo'], 'ai_related_guess':int(ai_flag)
        })
        for v in versions:
            vv=dict(v); vv.update({'id':item.get('id',''), 'slug':slug, 'type':t, 'name':item.get('name','')})
            version_rows.append(vv)
    for filename, rws, fields in [
        ('extensions_current.csv', rows, ['id','slug','name','type','first_listed','latest_version_date','cohort_half','cohort_quarter','age_days','downloads_current','versions_count','api_version','maintainer','tags','tagline','website','github_repo','ai_related_guess','external_links']),
        ('versions_current.csv', version_rows, ['id','slug','type','name','version','published','downloads','status'])]:
        with (DATA/filename).open('w', newline='', encoding='utf-8') as f:
            w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rws)
    print(f'wrote {len(rows)} extensions, {len(version_rows)} versions')

def parse_queue_page(html):
    lines=[]
    for line in re.sub(r'<[^>]+>','\n',html).splitlines():
        ss=' '.join(html_lib.unescape(line).split())
        if ss: lines.append(ss)
    statuses=['Awaiting Review','Awaiting Changes','Approved','Declined']
    rows=[]; i=0
    while i < len(lines):
        if lines[i] in ['Add-on','Theme','Asset Library'] and i+5 < len(lines):
            typ=lines[i]; name=lines[i+1]; maint=lines[i+2]; sub=lines[i+3]; act=lines[i+4]
            j=i+5
            if j < len(lines) and re.fullmatch(r'\d+', lines[j]): j+=1
            status=lines[j] if j < len(lines) and lines[j] in statuses else ''
            if status:
                rows.append({'type':typ,'name':name,'maintainer':maint,'submitted_age':sub,'activity_age':act,'status':status})
                i=j+1; continue
        i+=1
    return rows

def age_to_hours(s):
    m=re.match(r'(\d+)\s*([hmwd])', s or '')
    if not m: return None
    val=int(m.group(1)); unit=m.group(2); return val*{'m':1/60,'h':1,'d':24,'w':168}[unit]

def collect_queue():
    first=fetch_url('https://extensions.blender.org/approval-queue/', CACHE/'approval_queue_page_1.html')
    max_page=1
    for m in re.finditer(r'href="\?page=(\d+)"', first):
        max_page=max(max_page,int(m.group(1)))
    pages={1:first}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs={ex.submit(fetch_url, f'https://extensions.blender.org/approval-queue/?page={i}', CACHE/f'approval_queue_page_{i}.html', False, 18):i for i in range(2,max_page+1)}
        for f in as_completed(futs):
            try: pages[futs[f]]=f.result()
            except Exception as e: print('queue page failed', futs[f], e, file=sys.stderr)
    allrows=[]
    for i in range(1,max_page+1):
        if i in pages: allrows.extend(parse_queue_page(pages[i]))
    statuses=['Awaiting Review','Awaiting Changes','Approved','Declined']
    counts={s:sum(1 for r in allrows if r['status']==s) for s in statuses}
    waits=[age_to_hours(r['submitted_age']) for r in allrows if r['status'] in ['Awaiting Review','Awaiting Changes']]
    waits=[w for w in waits if w is not None]
    waits_sorted=sorted(waits)
    with (DATA/'approval_queue_current.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['type','name','maintainer','submitted_age','activity_age','status']); w.writeheader(); w.writerows(allrows)
    summary={'rows':len(allrows),'pages':max_page,'status_counts':counts,
        'open_wait_hours_median': (waits_sorted[len(waits_sorted)//2] if waits_sorted else None),
        'open_wait_hours_p90': (waits_sorted[int(len(waits_sorted)*0.9)] if waits_sorted else None),
        'open_wait_days_median': (waits_sorted[len(waits_sorted)//2]/24 if waits_sorted else None),
        'open_wait_days_p90': (waits_sorted[int(len(waits_sorted)*0.9)]/24 if waits_sorted else None)}
    (DATA/'approval_queue_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f'queue rows {len(allrows)} counts {counts}')

def collect_github_topic_counts():
    # GitHub repos tagged blender-addon(s), creation counts per half-year since 2021. Current stars only.
    periods=[]
    for y in range(2021,2027):
        periods.append((f'{y}H1', f'{y}-01-01', f'{y}-06-30'))
        periods.append((f'{y}H2', f'{y}-07-01', f'{y}-12-31'))
    rows=[]; allrepos={}
    topics=['blender-addon','blender-addons']
    for label,start,end in periods:
        for topic in topics:
            q=f'topic:{topic} created:{start}..{end}'
            outpath=CACHE/'github'/f'search_{topic}_{label}.json'
            if outpath.exists():
                obj=json.loads(outpath.read_text())
            else:
                cmd=['gh','api','-X','GET','search/repositories','-f',f'q={q}','-f','per_page=100','--paginate','--slurp']
                cp=subprocess.run(cmd, text=True, capture_output=True, check=False)
                if cp.returncode != 0:
                    print('gh failed', q, cp.stderr[:300], file=sys.stderr); continue
                txt=cp.stdout.strip()
                parsed=json.loads(txt)
                if isinstance(parsed, list):
                    items=[]; total=0
                    for d in parsed:
                        total=max(total, d.get('total_count',0)); items.extend(d.get('items',[]))
                    obj={'total_count':total,'items':items}
                else:
                    obj=parsed
                outpath.write_text(json.dumps(obj), encoding='utf-8')
            for it in obj.get('items',[]):
                rid=it['id']; allrepos[rid]=it
    byhalf={label:{} for label,_,_ in periods}
    for it in allrepos.values():
        created=it['created_at'][:10]
        label=cohort_half(created)
        if label in byhalf: byhalf[label][it['id']]=it
    for label,_,_ in periods:
        repos=list(byhalf[label].values())
        if label > '2026H2': continue
        rows.append({'cohort_half':label,'repo_count':len(repos),'stars_ge_10':sum(1 for r in repos if r.get('stargazers_count',0)>=10),'stars_ge_100':sum(1 for r in repos if r.get('stargazers_count',0)>=100),'stars_total':sum(r.get('stargazers_count',0) for r in repos)})
    with (DATA/'github_topic_blender_addon_counts.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['cohort_half','repo_count','stars_ge_10','stars_ge_100','stars_total']); w.writeheader(); w.writerows(rows)
    top=sorted(allrepos.values(), key=lambda r:r.get('stargazers_count',0), reverse=True)[:100]
    with (DATA/'github_topic_top_repos.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['full_name','created_at','stargazers_count','html_url','description','topics']
        w=csv.DictWriter(f, fields); w.writeheader()
        for r in top:
            w.writerow({k: ('|'.join(r[k]) if k=='topics' else r.get(k,'')) for k in fields})
    print(f'github repos {len(allrepos)}')

if __name__ == '__main__':
    todo=set(sys.argv[1:] or ['blender','queue','github'])
    if 'blender' in todo: collect_blender()
    if 'queue' in todo: collect_queue()
    if 'github' in todo: collect_github_topic_counts()
