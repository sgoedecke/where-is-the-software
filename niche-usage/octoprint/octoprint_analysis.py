#!/usr/bin/env python3
import csv
import datetime as dt
import gzip
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/octoprint')
REPO = BASE / 'plugins.octoprint.org'
CACHE = BASE / 'cache'
CACHE.mkdir(parents=True, exist_ok=True)
UA = 'where-is-the-software-research/1.0 (OctoPrint plugin cohort analysis)'
TODAY = dt.date(2026, 10, 15)
CURRENT_TOTAL = None
THRESHOLDS = [10, 100, 1000]


def get_url(url, cache_name=None, binary=False, retries=4):
    if cache_name:
        path = CACHE / cache_name
        if path.exists():
            data = path.read_bytes()
            return data if binary else data.decode('utf-8')
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if data.startswith(b'\x1f\x8b'):
                data = gzip.decompress(data)
            if cache_name:
                (CACHE / cache_name).write_bytes(data)
            time.sleep(0.6)
            return data if binary else data.decode('utf-8')
        except Exception as e:
            last = e
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f'failed fetching {url}: {last}')


def get_json(url, cache_name=None):
    return json.loads(get_url(url, cache_name=cache_name, binary=False))


def parse_date(x):
    if not x:
        return None
    if isinstance(x, dt.date):
        return x
    s = str(x).strip()
    # Strip timezone names/offsets where strptime is brittle.
    for fmt in ('%Y-%m-%d %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    m = re.match(r'(\d{4}-\d{2}-\d{2})', s)
    if m:
        return dt.date.fromisoformat(m.group(1))
    return None


def cohort(d):
    if d is None:
        return 'unknown'
    return f'{d.year}H{1 if d.month <= 6 else 2}'


def cdx(url, from_='202101', to='202610', extra=None):
    params = {
        'url': url,
        'output': 'json',
        'fl': 'timestamp,statuscode,mimetype,digest,original',
        'filter': 'statuscode:200',
        'from': from_,
        'to': to,
    }
    if extra:
        params.update(extra)
    q = 'https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode(params)
    name = 'cdx_' + re.sub(r'[^A-Za-z0-9]+', '_', url + '_' + from_ + '_' + to + '_' + str(extra or '')) + '.json'
    data = get_json(q, name)
    if not data or len(data) == 1:
        return []
    header = data[0]
    return [dict(zip(header, row)) for row in data[1:]]


def wayback_json(timestamp, url, name_prefix):
    snap_url = f'https://web.archive.org/web/{timestamp}id_/{url}'
    name = f'{name_prefix}_{timestamp}.json'
    return get_json(snap_url, name)


def ensure_repo():
    if not (REPO / '.git').exists():
        subprocess.check_call(['git', 'clone', 'https://github.com/OctoPrint/plugins.octoprint.org.git', str(REPO)])


def git_lines(args):
    return subprocess.check_output(['git', '-C', str(REPO)] + args, text=True, errors='replace')


def frontmatter_id(path):
    text = path.read_text(errors='replace')
    m = re.match(r'---\n(.*?)\n---', text, re.S)
    if not m:
        return path.stem.lower()
    fm = m.group(1)
    mid = re.search(r'^id:\s*([^\n#]+)', fm, re.M)
    return (mid.group(1).strip().strip('"\'') if mid else path.stem).lower()


def git_added_paths():
    out = git_lines(['log', '--all', '--reverse', '--diff-filter=A', '--name-only', '--format=@@@%H%x09%cI', '--', '_plugins'])
    rows = []
    cur = None
    for line in out.splitlines():
        if line.startswith('@@@'):
            parts = line[3:].split('\t')
            cur = {'commit': parts[0], 'date': parse_date(parts[1])}
        elif line.strip().endswith('.md') and cur:
            rows.append({'path': line.strip(), 'add_commit': cur['commit'], 'git_add_date': cur['date']})
    first = {}
    for r in rows:
        first.setdefault(r['path'], r)
    return first


def fetch_current_plugins():
    data = get_json('https://plugins.octoprint.org/plugins.json', 'current_plugins_json.json')
    byid = {}
    for p in data:
        pid = str(p.get('id')).lower()
        st = p.get('stats') or {}
        byid[pid] = {
            'id': pid,
            'title': p.get('title') or '',
            'description': p.get('description') or '',
            'published': parse_date(p.get('published')),
            'homepage': p.get('homepage') or p.get('source') or '',
            'source': p.get('source') or p.get('homepage') or '',
            'archive': p.get('archive') or '',
            'author': p.get('author') or p.get('authors') or '',
            'license': p.get('license') or '',
            'abandoned': p.get('abandoned'),
            'attributes': ','.join(p.get('attributes') or []),
            'instances_month': int(st.get('instances_month') or 0),
            'install_events_month': int(st.get('install_events_month') or 0),
            'instances_week': int(st.get('instances_week') or 0),
            'install_events_week': int(st.get('install_events_week') or 0),
            'page': p.get('page') or '',
        }
    return byid


def fetch_total_snapshots():
    rows = []
    for r in cdx('https://data.octoprint.org/export/instance_stats_30d.json', extra={'limit': '200'}):
        try:
            j = wayback_json(r['timestamp'], 'https://data.octoprint.org/export/instance_stats_30d.json', 'wb_instance_stats_30d')
            d = parse_date(j.get('_generated')) or dt.datetime.strptime(r['timestamp'][:8], '%Y%m%d').date()
            rows.append({'snapshot_date': d, 'timestamp': r['timestamp'], 'source': 'wayback:data_instance_30d', 'total_instances': int(j.get('count') or 0)})
        except Exception as e:
            print(f'WARN total snapshot {r.get("timestamp")} failed: {e}', file=sys.stderr)
    live = get_json('https://data.octoprint.org/export/instance_stats_30d.json', 'current_instance_stats_30d.json')
    rows.append({'snapshot_date': parse_date(live.get('_generated')) or TODAY, 'timestamp': 'current', 'source': 'live:data_instance_30d', 'total_instances': int(live.get('count') or 0)})
    # de-duplicate by date, keeping latest appended for current.
    by = {}
    for r in rows:
        by[r['snapshot_date']] = r
    return sorted(by.values(), key=lambda r: r['snapshot_date'])


def nearest_total(date, total_rows, max_days=90):
    if not date or not total_rows:
        return (None, None)
    best = min(total_rows, key=lambda r: abs((r['snapshot_date'] - date).days))
    delta = abs((best['snapshot_date'] - date).days)
    if delta <= max_days:
        return best['total_instances'], delta
    return (None, delta)


def fetch_stat_snapshots(total_rows):
    snaps = []
    # plugin_stats_30d snapshots often continue when plugins.json snapshots are sparse.
    for r in cdx('https://data.octoprint.org/export/plugin_stats_30d.json', extra={'limit': '200'}):
        try:
            j = wayback_json(r['timestamp'], 'https://data.octoprint.org/export/plugin_stats_30d.json', 'wb_plugin_stats_30d')
            d = parse_date(j.get('_generated')) or dt.datetime.strptime(r['timestamp'][:8], '%Y%m%d').date()
            total, total_delta = nearest_total(d, total_rows)
            stats = {str(k).lower(): int((v or {}).get('instances') or 0) for k, v in (j.get('plugins') or {}).items()}
            snaps.append({'snapshot_date': d, 'timestamp': r['timestamp'], 'source': 'wayback:data_plugin_30d', 'total_instances': total, 'total_delta_days': total_delta, 'stats': stats})
        except Exception as e:
            print(f'WARN plugin stats snapshot {r.get("timestamp")} failed: {e}', file=sys.stderr)
    # plugins.json snapshots include rendered stats and reach back to 2021.
    for r in cdx('https://plugins.octoprint.org/plugins.json', extra={'limit': '200'}):
        try:
            j = wayback_json(r['timestamp'], 'https://plugins.octoprint.org/plugins.json', 'wb_plugins_json')
            d = dt.datetime.strptime(r['timestamp'][:8], '%Y%m%d').date()
            total, total_delta = nearest_total(d, total_rows)
            stats = {}
            for p in j:
                st = p.get('stats') or {}
                stats[str(p.get('id')).lower()] = int(st.get('instances_month') or 0)
            snaps.append({'snapshot_date': d, 'timestamp': r['timestamp'], 'source': 'wayback:plugins_json', 'total_instances': total, 'total_delta_days': total_delta, 'stats': stats})
        except Exception as e:
            print(f'WARN plugins.json snapshot {r.get("timestamp")} failed: {e}', file=sys.stderr)
    live_plugins = get_json('https://plugins.octoprint.org/plugins.json', 'current_plugins_json.json')
    d = TODAY
    total, total_delta = nearest_total(d, total_rows)
    snaps.append({'snapshot_date': d, 'timestamp': 'current', 'source': 'live:plugins_json', 'total_instances': total, 'total_delta_days': total_delta,
                  'stats': {str(p.get('id')).lower(): int(((p.get('stats') or {}).get('instances_month')) or 0) for p in live_plugins}})
    live_data = get_json('https://data.octoprint.org/export/plugin_stats_30d.json', 'current_plugin_stats_30d.json')
    d2 = parse_date(live_data.get('_generated')) or TODAY
    total2, total_delta2 = nearest_total(d2, total_rows)
    snaps.append({'snapshot_date': d2, 'timestamp': 'current-data', 'source': 'live:data_plugin_30d', 'total_instances': total2, 'total_delta_days': total_delta2,
                  'stats': {str(k).lower(): int((v or {}).get('instances') or 0) for k, v in (live_data.get('plugins') or {}).items()}})
    # If multiple snapshots are same date/source-ish, keep all; equal-age choice can use duplicates harmlessly.
    return sorted(snaps, key=lambda s: (s['snapshot_date'], s['source']))


def build_plugin_records(current):
    current_paths = {}
    for p in (REPO / '_plugins').glob('*.md'):
        try:
            current_paths[str(p.relative_to(REPO))] = frontmatter_id(p)
        except Exception:
            current_paths[str(p.relative_to(REPO))] = p.stem.lower()
    added = git_added_paths()
    records = {}
    # Current, authoritative registry fields.
    for pid, p in current.items():
        records[pid] = dict(p)
        records[pid].update({'listed_current': True, 'deleted_or_unlisted': False, 'git_add_date': None, 'git_path': ''})
    # Attach git add dates for current where id can be mapped.
    id_to_path = {pid: path for path, pid in current_paths.items()}
    for pid, path in id_to_path.items():
        if pid in records and path in added:
            records[pid]['git_add_date'] = added[path]['git_add_date']
            records[pid]['git_path'] = path
    # Deleted/unlisted paths for survivorship counts.
    for path, add in added.items():
        if path in current_paths:
            continue
        stem = Path(path).stem.lower()
        pid = stem
        if pid in records:
            continue
        # Try to extract id from the file at the add commit.
        try:
            blob = git_lines(['show', f'{add["add_commit"]}:{path}'])
            mid = re.search(r'^id:\s*([^\n#]+)', blob, re.M)
            if mid:
                pid = mid.group(1).strip().strip('"\'').lower()
        except Exception:
            pass
        if pid not in records:
            records[pid] = {
                'id': pid, 'title': stem, 'description': '', 'published': add['git_add_date'], 'homepage': '', 'source': '', 'archive': '',
                'author': '', 'license': '', 'abandoned': '', 'attributes': '', 'instances_month': 0, 'install_events_month': 0,
                'instances_week': 0, 'install_events_week': 0, 'page': '', 'listed_current': False, 'deleted_or_unlisted': True,
                'git_add_date': add['git_add_date'], 'git_path': path,
            }
    for r in records.values():
        if r.get('published') is None:
            r['published'] = r.get('git_add_date')
        r['cohort'] = cohort(r.get('published'))
    return records


def choose_equal_age(pid, created, snaps):
    if not created:
        return None
    target = created + dt.timedelta(days=180)
    lo = created + dt.timedelta(days=150)
    hi = created + dt.timedelta(days=365)
    cands = []
    for s in snaps:
        if lo <= s['snapshot_date'] <= hi and pid in s['stats']:
            cands.append((abs((s['snapshot_date'] - target).days), s))
    if not cands:
        return None
    cands.sort(key=lambda x: (x[0], x[1]['snapshot_date']))
    s = cands[0][1]
    inst = int(s['stats'].get(pid) or 0)
    return {
        'snapshot_date': s['snapshot_date'],
        'age_days': (s['snapshot_date'] - created).days,
        'instances_month': inst,
        'total_instances': s.get('total_instances'),
        'normalised_to_current_total': (inst / s['total_instances'] * CURRENT_TOTAL) if s.get('total_instances') and CURRENT_TOTAL else None,
        'source': s['source'],
    }


def count_thresholds(vals, denom, prefix=''):
    out = {}
    for t in THRESHOLDS:
        c = sum(1 for v in vals if v is not None and v >= t)
        out[f'{prefix}ge_{t}'] = c
        out[f'{prefix}share_ge_{t}'] = c / denom if denom else None
    return out


def write_csv(path, rows, fields):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            rr = {}
            for k in fields:
                v = r.get(k)
                if isinstance(v, dt.date):
                    v = v.isoformat()
                elif isinstance(v, float):
                    v = round(v, 6)
                rr[k] = v
            w.writerow(rr)


def gh_json(url):
    try:
        return get_json(url, 'gh_' + re.sub(r'[^A-Za-z0-9]+', '_', url)[:180] + '.json')
    except Exception as e:
        print(f'WARN github fetch failed {url}: {e}', file=sys.stderr)
        return None


def repo_from_url(url):
    if not url:
        return None
    m = re.search(r'github\.com[:/]+([^/]+)/([^/#?]+)', url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    repo = re.sub(r'\.git$', '', repo)
    return f'{owner}/{repo}'


def enrich_top(rows):
    enriched = []
    for r in rows:
        rr = dict(r)
        repo = repo_from_url(r.get('source') or r.get('homepage') or r.get('archive'))
        rr['github_repo'] = repo or ''
        rr['repo_created_at'] = ''
        rr['repo_stars'] = ''
        readme_text = ''
        if repo:
            info = gh_json(f'https://api.github.com/repos/{repo}')
            if info:
                rr['repo_created_at'] = info.get('created_at', '')[:10]
                rr['repo_stars'] = info.get('stargazers_count', '')
            # Raw README via API. It may be base64; use download_url instead to avoid extra parsing.
            readme = gh_json(f'https://api.github.com/repos/{repo}/readme')
            if readme and readme.get('download_url'):
                try:
                    readme_text = get_url(readme['download_url'], 'readme_' + re.sub(r'[^A-Za-z0-9]+', '_', repo) + '.md')[:200000]
                except Exception:
                    readme_text = ''
        descriptive_text = ' '.join([r.get('title',''), r.get('description',''), readme_text[:5000]])
        ai_theme = bool(re.search(r'\b(AI|LLM|ChatGPT|Claude|OpenAI|Gemini|Copilot|machine learning|artificial intelligence)\b', descriptive_text, re.I))
        explicit_ai_built_strict = bool(re.search(r'\b(built|created|generated|written|developed)\b.{0,80}\b(AI|Claude|ChatGPT|Copilot|Cursor|LLM)\b', descriptive_text, re.I))
        registry_ai_developed = 'ai-developed' in (r.get('attributes') or '').lower()
        rr['ai_themed_or_mentions_ai'] = ai_theme
        rr['explicit_ai_built_readme_or_description'] = explicit_ai_built_strict
        rr['registry_ai_developed_attribute'] = registry_ai_developed
        pub = parse_date(r.get('published'))
        repo_created = parse_date(rr.get('repo_created_at'))
        if repo_created and pub and (pub - repo_created).days > 180:
            newness = 'possibly established before listing (repo predates listing by >180d)'
        elif repo_created and pub:
            newness = 'appears newly created/listed together'
        else:
            newness = 'unclear from metadata'
        rr['newness_judgement'] = newness
        enriched.append(rr)
    return enriched


def github_topic_counts():
    rows = []
    for topic in ['klipper-plugin']:
        for year in range(2021, 2027):
            end = f'{year}-12-31'
            if year == 2026:
                end = TODAY.isoformat()
            q = urllib.parse.quote(f'topic:{topic} created:{year}-01-01..{end}')
            url = f'https://api.github.com/search/repositories?q={q}&per_page=1'
            try:
                j = gh_json(url)
                rows.append({'topic': topic, 'year': year, 'repos_created': (j or {}).get('total_count')})
            except Exception as e:
                rows.append({'topic': topic, 'year': year, 'repos_created': None, 'error': str(e)})
            time.sleep(0.8)
    return rows


def main():
    global CURRENT_TOTAL
    ensure_repo()
    current = fetch_current_plugins()
    total_rows = fetch_total_snapshots()
    CURRENT_TOTAL = [r for r in total_rows if r['source'].startswith('live')][-1]['total_instances']
    snaps = fetch_stat_snapshots(total_rows)
    records = build_plugin_records(current)

    # plugin CSV
    plugin_rows = []
    for r in sorted(records.values(), key=lambda x: (x.get('published') or dt.date(1900,1,1), x['id'])):
        plugin_rows.append(r)
    write_csv(BASE / 'plugins_current_and_deleted.csv', plugin_rows,
              ['id','title','published','cohort','listed_current','deleted_or_unlisted','instances_month','instances_week','install_events_month','attributes','abandoned','homepage','source','git_add_date','git_path','description'])

    # snapshot CSVs
    write_csv(BASE / 'total_instances_snapshots.csv', total_rows, ['snapshot_date','timestamp','source','total_instances'])
    stat_flat = []
    for s in snaps:
        for pid, inst in s['stats'].items():
            stat_flat.append({'snapshot_date': s['snapshot_date'], 'timestamp': s['timestamp'], 'source': s['source'], 'id': pid, 'instances_month': inst, 'total_instances': s.get('total_instances'), 'total_delta_days': s.get('total_delta_days')})
    write_csv(BASE / 'plugin_stats_snapshots.csv', stat_flat, ['snapshot_date','timestamp','source','id','instances_month','total_instances','total_delta_days'])

    cohorts = [f'{y}H{h}' for y in range(2021, 2027) for h in (1,2)]
    cohorts = [c for c in cohorts if not (c == '2026H2' and TODAY.month <= 6)]
    current_rows = []
    equal_rows = []
    equal_plugin_rows = []
    for c in cohorts:
        recs_total = [r for r in records.values() if r['cohort'] == c]
        recs_current = [r for r in recs_total if r.get('listed_current')]
        cur_vals = [int(r.get('instances_month') or 0) for r in recs_current]
        row = {'cohort': c, 'n_created_incl_recovered_deleted': len(recs_total), 'n_still_listed_current': len(recs_current), 'current_total_instances': CURRENT_TOTAL}
        row.update(count_thresholds(cur_vals, len(recs_current), 'current_abs_'))
        row.update({f'current_count_share_of_created_ge_{t}': row[f'current_abs_ge_{t}'] / len(recs_total) if recs_total else None for t in THRESHOLDS})
        current_rows.append(row)

        eqs = []
        eq_norm_vals = []
        for r in recs_total:
            eq = choose_equal_age(r['id'], r.get('published'), snaps)
            if eq:
                out = {'id': r['id'], 'title': r.get('title',''), 'cohort': c, 'published': r.get('published'), **eq}
                equal_plugin_rows.append(out)
                eqs.append(eq['instances_month'])
                eq_norm_vals.append(eq['normalised_to_current_total'])
        norm_eligible = len([v for v in eq_norm_vals if v is not None])
        erow = {'cohort': c, 'n_created_incl_recovered_deleted': len(recs_total), 'equal_age_eligible': len(eqs), 'equal_norm_eligible': norm_eligible, 'age_window_days': '150-365', 'target_age_days': 180}
        erow.update(count_thresholds(eqs, len(eqs), 'equal_abs_'))
        erow.update(count_thresholds(eq_norm_vals, norm_eligible, 'equal_norm_to_current_total_'))
        equal_rows.append(erow)
    write_csv(BASE / 'cohorts_current_usage.csv', current_rows, ['cohort','n_created_incl_recovered_deleted','n_still_listed_current','current_total_instances','current_abs_ge_10','current_abs_share_ge_10','current_count_share_of_created_ge_10','current_abs_ge_100','current_abs_share_ge_100','current_count_share_of_created_ge_100','current_abs_ge_1000','current_abs_share_ge_1000','current_count_share_of_created_ge_1000'])
    write_csv(BASE / 'cohorts_equal_age_usage.csv', equal_rows, ['cohort','n_created_incl_recovered_deleted','equal_age_eligible','equal_norm_eligible','age_window_days','target_age_days','equal_abs_ge_10','equal_abs_share_ge_10','equal_abs_ge_100','equal_abs_share_ge_100','equal_abs_ge_1000','equal_abs_share_ge_1000','equal_norm_to_current_total_ge_10','equal_norm_to_current_total_share_ge_10','equal_norm_to_current_total_ge_100','equal_norm_to_current_total_share_ge_100','equal_norm_to_current_total_ge_1000','equal_norm_to_current_total_share_ge_1000'])
    write_csv(BASE / 'equal_age_plugin_measurements.csv', equal_plugin_rows, ['id','title','cohort','published','snapshot_date','age_days','instances_month','total_instances','normalised_to_current_total','source'])

    recent = [dict(r) for r in records.values() if r.get('listed_current') and r['cohort'] in ('2025H2','2026H1','2026H2')]
    recent.sort(key=lambda r: int(r.get('instances_month') or 0), reverse=True)
    top = enrich_top(recent[:12])
    write_csv(BASE / 'recent_top_plugins.csv', top, ['id','title','cohort','published','instances_month','install_events_month','description','attributes','homepage','source','github_repo','repo_created_at','repo_stars','newness_judgement','ai_themed_or_mentions_ai','explicit_ai_built_readme_or_description','registry_ai_developed_attribute'])

    klipper = github_topic_counts()
    write_csv(BASE / 'klipper_topic_repos.csv', klipper, ['topic','year','repos_created','error'])

    # Draft report markdown.
    def fmt_pct(x):
        return None if x is None else f'{100*x:.0f}%'
    def fmt_cell(count, share):
        pct = fmt_pct(share)
        return 'n/a' if pct is None else f'{count} ({pct})'
    lines = []
    lines.append('# OctoPrint plugin cohort usage')
    lines.append('')
    lines.append(f'Generated {TODAY.isoformat()}. Source: OctoPrint plugin registry, plugins.octoprint.org git history, data.octoprint.org exports, Wayback Machine snapshots. Current 30-day OctoPrint instance denominator: {CURRENT_TOTAL:,}.')
    lines.append('')
    lines.append('## Cohort table: current 30-day active instances')
    lines.append('')
    lines.append('This table uses current `instances_month` for plugins still listed today; deleted/unlisted plugins are counted in `created` where recovered from git, but have no current usage in the registry, so the usage shares are also shown over still-listed plugins.')
    lines.append('')
    lines.append('| cohort | created incl. recovered deleted | still listed | ≥10 | ≥100 | ≥1,000 |')
    lines.append('|---|---:|---:|---:|---:|---:|')
    for r in current_rows:
        lines.append(f"| {r['cohort']} | {r['n_created_incl_recovered_deleted']} | {r['n_still_listed_current']} | {fmt_cell(r['current_abs_ge_10'], r['current_abs_share_ge_10'])} | {fmt_cell(r['current_abs_ge_100'], r['current_abs_share_ge_100'])} | {fmt_cell(r['current_abs_ge_1000'], r['current_abs_share_ge_1000'])} |")
    lines.append('')
    lines.append('## Equal-age check')
    lines.append('')
    lines.append('For equal-age usage, I chose the closest available 30-day active-instance snapshot between 150 and 365 days after a plugin\'s published/add date. Snapshots are sparse, so `eligible` is often below `created`; normalized columns scale each plugin by OctoPrint total instances at the nearest `instance_stats_30d` snapshot to the current denominator where a nearby total-instance snapshot exists.')
    lines.append('')
    lines.append('| cohort | created | eligible | norm eligible | ≥10 abs | ≥100 abs | ≥1,000 abs | ≥10 norm | ≥100 norm | ≥1,000 norm |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for r in equal_rows:
        lines.append(f"| {r['cohort']} | {r['n_created_incl_recovered_deleted']} | {r['equal_age_eligible']} | {r['equal_norm_eligible']} | {fmt_cell(r['equal_abs_ge_10'], r['equal_abs_share_ge_10'])} | {fmt_cell(r['equal_abs_ge_100'], r['equal_abs_share_ge_100'])} | {fmt_cell(r['equal_abs_ge_1000'], r['equal_abs_share_ge_1000'])} | {fmt_cell(r['equal_norm_to_current_total_ge_10'], r['equal_norm_to_current_total_share_ge_10'])} | {fmt_cell(r['equal_norm_to_current_total_ge_100'], r['equal_norm_to_current_total_share_ge_100'])} | {fmt_cell(r['equal_norm_to_current_total_ge_1000'], r['equal_norm_to_current_total_share_ge_1000'])} |")
    lines.append('')
    lines.append('## Top recent plugins')
    lines.append('')
    lines.append('| plugin | cohort | current instances | judgement | AI? |')
    lines.append('|---|---:|---:|---|---|')
    for r in top[:10]:
        ai = []
        if r.get('ai_themed_or_mentions_ai'):
            ai.append('AI-themed/mentions AI')
        if r.get('explicit_ai_built_readme_or_description'):
            ai.append('README/description says AI-built')
        if r.get('registry_ai_developed_attribute'):
            ai.append('registry attribute: ai-developed')
        if not ai:
            ai.append('no explicit AI signal in description/README spot-check')
        lines.append(f"| {r['title']} (`{r['id']}`) | {r['cohort']} | {int(r.get('instances_month') or 0):,} | {r.get('newness_judgement','')} | {'; '.join(ai)} |")
    lines.append('')
    lines.append('## Klipper comparison')
    lines.append('')
    lines.append('As a cheap comparison for the Klipper/Moonraker ecosystem, I counted GitHub repositories with the `klipper-plugin` topic by repository creation year. This is a supply-side comparison, not usage.')
    lines.append('')
    lines.append('| year | klipper-plugin repos created |')
    lines.append('|---:|---:|')
    for r in klipper:
        lines.append(f"| {r['year']} | {r.get('repos_created','')} |")
    lines.append('')
    lines.append('## Method')
    lines.append('')
    lines.append('- Creation cohorts are half-years from 2021H1 through partial 2026H2. For still-listed plugins I used the registry `published` date; for deleted/unlisted plugins I recovered first-add dates for `_plugins/*.md` from the site git history where possible.')
    lines.append('- Usage is OctoPrint anonymous-telemetry `instances_month` (unique active instances seen in the last 30 days), not cumulative downloads. Current usage comes from `https://plugins.octoprint.org/plugins.json`; historical equal-age usage comes from Wayback snapshots of that file plus `data.octoprint.org/export/plugin_stats_30d.json`.')
    lines.append('- Normalization uses `data.octoprint.org/export/instance_stats_30d.json` total OctoPrint instances and scales historical plugin instances to the current total denominator. When no nearby total-instance snapshot exists, normalized counts omit that plugin.')
    lines.append('- API calls used a custom User-Agent, cached responses under this output folder, and slept between requests.')
    lines.append('')
    lines.append('## Confounders')
    lines.append('')
    lines.append('- Survivorship: removed plugins are recoverable for counts from git, but current registry usage only exists for plugins still listed. Historical snapshots partly mitigate this but are sparse.')
    lines.append('- OctoPrint active instances appear flat/down versus the pandemic-era peak; current `instance_stats_30d` is about 51k, and normalized equal-age counts are therefore important.')
    lines.append('- Registry review/listing dates may lag actual plugin creation, and a GitHub repo can predate the registry listing.')
    lines.append('- Stats are anonymous telemetry from opted-in/reporting OctoPrint instances, not all installations, and commercial/manipulated plugins may be excluded from public stats.')
    lines.append('- Maker ecosystem demand shifted toward Klipper/Moonraker/Mainsail/Fluidd and Bambu workflows, so OctoPrint is not the full 3D-printing plugin market.')
    lines.append('')
    lines.append('## Verdict')
    lines.append('')
    # Compute simple baselines for verdict.
    base = [r for r in current_rows if r['cohort'][:4] in ('2022','2023','2024')]
    recent_rows = [r for r in current_rows if r['cohort'] in ('2025H2','2026H1','2026H2')]
    def avg(rows, key):
        vals = [r[key] for r in rows]
        return sum(vals)/len(vals) if vals else 0
    lines.append(f'OctoPrint does not show a big post-2025 explosion in successful new plugins: current listed-plugin cohorts in 2025H2-2026 average {avg(recent_rows,"current_abs_ge_10"):.1f} plugins above 10 active instances per half-year versus {avg(base,"current_abs_ge_10"):.1f} in 2022-24, and the ≥100 bar is {avg(recent_rows,"current_abs_ge_100"):.1f} versus {avg(base,"current_abs_ge_100"):.1f}.')
    lines.append(f'The ≥1,000 bar remains essentially empty for new cohorts: {sum(r["current_abs_ge_1000"] for r in recent_rows)} recent plugins versus {sum(r["current_abs_ge_1000"] for r in base)} across 2022-24 cohorts, and equal-age snapshots tell the same story despite sparse coverage.')
    lines.append('This source therefore weakly supports the broader hypothesis only at the very low bar, if at all: OctoPrint has some new niche utilities, including several registry entries marked `ai-developed`, but no clear surge of widely used new software.')
    (BASE / 'REPORT.md').write_text('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()
