#!/usr/bin/env python3
from pathlib import Path
from urllib.request import Request, urlopen
import csv, re
OUT=Path('/Users/seangoedecke/Code/where-is-the-software/market-usage/chrome')
DATA=OUT/'data'; CACHE=OUT/'cache'
DATA.mkdir(parents=True, exist_ok=True); CACHE.mkdir(parents=True, exist_ok=True)
root_url='https://chromewebstore.google.com/sitemap'
root=urlopen(Request(root_url, headers={'User-Agent':'Mozilla/5.0 cohort research'}), timeout=45).read().decode('utf-8')
(CACHE/'cws_sitemap_index.xml').write_text(root)
shards=re.findall(r'<loc>(https://chromewebstore\.google\.com/sitemap\?shard=\d+)</loc>', root)
first=''
first_url_count=''
if shards:
    first=urlopen(Request(shards[0], headers={'User-Agent':'Mozilla/5.0 cohort research'}), timeout=60).read().decode('utf-8', errors='ignore')
    first_url_count=first.count('<url>')
with (DATA/'cws_sitemap_verification.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=['root_url','shard_count','first_shard_url','first_shard_url_count','lastmod_values'])
    w.writeheader(); w.writerow({'root_url':root_url,'shard_count':len(shards),'first_shard_url':shards[0] if shards else '', 'first_shard_url_count':first_url_count, 'lastmod_values':';'.join(sorted(set(re.findall(r'<lastmod>(.*?)</lastmod>', root))))})
print('shards', len(shards), 'first_shard_urls', first_url_count)
