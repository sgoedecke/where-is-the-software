#!/usr/bin/env python3
"""Collect Steam release cohorts, sampled early-review usage, and AI disclosures.

All outputs and caches live under market-usage/steam/.
"""
from __future__ import annotations

import concurrent.futures as cf
import csv
import datetime as dt
import html as html_lib
import json
import math
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE = Path('/Users/seangoedecke/Code/where-is-the-software/market-usage/steam')
CACHE = BASE / 'cache'
DATA = BASE / 'data'
SCRIPTS = BASE / 'scripts'
for p in [CACHE, DATA, SCRIPTS, CACHE / 'search', CACHE / 'hist', CACHE / 'apphtml', CACHE / 'top_search', CACHE / 'appdetails']:
    p.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X) Steam cohort analysis; contact: local research script',
    'Accept-Language': 'en-US,en;q=0.9',
}
START_DATE = dt.date(2021, 1, 1)
END_DATE = dt.date(2026, 9, 30)
CURRENT_DATE = dt.date(2026, 10, 15)
SAMPLE_PER_MONTH = int(os.environ.get('STEAM_SAMPLE_PER_MONTH', '300'))
AI_SAMPLE_PER_MONTH = int(os.environ.get('STEAM_AI_SAMPLE_PER_MONTH', '200'))
MAX_WORKERS = int(os.environ.get('STEAM_WORKERS', '24'))

DATE_FORMATS = ['%b %d, %Y', '%d %b, %Y', '%Y-%m-%d']


def request_bytes(url: str, tries: int = 5, sleep: float = 1.0) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last = e
            code = getattr(e, 'code', None)
            if code == 429:
                wait = 35 * (i + 1) + random.random()
            else:
                wait = sleep * (2 ** i) + random.random() * 0.5
            time.sleep(wait)
    raise RuntimeError(f'failed after {tries} tries: {url}: {last}')


def read_json_cache(path: Path):
    if path.exists() and path.stat().st_size:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    return None


def fetch_json_cached(url: str, path: Path):
    cached = read_json_cache(path)
    if cached is not None:
        return cached
    data = json.loads(request_bytes(url).decode('utf-8', 'replace'))
    tmp = path.with_suffix(path.suffix + '.part')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    tmp.replace(path)
    return data


def fetch_text_cached(url: str, path: Path) -> str:
    if path.exists() and path.stat().st_size:
        return path.read_text(encoding='utf-8', errors='replace')
    text = request_bytes(url).decode('utf-8', 'replace')
    tmp = path.with_suffix(path.suffix + '.part')
    tmp.write_text(text, encoding='utf-8')
    tmp.replace(path)
    return text


def parse_release_date(s: str) -> dt.date | None:
    s = html_lib.unescape(re.sub(r'\s+', ' ', s or '')).strip()
    if not s or 'soon' in s.lower() or 'to be announced' in s.lower():
        return None
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    # Some search locales use no comma, e.g. 15 Oct 2026
    for fmt in ['%d %b %Y', '%b %d %Y']:
        try:
            return dt.datetime.strptime(s.replace(',', ''), fmt).date()
        except ValueError:
            pass
    return None


def clean_html_text(s: str) -> str:
    s = re.sub(r'<[^>]+>', ' ', s or '')
    return html_lib.unescape(re.sub(r'\s+', ' ', s)).strip()


def parse_search_html(html: str) -> list[dict]:
    rows = re.findall(r'<a\b[^>]*class="[^"]*search_result_row[^"]*"[\s\S]*?</a>', html)
    out = []
    for row in rows:
        app_m = re.search(r'data-ds-appid="(\d+)"', row)
        if not app_m:
            continue
        title_m = re.search(r'<span class="title">([\s\S]*?)</span>', row)
        date_m = re.search(r'<div class="search_released[^>]*">([\s\S]*?)</div>', row)
        price_m = re.search(r'data-price-final="(\d+)"', row)
        review_m = re.search(r'<span class="search_review_summary[^>]*data-tooltip-html="([^"]*)"', row)
        appid = int(app_m.group(1))
        title = clean_html_text(title_m.group(1) if title_m else '')
        release_raw = clean_html_text(date_m.group(1) if date_m else '')
        release_date = parse_release_date(release_raw)
        current_review_tooltip = html_lib.unescape(review_m.group(1)) if review_m else ''
        cur_reviews = None
        rm = re.search(r'([\d,]+)\s+user reviews', current_review_tooltip)
        if rm:
            cur_reviews = int(rm.group(1).replace(',', ''))
        out.append({
            'appid': appid,
            'title': title,
            'release_raw': release_raw,
            'release_date': release_date.isoformat() if release_date else '',
            'price_final_cents': int(price_m.group(1)) if price_m else None,
            'current_review_tooltip': current_review_tooltip,
            'current_reviews_search': cur_reviews,
        })
    return out


def obvious_non_game(title: str) -> bool:
    t = title.strip().lower()
    # category1=998 already restricts to games; this removes obvious demos/soundtracks that leak into search.
    bad_suffixes = [' demo', ': demo', ' soundtrack', ' ost', ' original soundtrack', ' artbook', ' art book']
    if any(t.endswith(x) for x in bad_suffixes):
        return True
    if re.search(r'\b(soundtrack|ost)\b', t) and not re.search(r'\b(soundtrack attack|ostfront)\b', t):
        return True
    if re.search(r'\b(dlc|expansion pass|season pass)\b', t):
        return True
    return False


def crawl_supply() -> list[dict]:
    by_app = {}
    start = 0
    count = 100
    old_pages = 0
    while True:
        url = ('https://store.steampowered.com/search/results/?'
               + urllib.parse.urlencode({
                   'sort_by': 'Released_DESC', 'category1': '998', 'json': '1', 'infinite': '1',
                   'start': start, 'count': count, 'cc': 'US', 'l': 'english'
               }))
        path = CACHE / 'search' / f'released_desc_{start}_{count}.json'
        data = fetch_json_cached(url, path)
        html = data.get('results_html') or ''
        rows = parse_search_html(html)
        if not rows:
            print(f'No rows at start={start}; stopping')
            break
        dates = []
        for r in rows:
            if obvious_non_game(r['title']):
                continue
            d = parse_release_date(r['release_date']) if r['release_date'] else None
            if d:
                dates.append(d)
                if START_DATE <= d <= END_DATE:
                    r['release_month'] = d.strftime('%Y-%m')
                    r['cohort'] = f'{d.year}H{1 if d.month <= 6 else 2}'
                    by_app[r['appid']] = r
        if dates:
            print(f'start={start:6d} rows={len(rows):3d} kept={len(by_app):5d} page {max(dates)}..{min(dates)}')
            if max(dates) < START_DATE:
                old_pages += 1
            else:
                old_pages = 0
            if old_pages >= 2:
                break
        start += count
        if start > int(data.get('total_count') or 200000):
            break
        time.sleep(1.2)
    apps = sorted(by_app.values(), key=lambda r: (r['release_date'], r['appid']))
    write_csv(DATA / 'steam_supply_apps.csv', apps, ['appid','title','release_date','release_month','cohort','price_final_cents','current_reviews_search','current_review_tooltip','release_raw'])
    return apps


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_supply_csv() -> list[dict]:
    path = DATA / 'steam_supply_apps.csv'
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def pick_monthly_sample(apps: list[dict], per_month: int) -> set[int]:
    rng = random.Random(20261015)
    groups = defaultdict(list)
    for a in apps:
        groups[a['release_month']].append(a)
    chosen = set()
    for month, items in sorted(groups.items()):
        items = list(items)
        rng.shuffle(items)
        for a in items[:min(per_month, len(items))]:
            chosen.add(int(a['appid']))
    return chosen


def month_bounds(d: dt.date) -> tuple[dt.date, dt.date]:
    start = d.replace(day=1)
    if d.month == 12:
        end = dt.date(d.year + 1, 1, 1)
    else:
        end = dt.date(d.year, d.month + 1, 1)
    return start, end


def count_rollups(hist: dict, release_date: dt.date, days: int) -> int | None:
    if not hist or hist.get('success') != 1:
        return None
    cutoff = release_date + dt.timedelta(days=days)
    total = 0
    for item in hist.get('results', {}).get('rollups', []):
        try:
            ms = dt.datetime.utcfromtimestamp(int(item.get('date'))).date()
        except Exception:
            continue
        mstart, mend = month_bounds(ms)
        # Include monthly bucket if it overlaps [release_date, cutoff). This is approximate but matches endpoint granularity.
        if mend <= release_date or mstart >= cutoff:
            continue
        total += int(item.get('recommendations_up') or 0) + int(item.get('recommendations_down') or 0)
    return total


def fetch_hist_one(app: dict) -> dict:
    appid = int(app['appid'])
    url = f'https://store.steampowered.com/appreviewhistogram/{appid}?l=english&review_score_preference=0&review_type=all&purchase_type=all'
    path = CACHE / 'hist' / f'{appid}.json'
    try:
        hist = fetch_json_cached(url, path)
    except Exception as e:
        return {'appid': appid, 'hist_error': str(e)}
    rd = dt.date.fromisoformat(app['release_date'])
    r90 = count_rollups(hist, rd, 90)
    r365 = count_rollups(hist, rd, 365)
    current = None
    if hist and hist.get('success') == 1:
        current = sum(int(x.get('recommendations_up') or 0) + int(x.get('recommendations_down') or 0)
                      for x in hist.get('results', {}).get('rollups', []))
    return {
        'appid': appid,
        'reviews_90d': r90,
        'reviews_365d': r365,
        'reviews_current_hist': current,
        'hist_success': hist.get('success') if isinstance(hist, dict) else '',
        'hist_error': '',
    }


def extract_ai_disclosure(page: str) -> tuple[bool, str]:
    if 'AI Generated Content Disclosure' not in page:
        return False, ''
    idx = page.find('AI Generated Content Disclosure')
    snip = page[idx:idx + 2500]
    # Text is usually the first italic paragraph after the heading.
    im = re.search(r'<i>\s*([\s\S]*?)\s*</i>', snip)
    if im:
        return True, clean_html_text(im.group(1))
    return True, ''


def fetch_ai_one(app: dict) -> dict:
    appid = int(app['appid'])
    url = f'https://store.steampowered.com/app/{appid}/?cc=US&l=english'
    path = CACHE / 'apphtml' / f'{appid}.html'
    try:
        page = fetch_text_cached(url, path)
        flag, note = extract_ai_disclosure(page)
        return {'appid': appid, 'ai_checked': 1, 'ai_disclosure': int(flag), 'ai_disclosure_text': note, 'ai_error': ''}
    except Exception as e:
        return {'appid': appid, 'ai_checked': 0, 'ai_disclosure': '', 'ai_disclosure_text': '', 'ai_error': str(e)}


def add_reviews_and_ai(apps: list[dict]) -> list[dict]:
    sample_ids = pick_monthly_sample(apps, SAMPLE_PER_MONTH)
    sampled = [a for a in apps if int(a['appid']) in sample_ids]
    print(f'Review sample: {len(sampled)} apps ({SAMPLE_PER_MONTH}/month cap)')
    hist_rows = {}
    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(fetch_hist_one, a): a for a in sampled}
        done = 0
        for fut in cf.as_completed(futs):
            row = fut.result()
            hist_rows[int(row['appid'])] = row
            done += 1
            if done % 500 == 0:
                print(f'  hist {done}/{len(sampled)}')
    # AI disclosure became mandatory/visible in Jan 2024; sample these months.
    ai_ids = set()
    monthly = defaultdict(list)
    for a in apps:
        d = dt.date.fromisoformat(a['release_date'])
        if d >= dt.date(2024, 1, 1):
            monthly[a['release_month']].append(a)
    rng = random.Random(20261016)
    for month, items in monthly.items():
        items = list(items)
        rng.shuffle(items)
        for a in items[:min(AI_SAMPLE_PER_MONTH, len(items))]:
            ai_ids.add(int(a['appid']))
    # Ensure review sample recent rows also have AI when in post-policy window.
    for a in sampled:
        if dt.date.fromisoformat(a['release_date']) >= dt.date(2024, 1, 1):
            ai_ids.add(int(a['appid']))
    ai_apps = [a for a in apps if int(a['appid']) in ai_ids]
    print(f'AI disclosure sample: {len(ai_apps)} apps')
    ai_rows = {}
    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(fetch_ai_one, a): a for a in ai_apps}
        done = 0
        for fut in cf.as_completed(futs):
            row = fut.result()
            ai_rows[int(row['appid'])] = row
            done += 1
            if done % 500 == 0:
                print(f'  ai {done}/{len(ai_apps)}')
    rows = []
    for a in sampled:
        rd = dt.date.fromisoformat(a['release_date'])
        out = dict(a)
        out.update(hist_rows.get(int(a['appid']), {}))
        out.update(ai_rows.get(int(a['appid']), {'ai_checked': 0, 'ai_disclosure': '', 'ai_disclosure_text': '', 'ai_error': ''}))
        out['eligible_90d'] = int(rd + dt.timedelta(days=90) <= CURRENT_DATE)
        out['eligible_365d'] = int(rd + dt.timedelta(days=365) <= CURRENT_DATE)
        rows.append(out)
    fields = ['appid','title','release_date','release_month','cohort','reviews_90d','reviews_365d','reviews_current_hist','eligible_90d','eligible_365d','hist_success','hist_error','ai_checked','ai_disclosure','ai_disclosure_text','ai_error','price_final_cents','current_reviews_search']
    write_csv(DATA / 'steam_sample_reviews.csv', rows, fields)
    # Separate AI sample rows, including non-review-sampled apps.
    ai_out = []
    by_app = {int(a['appid']): a for a in apps}
    for appid, ai in ai_rows.items():
        r = dict(by_app[appid])
        r.update(ai)
        ai_out.append(r)
    write_csv(DATA / 'steam_ai_disclosure_sample.csv', ai_out, ['appid','title','release_date','release_month','cohort','ai_checked','ai_disclosure','ai_disclosure_text','ai_error'])
    return rows


def read_sample_reviews() -> list[dict]:
    path = DATA / 'steam_sample_reviews.csv'
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def read_ai_sample() -> list[dict]:
    path = DATA / 'steam_ai_disclosure_sample.csv'
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def threshold_count(rows: list[dict], metric: str, threshold: int) -> int:
    n = 0
    for r in rows:
        try:
            if int(float(r.get(metric) or -1)) >= threshold:
                n += 1
        except Exception:
            pass
    return n


def aggregate(apps: list[dict], samples: list[dict], ai_samples: list[dict]):
    months = sorted({a['release_month'] for a in apps})
    supply_by_month = {m: 0 for m in months}
    for a in apps:
        supply_by_month[a['release_month']] += 1
    write_csv(DATA / 'monthly_supply.csv', [{'release_month': m, 'supply': supply_by_month[m]} for m in months], ['release_month','supply'])

    samples_by_month = defaultdict(list)
    for r in samples:
        samples_by_month[r['release_month']].append(r)
    ai_by_month = defaultdict(list)
    for r in ai_samples:
        if str(r.get('ai_checked')) == '1':
            ai_by_month[r['release_month']].append(r)

    cohorts = sorted({a['cohort'] for a in apps})
    out = []
    for cohort in cohorts:
        cm = [m for m in months if f'{m[:4]}H{1 if int(m[5:7]) <= 6 else 2}' == cohort]
        supply = sum(supply_by_month[m] for m in cm)
        row = {'cohort': cohort, 'supply': supply}
        for days, metric, elig_key in [(90, 'reviews_90d', 'eligible_90d'), (365, 'reviews_365d', 'eligible_365d')]:
            scaled = {10: 0.0, 100: 0.0, 1000: 0.0}
            sample_n = 0
            eligible_supply = 0
            complete = True
            for m in cm:
                month_samples = [r for r in samples_by_month[m] if str(r.get(elig_key)) == '1' and r.get(metric) not in ('', None)]
                if not month_samples:
                    # Complete only when the month itself is too young; otherwise mark missing.
                    y, mo = map(int, m.split('-'))
                    last_day = (dt.date(y + (mo // 12), (mo % 12) + 1, 1) - dt.timedelta(days=1)) if mo < 12 else dt.date(y, 12, 31)
                    if last_day + dt.timedelta(days=days) <= CURRENT_DATE:
                        complete = False
                    continue
                month_supply = supply_by_month[m]
                eligible_supply += month_supply
                sample_n += len(month_samples)
                for th in scaled:
                    scaled[th] += month_supply * threshold_count(month_samples, metric, th) / len(month_samples)
            row[f'sample_n_{days}d'] = sample_n
            row[f'supply_eligible_{days}d'] = eligible_supply
            row[f'usage_{days}d_complete'] = int(complete and eligible_supply == supply)
            for th in [10, 100, 1000]:
                row[f'est_ge_{th}_reviews_{days}d'] = int(round(scaled[th])) if sample_n else ''
                row[f'pct_ge_{th}_reviews_{days}d'] = round((scaled[th] / eligible_supply * 100), 1) if eligible_supply else ''
        # AI disclosure share, monthly supply-weighted sample, post-Jan-2024 only.
        ai_scaled = 0.0
        ai_supply = 0
        ai_n = 0
        for m in cm:
            rows = ai_by_month[m]
            if rows:
                ai_supply += supply_by_month[m]
                ai_n += len(rows)
                ai_scaled += supply_by_month[m] * sum(1 for r in rows if str(r.get('ai_disclosure')) == '1') / len(rows)
        row['ai_sample_n'] = ai_n
        row['est_ai_disclosure_count'] = int(round(ai_scaled)) if ai_n else ''
        row['ai_disclosure_pct'] = round(ai_scaled / ai_supply * 100, 1) if ai_supply else ''
        out.append(row)
    fields = ['cohort','supply',
              'sample_n_90d','supply_eligible_90d','usage_90d_complete','est_ge_10_reviews_90d','pct_ge_10_reviews_90d','est_ge_100_reviews_90d','pct_ge_100_reviews_90d','est_ge_1000_reviews_90d','pct_ge_1000_reviews_90d',
              'sample_n_365d','supply_eligible_365d','usage_365d_complete','est_ge_10_reviews_365d','pct_ge_10_reviews_365d','est_ge_100_reviews_365d','pct_ge_100_reviews_365d','est_ge_1000_reviews_365d','pct_ge_1000_reviews_365d',
              'ai_sample_n','est_ai_disclosure_count','ai_disclosure_pct']
    write_csv(DATA / 'cohort_summary.csv', out, fields)


def collect_top_recent(apps: list[dict]):
    # Search rows sorted by current review count; then fetch hist/appdetails for recent candidates.
    rows = []
    count = 100
    for start in range(0, 5000, count):
        url = ('https://store.steampowered.com/search/results/?'
               + urllib.parse.urlencode({
                   'sort_by': 'Reviews_DESC', 'category1': '998', 'json': '1', 'infinite': '1',
                   'start': start, 'count': count, 'cc': 'US', 'l': 'english'
               }))
        data = fetch_json_cached(url, CACHE / 'top_search' / f'reviews_desc_{start}_{count}.json')
        parsed = parse_search_html(data.get('results_html') or '')
        if not parsed:
            break
        rows.extend(parsed)
        time.sleep(0.08)
    # Keep recent released games in 2025-2026 from search sorted by current reviews.
    app_by_id = {int(a['appid']): a for a in apps}
    recent = []
    seen = set()
    for r in rows:
        appid = int(r['appid'])
        if appid in seen or appid not in app_by_id:
            continue
        seen.add(appid)
        d = dt.date.fromisoformat(app_by_id[appid]['release_date'])
        if d >= dt.date(2025, 1, 1):
            x = dict(app_by_id[appid])
            x['current_reviews_search'] = r.get('current_reviews_search') or x.get('current_reviews_search') or ''
            recent.append(x)
        if len(recent) >= 80:
            break
    # Fetch hist/appdetails/AI for candidates.
    hist = {}
    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for rr in ex.map(fetch_hist_one, recent):
            hist[int(rr['appid'])] = rr
    ai = {}
    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for rr in ex.map(fetch_ai_one, recent):
            ai[int(rr['appid'])] = rr
    details = {}
    for a in recent:
        appid = int(a['appid'])
        url = f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=US&l=english'
        path = CACHE / 'appdetails' / f'{appid}.json'
        try:
            data = fetch_json_cached(url, path)
            d = data.get(str(appid), {}).get('data', {}) if isinstance(data, dict) else {}
            details[appid] = {
                'developers': '; '.join(d.get('developers') or []),
                'publishers': '; '.join(d.get('publishers') or []),
                'is_free': d.get('is_free'),
                'genres': '; '.join(g.get('description','') for g in (d.get('genres') or [])),
            }
        except Exception as e:
            details[appid] = {'developers':'', 'publishers':'', 'is_free':'', 'genres':'', 'details_error': str(e)}
        time.sleep(0.25)
    out = []
    for a in recent:
        appid = int(a['appid'])
        r = dict(a)
        r.update(hist.get(appid, {}))
        r.update(ai.get(appid, {}))
        r.update(details.get(appid, {}))
        out.append(r)
    def sort_key(r):
        try: return int(r.get('reviews_90d') or -1)
        except Exception: return -1
    out.sort(key=sort_key, reverse=True)
    fields = ['appid','title','release_date','cohort','reviews_90d','reviews_365d','reviews_current_hist','current_reviews_search','developers','publishers','genres','is_free','ai_disclosure','ai_disclosure_text']
    write_csv(DATA / 'top_recent_by_90d_reviews.csv', out[:50], fields)


def main():
    apps = read_supply_csv()
    if not apps:
        apps = crawl_supply()
    else:
        print(f'Read existing supply: {len(apps)}')
    # Ensure typed strings from CSV.
    if not (DATA / 'steam_sample_reviews.csv').exists():
        samples = add_reviews_and_ai(apps)
    else:
        samples = read_sample_reviews()
        print(f'Read existing review sample: {len(samples)}')
    ai_samples = read_ai_sample()
    aggregate(apps, samples, ai_samples)
    collect_top_recent(apps)
    print('Done. Outputs under', DATA)

if __name__ == '__main__':
    main()
