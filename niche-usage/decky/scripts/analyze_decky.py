#!/usr/bin/env python3
import csv, gzip, json, pathlib, re, subprocess, difflib
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/decky')
CACHE = ROOT / 'cache'
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
NOW = datetime(2026, 10, 15, 7, 28, 48, tzinfo=timezone.utc)
THRESHOLDS = [5000, 20000, 100000]


def dt(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def cohort(t):
    return f'{t.year}-H{1 if t.month <= 6 else 2}'


def write_csv(path, rows, fields):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fields})

plugins = json.load(open(CACHE / 'plugins_downloads.json'))
plugins_by_id = {p['id']: p for p in plugins}

# Parse gitmodules and first-addition commits for current submodules.
mods_text = (CACHE / 'decky-plugin-database/.gitmodules').read_text()
mods = []
for block in re.split(r'\n(?=\[submodule)', mods_text):
    pm = re.search(r'path\s*=\s*([^\n]+)', block)
    um = re.search(r'url\s*=\s*([^\n]+)', block)
    if pm:
        mods.append({'path': pm.group(1).strip(), 'base': pm.group(1).strip().split('/')[-1], 'url': um.group(1).strip() if um else ''})

sub_rows = []
for m in mods:
    r = subprocess.run(
        ['git', '-C', str(CACHE / 'decky-plugin-database'), '--no-pager', 'log', '--reverse', '--format=%aI|%H|%s', '--diff-filter=A', '--', m['path']],
        text=True, capture_output=True
    )
    line = r.stdout.splitlines()[0] if r.stdout.splitlines() else ''
    if line:
        parts = line.split('|', 2)
        added_at, commit, subject = parts[0], parts[1], parts[2] if len(parts) > 2 else ''
    else:
        added_at = commit = subject = ''
    sub_rows.append({**m, 'git_added_at': added_at, 'git_added_cohort': cohort(dt(added_at)) if added_at else '', 'git_commit': commit, 'git_subject': subject})
write_csv(DATA / 'git_submodule_additions.csv', sub_rows, ['path', 'base', 'url', 'git_added_at', 'git_added_cohort', 'git_commit', 'git_subject'])

# Fuzzy/manual mapping for top recent repos.
def norm(s):
    s = s.lower().replace('steamdeck', 'deck').replace('steam-deck', 'deck')
    s = re.sub(r'^(sdh-|decky-|deck-)', '', s)
    s = re.sub(r'(-decky|-plugin|-plugins|-for-deck|deck)$', '', s)
    return re.sub(r'[^a-z0-9]+', '', s)

pathmap = {m['path']: m for m in mods}
manual = {
    'Decky-Framegen': 'plugins/Decky-Framegen', 'Decky LSFG-VK': 'plugins/decky-lsfg-vk',
    'PlayCount': 'plugins/playcount-decky', 'Deck Settings': 'plugins/decky-game-settings',
    'HueSync': 'plugins/HueSync', 'Picture in Picture': 'plugins/decky-pip',
    'Virtual Surround Sound': 'plugins/decky-virtual-surround-sound', 'LetMeReShade': 'plugins/LetMeReShade',
    'Music Control': 'plugins/MusicControl', 'Decky Sunshine': 'plugins/decky-sunshine',
    'DeckSP': 'plugins/DeckSP', 'Better Keyboard': 'plugins/BetterKeyboard',
    'Speed Test': 'plugins/decky-speed-test', 'WiFi Locker': 'plugins/decky-wifi-locker',
    'Decky-Lookup': 'plugins/Decky-Lookup', 'Decky Proton Launch': 'plugins/decky-proton-launch',
    'Non-Steam Badges': 'plugins/decky-nonsteam-badges', 'Simple Timer': 'plugins/simple-timer',
    'Deck Shelves': 'plugins/Deck-Shelves', 'Launch Options': 'plugins/decky-launch-options',
    'Dimmer Deck': 'plugins/DimmerDeck', 'Crosshair': 'plugins/Crosshair',
    'Decky Ludusavi': 'plugins/decky-ludusavi', 'MuraDeck': 'plugins/MuraDeck',
    'Decky Translator': 'plugins/decky-translator', 'Deck Progress Tracker': 'plugins/deck-progress-tracker',
    'Game Sync': 'plugins/SDH-GameSync', 'Network Sentinel': 'plugins/network-sentinel',
    'Steam Status': 'plugins/steamstatus-decky', 'Download All': 'plugins/decky-download-all'
}
mods_by = [(norm(m['base']), m) for m in mods]

def map_mod(name):
    if name in manual and manual[name] in pathmap:
        return pathmap[manual[name]]
    nx = norm(name)
    return max(mods_by, key=lambda nm: difflib.SequenceMatcher(None, nx, nm[0]).ratio())[1]

# Current plugin CSV.
plugin_rows = []
ai_pat = re.compile(r'\b(ai|llm|chatgpt|openai|claude|copilot|agent|translator|translate|ocr)\b', re.I)
for p in sorted(plugins, key=lambda x: x['created']):
    c = cohort(dt(p['created']))
    first_version = min(v.get('created', p['created']) for v in p.get('versions', [])) if p.get('versions') else p['created']
    plugin_rows.append({
        'id': p['id'], 'name': p['name'], 'author': p['author'], 'created': p['created'], 'cohort': c,
        'downloads': p['downloads'], 'updates': p.get('updates', ''), 'versions': len(p.get('versions', [])),
        'first_version_created': first_version, 'updated': p.get('updated', ''), 'tags': ';'.join(p.get('tags', [])),
        'description': p.get('description', '').replace('\n', ' '),
        'ai_flag': bool(ai_pat.search(' '.join([p['name'], p.get('description',''), ' '.join(p.get('tags', []))])))
    })
write_csv(DATA / 'plugins_current.csv', plugin_rows, ['id','name','author','created','cohort','downloads','updates','versions','first_version_created','updated','tags','ai_flag','description'])

# Wayback/current snapshots with download fields.
def load_snapshot(f):
    raw = open(f, 'rb').read()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    try:
        return json.loads(raw)
    except Exception:
        return None

snapshots = []
for f in sorted((CACHE / 'wayback_snapshots').glob('*.json')):
    m = re.match(r'(\d{14})_', f.name)
    if not m:
        continue
    data = load_snapshot(f)
    if isinstance(data, list) and data and isinstance(data[0], dict) and 'downloads' in data[0]:
        sdt = datetime.strptime(m.group(1), '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
        snapshots.append((sdt, {x['id']: x for x in data}))
snapshots.append((NOW, plugins_by_id))
snapshots.sort(key=lambda x: x[0])
write_csv(DATA / 'snapshot_inventory.csv', [{'snapshot_at': s[0].isoformat(), 'plugins': len(s[1]), 'has_downloads': True} for s in snapshots], ['snapshot_at','plugins','has_downloads'])

# Equal-age proxy: nearest snapshot at age >=120 days; choose nearest to 180 days.
equal_rows = []
for p in plugins:
    listed = dt(p['created'])
    candidates = []
    for sdt, data in snapshots:
        if p['id'] in data:
            age = (sdt - listed).days
            if age >= 120:
                candidates.append((abs(age - 180), age, sdt, data[p['id']].get('downloads')))
    if candidates:
        _, age, sdt, downloads = sorted(candidates, key=lambda x: (x[0], x[1]))[0]
        equal_rows.append({'id': p['id'], 'name': p['name'], 'cohort': cohort(listed), 'created': p['created'], 'snapshot_at': sdt.isoformat(), 'age_days': age, 'downloads_at_snapshot': downloads})
write_csv(DATA / 'equal_age_proxy.csv', equal_rows, ['id','name','cohort','created','snapshot_at','age_days','downloads_at_snapshot'])

# PR counts and backlog.
prs = json.load(open(CACHE / 'prs.json'))
def labels(p): return [l['name'] for l in p.get('labels', [])]
def is_add(p): return 'plugin-addition' in labels(p) and 'not-plugin' not in labels(p)
created_counts = Counter(cohort(dt(p['createdAt'])) for p in prs if is_add(p) and p.get('createdAt'))
merged_counts = Counter(cohort(dt(p['mergedAt'])) for p in prs if is_add(p) and p.get('mergedAt'))
open_add = [p for p in prs if is_add(p) and p['state'] == 'OPEN']
closed_unmerged_counts = Counter(cohort(dt(p['createdAt'])) for p in prs if is_add(p) and p['state'] == 'CLOSED' and not p.get('mergedAt'))
write_csv(DATA / 'open_plugin_addition_prs.csv', [
    {'number': p['number'], 'createdAt': p['createdAt'], 'title': p['title'], 'labels': ';'.join(labels(p)), 'url': p['url']} for p in sorted(open_add, key=lambda x: x['createdAt'])
], ['number','createdAt','title','labels','url'])

# Cohort summary.
by_cohort = defaultdict(list)
for p in plugins:
    by_cohort[cohort(dt(p['created']))].append(p)
equal_by = defaultdict(list)
for r in equal_rows:
    equal_by[r['cohort']].append(r)
all_cohorts = sorted(set(by_cohort) | set(created_counts) | set(merged_counts))
summary = []
for c in all_cohorts:
    arr = by_cohort.get(c, [])
    downloads = [p['downloads'] for p in arr]
    eq = equal_by.get(c, [])
    eqd = [int(r['downloads_at_snapshot'] or 0) for r in eq]
    ages = [int(r['age_days']) for r in eq]
    row = {
        'cohort': c,
        'current_store_plugins': len(arr),
        'current_ge_5k': sum(d >= 5000 for d in downloads),
        'current_ge_20k': sum(d >= 20000 for d in downloads),
        'current_ge_100k': sum(d >= 100000 for d in downloads),
        'current_median_downloads': int(sorted(downloads)[len(downloads)//2]) if downloads else '',
        'current_max_downloads': max(downloads) if downloads else '',
        'equal_age_n': len(eq),
        'equal_age_median_age_days': int(sorted(ages)[len(ages)//2]) if ages else '',
        'equal_age_ge_5k': sum(d >= 5000 for d in eqd),
        'equal_age_ge_20k': sum(d >= 20000 for d in eqd),
        'equal_age_ge_100k': sum(d >= 100000 for d in eqd),
        'plugin_addition_prs_created': created_counts.get(c, 0),
        'plugin_addition_prs_merged': merged_counts.get(c, 0),
        'closed_unmerged_addition_prs_created': closed_unmerged_counts.get(c, 0),
    }
    summary.append(row)
write_csv(DATA / 'cohort_summary.csv', summary, ['cohort','current_store_plugins','current_ge_5k','current_ge_20k','current_ge_100k','current_median_downloads','current_max_downloads','equal_age_n','equal_age_median_age_days','equal_age_ge_5k','equal_age_ge_20k','equal_age_ge_100k','plugin_addition_prs_created','plugin_addition_prs_merged','closed_unmerged_addition_prs_created'])

# Top recent table enriched with repo metadata from previous script.
repo_meta = json.load(open(CACHE / 'repo_metadata.json')) if (CACHE / 'repo_metadata.json').exists() else {}
def gh_repo(url):
    m = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', url)
    return f'{m.group(1)}/{m.group(2)}' if m else ''

top_recent = []
for p in sorted([x for x in plugins if x['created'] >= '2025-01-01'], key=lambda x: x['downloads'], reverse=True)[:30]:
    mod = map_mod(p['name'])
    repo = gh_repo(mod['url'])
    meta = repo_meta.get(repo, {}) if repo else {}
    top_recent.append({
        'rank': len(top_recent) + 1, 'name': p['name'], 'created': p['created'][:10], 'downloads': p['downloads'],
        'cohort': cohort(dt(p['created'])), 'ai_flag': bool(ai_pat.search(' '.join([p['name'], p.get('description',''), ' '.join(p.get('tags', []))]))),
        'github_repo': repo, 'repo_created_at': meta.get('created_at', ''), 'submodule_path': mod['path'],
        'description': p.get('description','').replace('\n',' ')[:160]
    })
write_csv(DATA / 'top_recent_plugins.csv', top_recent, ['rank','name','created','cohort','downloads','ai_flag','github_repo','repo_created_at','submodule_path','description'])

print('Wrote data files in', DATA)
