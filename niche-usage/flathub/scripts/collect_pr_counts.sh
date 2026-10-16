#!/usr/bin/env bash
set -euo pipefail
OUT=/Users/seangoedecke/Code/where-is-the-software/niche-usage/flathub/data/pr_counts_quarterly.csv
echo 'quarter,opened,closed,merged_search_count,still_open_created_in_quarter' > "$OUT"
python3 - <<'PY' | while IFS=, read -r q start end; do
import datetime as dt
start=dt.date(2021,1,1); end=dt.date(2026,10,15)
y=start.year
while y<=end.year:
  for qi,(m1,m2) in enumerate([(1,3),(4,6),(7,9),(10,12)],1):
    s=dt.date(y,m1,1)
    e=(dt.date(y+1,1,1)-dt.timedelta(days=1)) if m2==12 else (dt.date(y,m2+1,1)-dt.timedelta(days=1))
    if e < start or s > end: continue
    if e > end: e=end
    print(f'{y}-Q{qi},{s},{e}')
  y+=1
PY
  opened_q="repo:flathub/flathub is:pr base:new-pr created:${start}..${end}"
  closed_q="repo:flathub/flathub is:pr base:new-pr closed:${start}..${end}"
  merged_q="repo:flathub/flathub is:pr base:new-pr merged:${start}..${end}"
  open_created_q="repo:flathub/flathub is:pr base:new-pr is:open created:${start}..${end}"
  query='query($q:String!){ search(query:$q, type:ISSUE, first:1){ issueCount } }'
  opened=$(gh api graphql -f query="$query" -f q="$opened_q" --jq '.data.search.issueCount')
  closed=$(gh api graphql -f query="$query" -f q="$closed_q" --jq '.data.search.issueCount')
  merged=$(gh api graphql -f query="$query" -f q="$merged_q" --jq '.data.search.issueCount')
  still=$(gh api graphql -f query="$query" -f q="$open_created_q" --jq '.data.search.issueCount')
  echo "$q,$opened,$closed,$merged,$still" | tee -a "$OUT" >&2
done
