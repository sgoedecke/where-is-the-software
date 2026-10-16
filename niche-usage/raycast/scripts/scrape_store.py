import concurrent.futures, csv, json, os, re, time, urllib.request
from pathlib import Path
BASE=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/raycast')
CACHE=BASE/'cache'/'store_pages'
DATA=BASE/'data'
CACHE.mkdir(parents=True, exist_ok=True); DATA.mkdir(parents=True, exist_ok=True)
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 RaycastCohortStudy/1.0'

def fetch_page(n):
    path=CACHE/f'page_{n}.html'
    if path.exists() and path.stat().st_size>10000:
        return n, path.stat().st_size, 'cached'
    url='https://www.raycast.com/store' if n==1 else f'https://www.raycast.com/store/{n}'
    req=urllib.request.Request(url, headers={'User-Agent':UA})
    last=None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data=r.read()
            path.write_bytes(data)
            time.sleep(0.03)
            return n, len(data), 'fetched'
        except Exception as e:
            last=e; time.sleep(1.5*(attempt+1))
    return n, 0, f'ERR {last}'

def find_total_pages(text):
    nums=[int(x) for x in re.findall(r'href="/store/(\d+)#list"', text)]
    return max(nums) if nums else 1

# fetch first and determine count
n, size, status=fetch_page(1)
first=(CACHE/'page_1.html').read_text(errors='replace')
total=find_total_pages(first)
print('total_pages', total, 'first', size, status, flush=True)
# fetch rest
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs=[ex.submit(fetch_page, n) for n in range(2,total+1)]
    done=0
    for fut in concurrent.futures.as_completed(futs):
        done+=1
        n,size,status=fut.result()
        if done%25==0 or status.startswith('ERR'):
            print('progress', done, 'page', n, size, status, flush=True)

def raw_object_end(s,start):
    depth=0; in_str=False; i=start; n=len(s)
    while i<n:
        if s.startswith('\\"', i):
            # Treat escaped quotes in Next flight payload as JSON string delimiters.
            # A delimiter preceded by an extra backslash inside a JSON string is rare and not material here.
            in_str = not in_str
            i += 2
            continue
        if not in_str:
            c=s[i]
            if c=='{': depth += 1
            elif c=='}':
                depth -= 1
                if depth==0: return i+1
        i += 1
    return -1

def iter_extensions(text):
    needle='{\\"extension\\"'
    pos=0
    while True:
        idx=text.find(needle,pos)
        if idx<0: break
        end=raw_object_end(text,idx)
        pos=idx+len(needle)
        if end<0: continue
        raw=text[idx:end]
        try:
            decoded=json.loads('"'+raw+'"')
            obj=json.loads(decoded)
            ext=obj.get('extension')
            if isinstance(ext,dict) and 'download_count' in ext and ext.get('relative_path'):
                yield ext
        except Exception:
            continue

by_rel={}
for path in sorted(CACHE.glob('page_*.html')):
    text=path.read_text(errors='replace')
    for ext in iter_extensions(text):
        rel=ext.get('relative_path')
        if rel not in by_rel or ext.get('download_count',0)>by_rel[rel].get('download_count',0):
            by_rel[rel]=ext
print('extensions', len(by_rel), flush=True)
# flatten fields for CSV; full JSON saved too
rows=[]
for ext in by_rel.values():
    owner=ext.get('owner') or {}
    author=ext.get('author') or {}
    rows.append({
        'id':ext.get('id'), 'slug':ext.get('name'), 'title':ext.get('title'),
        'relative_path':ext.get('relative_path'), 'store_url':ext.get('store_url'),
        'download_count':ext.get('download_count'), 'is_new':ext.get('is_new'),
        'created_at':ext.get('created_at'), 'updated_at':ext.get('updated_at'),
        'owner_name':owner.get('name'), 'owner_handle':owner.get('handle') or owner.get('username'),
        'author_name':author.get('name'), 'author_handle':author.get('handle') or author.get('username'),
        'categories':'|'.join(ext.get('categories') or []),
        'platforms':'|'.join(ext.get('platforms') or []),
        'description':(ext.get('description') or '').replace('\n',' '),
        'prompt_examples':'|'.join(ext.get('prompt_examples') or []),
        'skills_count':len(ext.get('skills') or []), 'provides_models':ext.get('provides_models'),
        'has_mcp':ext.get('has_mcp'), 'source_url':ext.get('source_url'),
    })
rows.sort(key=lambda r: r['relative_path'])
with open(DATA/'store_extensions_current.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(DATA/'store_extensions_current.json','w') as f:
    json.dump(list(by_rel.values()), f, indent=2)
print('wrote', DATA/'store_extensions_current.csv')
