"""Obsidian plugins: downloads at ~60 days after first appearing in community-plugin-stats.json.
Weekly snapshots from git history of obsidianmd/obsidian-releases."""
import json, subprocess, datetime as dt, collections, csv, os
REPO = os.path.join(os.path.dirname(__file__), '..', 'obsidian-releases')
OUT = os.path.join(os.path.dirname(__file__), '..', 'results')
def git(*a): return subprocess.check_output(['git', '-C', REPO, *a], text=True)
log = git('log', '--format=%H %cs', '--', 'community-plugin-stats.json').split('\n')
by_week = {}
for line in reversed([l for l in log if l]):
    h, d = line.split(); d = dt.date.fromisoformat(d)
    wk = d - dt.timedelta(days=d.weekday())
    by_week[wk] = (h, d)  # last commit in week
snaps = []
for wk in sorted(by_week):
    h, d = by_week[wk]
    data = json.loads(git('show', f'{h}:community-plugin-stats.json'))
    snaps.append((d, {k: (v.get('downloads') or 0) for k, v in data.items()}))
first = {}
for d, vals in snaps:
    for k in vals:
        first.setdefault(k, (d, vals[k]))
start = snaps[0][0]
rows = []
for k, (d0, dl0) in first.items():
    if d0 <= start + dt.timedelta(days=7):
        continue  # present in first snapshot: unknown add date
    target = d0 + dt.timedelta(days=60)
    s = next(((d, v) for d, v in snaps if d >= target), None)
    if not s or (s[0] - target).days > 10:
        continue
    rows.append((k, d0.isoformat(), dl0, s[1].get(k, 0)))
with open(os.path.join(OUT, 'plugin_60d_downloads.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'first_seen_stats', 'downloads_at_first_seen', 'downloads_60d']); w.writerows(rows)
c = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for k, d0, dl0, dl in rows:
    y, m = int(d0[:4]), int(d0[5:7]); key = f'{y}Q{(m-1)//3+1}'
    c[key][0] += 1
    for i, t in enumerate([100, 1000, 10000, 50000]):
        if dl >= t: c[key][i+1] += 1
with open(os.path.join(OUT, 'cohort_60d_quarterly.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['quarter', 'n', 'ge100', 'ge1k', 'ge10k', 'ge50k'])
    for k in sorted(c): w.writerow([k, *c[k]]); print(k, *c[k])
