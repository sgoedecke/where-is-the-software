#!/usr/bin/env python3
import urllib.request, re, csv
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import collect_blender as cb
OUT=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/blender')
CACHE=OUT/'cache'/'wayback'; DATA=OUT/'data'; CACHE.mkdir(exist_ok=True)
out=[]
for ts in ['20241015','20250115','20250415','20250715','20251015','20260115','20260415','20260715','20261015']:
    url='https://web.archive.org/web/'+ts+'id_/https://extensions.blender.org/approval-queue/'
    p=CACHE/f'approval_queue_{ts}.html'
    try:
        html=cb.fetch_url(url,p,False,35)
        m=re.search(r'(\d[\d,]*)\s+results', html)
        if not m: m=re.search(r'(\d[\d,]*)\s+Extensions', html)
        rows=cb.parse_queue_page(html) if hasattr(cb,'parse_queue_page') else []
        out.append({'target_date':ts,'parsed_results':m.group(1).replace(',','') if m else '', 'parsed_rows':len(rows), 'awaiting_review':sum(1 for r in rows if r['status']=='Awaiting Review'), 'awaiting_changes':sum(1 for r in rows if r['status']=='Awaiting Changes'), 'status':'ok', 'url':url})
    except Exception as e:
        out.append({'target_date':ts,'parsed_results':'','parsed_rows':'','awaiting_review':'','awaiting_changes':'','status':'error:'+str(e)[:100], 'url':url})
with (DATA/'wayback_queue_sample.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['target_date','parsed_results','parsed_rows','awaiting_review','awaiting_changes','status','url']); w.writeheader(); w.writerows(out)
print('wrote',len(out))
