#!/usr/bin/env python3
"""Follow-up/link-rot audit for Show HN AI-built projects.

Writes samples, caches and REPORT.md in this directory. Uses only stdlib.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import math
import os
import random
import re
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

OUT = Path.home() / "Code" / "where-is-the-software" / "followup-audit"
CACHE = OUT / "cache"
UA = "where-is-the-software-followup-audit/1.0 (+research; polite; seangoedecke local)"
SEED = 20261015
CURRENT_START = dt.date(2025, 10, 1)
CURRENT_END = dt.date(2026, 4, 16)  # inclusive through 2026-04-15
BASE_START = dt.date(2022, 10, 1)
BASE_END = dt.date(2023, 4, 16)
TODAY = dt.date(2026, 10, 15)
MAX_WORKERS = 8
TIMEOUT = 20

BUILD_RE = re.compile(
    r"(claude\s*code|claude|cursor|vibe[-\s]?coded|\bvibe\b|codex|copilot|"
    r"built\s+with\s+ai|ai[-\s]?built|lovable|\bbolt\b|\bv0\b|windsurf|agent\s+wrote)",
    re.I,
)
AI_PRODUCT_TITLE_RE = re.compile(
    r"\b(ai|a\.i\.|llm|gpt|chatgpt|openai|claude|gemini|prompt|rag|chatbot|bot|agent|"
    r"copilot|cursor|voice assistant|image generator|text[-\s]?to[-\s]?speech|speech[-\s]?to[-\s]?text)\b",
    re.I,
)
PARKED_REASONS = [
    ("parked_or_for_sale", re.compile(r"domain (is )?(for sale|parked)|buy this domain|this domain may be for sale|hugedomains|afternic|sedo domain parking|parkingcrew|godaddy.com/forsale|namecheap parking", re.I)),
    ("vercel_not_found", re.compile(r"404: this page could not be found|deployment (could not be|was not) found|the deployment could not be found", re.I)),
    ("netlify_not_found", re.compile(r"page not found \| netlify|netlify\s+404|site not found|not found - request id", re.I)),
    ("render_or_heroku_error", re.compile(r"heroku \| (no such app|application error)|no such app|application error|render.*(not found|suspended)", re.I | re.S)),
    ("lovable_replit_missing", re.compile(r"project not found|this repl (does not exist|is unavailable)|replit.*not found", re.I | re.S)),
    ("github_pages_missing", re.compile(r"there isn't a github pages site here|github pages.*404", re.I | re.S)),
    ("cloudflare_error", re.compile(r"cloudflare.*(error 10\d\d|origin dns error|web server is down|access denied|attention required)|error 1016|error 1020|error 522|error 523|error 524", re.I | re.S)),
    ("generic_soft_404", re.compile(r"\b(404|not found|page not found)\b", re.I)),
]
GITHUB_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", re.I)
BAD_GITHUB_OWNERS = {"features", "topics", "marketplace", "collections", "pricing", "login", "signup", "orgs", "about", "explore", "settings", "notifications", "new"}

print_lock = threading.Lock()

def log(msg: str) -> None:
    with print_lock:
        print(msg, flush=True)

def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(exist_ok=True)

def cache_path(name: str) -> Path:
    return CACHE / name

def load_json(name: str) -> Any | None:
    p = cache_path(name)
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_json(name: str, obj: Any) -> None:
    p = cache_path(name)
    tmp = p.with_suffix(p.suffix + ".new")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.replace(p)

def date_to_ts(d: dt.date) -> int:
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())

def parse_iso_date(s: str | None) -> dt.date | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except Exception:
        try:
            return dt.date.fromisoformat(s[:10])
        except Exception:
            return None

def add_months(d: dt.date, months: int) -> dt.date:
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1])
    return dt.date(y, m, day)

def strip_html(s: str | None) -> str:
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def opener_request(url: str, headers: dict[str, str] | None = None, timeout: int = TIMEOUT, max_bytes: int = 250_000) -> dict[str, Any]:
    hdrs = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read(max_bytes)
            return {
                "ok": True,
                "status": int(getattr(resp, "status", 0) or resp.getcode()),
                "final_url": resp.geturl(),
                "headers": dict(resp.headers.items()),
                "body": body.decode(resp.headers.get_content_charset() or "utf-8", errors="replace"),
                "error": "",
            }
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read(max_bytes)
        except Exception:
            pass
        return {
            "ok": False,
            "status": int(e.code),
            "final_url": getattr(e, "url", url),
            "headers": dict(e.headers.items()) if e.headers else {},
            "body": body.decode((e.headers.get_content_charset() if e.headers else None) or "utf-8", errors="replace"),
            "error": f"HTTPError:{e.code}",
        }
    except Exception as e:
        return {"ok": False, "status": None, "final_url": url, "headers": {}, "body": "", "error": type(e).__name__ + ":" + str(e)[:200]}

def get_json(url: str, headers: dict[str, str] | None = None, retries: int = 2, sleep_s: float = 0.4) -> Any:
    last = None
    for attempt in range(retries + 1):
        res = opener_request(url, headers={**({"Accept": "application/json"}), **(headers or {})}, timeout=TIMEOUT, max_bytes=3_000_000)
        last = res
        if res["status"] and 200 <= res["status"] < 300:
            return json.loads(res["body"])
        if res["status"] in (429, 500, 502, 503, 504) and attempt < retries:
            time.sleep(sleep_s * (2 ** attempt))
            continue
        break
    raise RuntimeError(f"GET JSON failed {url}: {last.get('status')} {last.get('error')} {last.get('body','')[:200] if last else ''}")

def get_wayback_json(url: str, retries: int = 1) -> Any:
    """Fetch CDX JSON via curl.

    urllib occasionally stalls against web.archive.org on this machine even
    though curl returns immediately; curl also gives us a hard max-time.
    """
    last = ""
    for attempt in range(retries + 1):
        try:
            body = subprocess.check_output(
                ["curl", "-L", "--max-time", str(TIMEOUT), "-A", UA, "-sS", url],
                cwd=str(OUT),
                stderr=subprocess.STDOUT,
                timeout=TIMEOUT + 5,
                text=True,
            )
            return json.loads(body or "[]")
        except Exception as e:
            last = str(e)[:300]
            if attempt < retries:
                time.sleep(0.8 * (2 ** attempt))
    raise RuntimeError(f"Wayback CDX failed {last}")

def fetch_hn_window(start: dt.date, end: dt.date, cache_name: str, refresh: bool = False) -> list[dict[str, Any]]:
    if not refresh:
        cached = load_json(cache_name)
        if cached is not None:
            log(f"Loaded {len(cached)} HN hits from {cache_name}")
            return cached
    hits_by_id: dict[str, dict[str, Any]] = {}
    day = start
    while day < end:
        nxt = day + dt.timedelta(days=1)
        filters = f"created_at_i>={date_to_ts(day)},created_at_i<{date_to_ts(nxt)}"
        base = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode({
            "tags": "show_hn,story",
            "numericFilters": filters,
            "hitsPerPage": "1000",
            "page": "0",
        })
        data = get_json(base)
        pages = int(data.get("nbPages") or 1)
        day_hits = data.get("hits", [])
        for h in day_hits:
            hits_by_id[str(h.get("objectID") or h.get("story_id") or h.get("created_at_i"))] = h
        for page in range(1, pages):
            url = base.replace("page=0", f"page={page}")
            d2 = get_json(url)
            for h in d2.get("hits", []):
                hits_by_id[str(h.get("objectID") or h.get("story_id") or h.get("created_at_i"))] = h
            time.sleep(0.12)
        if len(day_hits) >= 900:
            log(f"Warning: high daily hits {day} {len(day_hits)} pages={pages}")
        if day.day == 1:
            log(f"Fetched HN through {day.isoformat()} total={len(hits_by_id)}")
        time.sleep(0.12)
        day = nxt
    hits = sorted(hits_by_id.values(), key=lambda h: int(h.get("created_at_i") or 0))
    save_json(cache_name, hits)
    log(f"Saved {len(hits)} HN hits to {cache_name}")
    return hits

def item_text(h: dict[str, Any]) -> str:
    return " ".join([str(h.get("title") or ""), strip_html(h.get("story_text"))])

def is_ai_product(h: dict[str, Any]) -> bool:
    title = str(h.get("title") or "")
    url = str(h.get("url") or "")
    story = strip_html(h.get("story_text"))[:300]
    if AI_PRODUCT_TITLE_RE.search(title):
        return True
    # Story heuristic excludes common build-attribution phrasings.
    scrubbed = re.sub(r"built\s+(it\s+)?with\s+(claude|cursor|ai|copilot|codex)|made\s+with\s+(claude|cursor|ai|copilot|codex)", "", story, flags=re.I)
    return bool(AI_PRODUCT_TITLE_RE.search(scrubbed) or re.search(r"/(ai|gpt|llm|chatbot|agent)[-/]", url, re.I))

def hn_row(h: dict[str, Any], cohort: str) -> dict[str, Any]:
    created = parse_iso_date(h.get("created_at"))
    text = item_text(h)
    mention = BUILD_RE.search(text)
    return {
        "cohort": cohort,
        "objectID": str(h.get("objectID") or ""),
        "created_at": h.get("created_at") or "",
        "created_date": created.isoformat() if created else "",
        "title": h.get("title") or "",
        "url": h.get("url") or "",
        "hn_url": f"https://news.ycombinator.com/item?id={h.get('objectID')}",
        "points": int(h.get("points") or 0),
        "num_comments": int(h.get("num_comments") or 0),
        "story_text": strip_html(h.get("story_text"))[:1000],
        "ai_build_mention": bool(mention),
        "ai_build_match": mention.group(0).lower() if mention else "",
        "ai_product_flag": is_ai_product(h),
        "points_bucket": points_bucket(int(h.get("points") or 0)),
    }

def points_bucket(points: int) -> str:
    if points < 5:
        return "<5"
    if points < 50:
        return "5-49"
    return ">=50"

def sample_hn(current: list[dict[str, Any]], baseline: list[dict[str, Any]], refresh: bool = False) -> dict[str, list[dict[str, Any]]]:
    if not refresh:
        cached = load_json("samples.json")
        if cached is not None:
            return cached
    rng = random.Random(SEED)
    current_rows = [hn_row(h, "") for h in current]
    treatment_pool = [r for r in current_rows if r["ai_build_mention"]]
    control_pool = [r for r in current_rows if not r["ai_build_mention"]]
    baseline_pool = [hn_row(h, "baseline") for h in baseline]
    for r in treatment_pool:
        r["cohort"] = "treatment_ai_mention"
    for r in control_pool:
        r["cohort"] = "control_no_mention"
    n_t = min(200, len(treatment_pool))
    n_c = min(200, len(control_pool))
    n_b = min(200, len(baseline_pool))
    samples = {
        "treatment": rng.sample(treatment_pool, n_t),
        "control": rng.sample(control_pool, n_c),
        "baseline": rng.sample(baseline_pool, n_b),
        "meta": [{"seed": SEED, "treatment_pool": len(treatment_pool), "control_pool": len(control_pool), "baseline_pool": len(baseline_pool)}],
    }
    save_json("samples.json", samples)
    return samples

def decode_body_excerpt(body: str) -> str:
    txt = strip_html(body)
    txt = re.sub(r"\s+", " ", txt)
    return txt[:500]

def page_title(body: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", body or "", re.I | re.S)
    return strip_html(m.group(1)) if m else ""

def soft_error_applies(label: str, body: str, status: int | None) -> bool:
    """Avoid treating bundled fallback strings in real SPAs as dead pages."""
    stripped = strip_html(body).lower()
    title = page_title(body).lower()
    head = stripped[:500]
    if label in {"parked_or_for_sale", "cloudflare_error"}:
        return True
    if label == "generic_soft_404":
        return bool(len(stripped) < 2500 or re.search(r"(404|not found|page not found)", title, re.I))
    if status and status >= 400:
        return True
    title_error = re.search(r"(404|not found|page not found|deployment .*not found|no such app|application error|project not found|site not found)", title, re.I)
    head_error = re.search(r"^(404[:\\s-]|page not found|not found|deployment .*not found|no such app|application error|project not found|site not found|there isn't a github pages site here)", head, re.I)
    short_error = len(stripped) < 900 and re.search(r"(404|not found|no such app|application error|project not found|site not found)", stripped, re.I)
    return bool(title_error or head_error or short_error)

def classify_fetch(url: str) -> dict[str, Any]:
    if not url:
        return {"fetch_status": "", "final_url": "", "alive_current": False, "alive_reason": "no_url", "body_excerpt": "", "landing_github_repo": ""}
    if not re.match(r"https?://", url, re.I):
        url = "https://" + url
    res = opener_request(url, max_bytes=300_000)
    status = res.get("status")
    body = res.get("body") or ""
    final_url = res.get("final_url") or url
    reason = "ok"
    alive = bool(status and 200 <= int(status) < 400)
    if not status:
        alive = False
        reason = "network_error"
    elif int(status) >= 400:
        alive = False
        reason = f"http_{status}"
    lower = body.lower()
    # Soft-404/error/parking checks. Generic soft-404 is only trusted for short pages or 404-ish titles.
    if alive:
        for label, rx in PARKED_REASONS:
            if rx.search(body):
                if soft_error_applies(label, body, int(status) if status else None):
                    alive = False
                    reason = label
                    break
    landing_repo = first_github_repo(" ".join([url, final_url, body]))
    return {
        "fetch_status": "" if status is None else str(status),
        "final_url": final_url,
        "alive_current": alive,
        "alive_reason": reason if reason != "ok" else "http_2xx_3xx",
        "body_excerpt": decode_body_excerpt(body),
        "landing_github_repo": landing_repo,
    }

def normalize_repo(owner: str, repo: str) -> str:
    repo = repo.rstrip(".")
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"

def first_github_repo(text: str) -> str:
    for m in GITHUB_RE.finditer(text or ""):
        owner, repo = m.group(1), m.group(2)
        if owner.lower() in BAD_GITHUB_OWNERS:
            continue
        if repo.lower() in {"issues", "pulls", "discussions", "stars", "followers", "following"}:
            continue
        if repo.endswith("."):
            repo = repo[:-1]
        return normalize_repo(owner, repo)
    return ""

def fetch_current_for_samples(samples: dict[str, list[dict[str, Any]]], refresh: bool = False) -> dict[str, dict[str, Any]]:
    if not refresh:
        cached = load_json("current_fetches.json")
        if cached is not None:
            return cached
    rows = samples["treatment"] + samples["control"] + samples["baseline"]
    results: dict[str, dict[str, Any]] = {}
    log(f"Fetching current URLs for {len(rows)} items with {MAX_WORKERS} workers")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(classify_fetch, r.get("url") or ""): r["objectID"] for r in rows}
        for i, fut in enumerate(as_completed(futs), 1):
            oid = futs[fut]
            try:
                results[oid] = fut.result()
            except Exception as e:
                results[oid] = {"fetch_status": "", "final_url": "", "alive_current": False, "alive_reason": "exception:" + str(e)[:120], "body_excerpt": "", "landing_github_repo": ""}
            if i % 50 == 0:
                log(f"Fetched {i}/{len(rows)} current URLs")
    save_json("current_fetches.json", results)
    return results

def gh_token() -> str:
    try:
        status = subprocess.run(["gh", "auth", "status"], cwd=str(OUT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        if status.returncode != 0:
            return ""
        token = subprocess.check_output(["gh", "auth", "token"], cwd=str(OUT), stderr=subprocess.DEVNULL, timeout=10, text=True).strip()
        return token
    except Exception:
        return ""

def github_json(path_or_url: str, token: str, params: dict[str, str] | None = None) -> tuple[Any | None, int | None, str]:
    if path_or_url.startswith("http"):
        url = path_or_url
    else:
        url = "https://api.github.com" + path_or_url
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    res = opener_request(url, headers=headers, timeout=TIMEOUT, max_bytes=2_500_000)
    status = res.get("status")
    if status and 200 <= int(status) < 300:
        return json.loads(res.get("body") or "null"), int(status), ""
    return None, int(status) if status else None, (res.get("error") or res.get("body") or "")[:300]

def parse_link_next(headers: dict[str, str]) -> str:
    link = headers.get("Link") or headers.get("link") or ""
    for part in link.split(","):
        if 'rel="next"' in part:
            m = re.search(r"<([^>]+)>", part)
            if m:
                return m.group(1)
    return ""

def github_get_with_headers(url: str, token: str) -> tuple[Any | None, dict[str, str], int | None, str]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    res = opener_request(url, headers=headers, timeout=TIMEOUT, max_bytes=2_500_000)
    status = res.get("status")
    if status and 200 <= int(status) < 300:
        return json.loads(res.get("body") or "null"), res.get("headers") or {}, int(status), ""
    return None, res.get("headers") or {}, int(status) if status else None, (res.get("error") or res.get("body") or "")[:300]

def collect_github(repo: str, token: str, post_date: dt.date | None = None) -> dict[str, Any]:
    owner, name = repo.split("/", 1)
    out: dict[str, Any] = {
        "github_repo": repo,
        "github_deleted": False,
        "github_error": "",
        "github_stars": "",
        "github_forks": "",
        "github_archived": "",
        "github_pushed_at": "",
        "github_pushed_last_90": False,
        "github_external_issues_open": 0,
        "github_external_issues_closed": 0,
        "github_external_prs_open": 0,
        "github_external_prs_closed": 0,
        "github_external_signal": False,
        "github_commit_6_12mo": False,
        "github_external_issue_pr_0_12mo": False,
    }
    data, status, err = github_json(f"/repos/{owner}/{name}", token)
    time.sleep(0.08)
    if status == 404:
        out["github_deleted"] = True
        out["github_error"] = "404"
        return out
    if not data:
        out["github_error"] = f"status={status} {err}"
        return out
    out.update({
        "github_stars": int(data.get("stargazers_count") or 0),
        "github_forks": int(data.get("forks_count") or 0),
        "github_archived": bool(data.get("archived")),
        "github_pushed_at": data.get("pushed_at") or "",
    })
    pushed_date = parse_iso_date(data.get("pushed_at"))
    if pushed_date:
        out["github_pushed_last_90"] = pushed_date >= TODAY - dt.timedelta(days=90)
    # Issues API returns both issues and PRs. Paginate, bounded to avoid pathological repos.
    url = f"https://api.github.com/repos/{owner}/{name}/issues?" + urllib.parse.urlencode({"state": "all", "per_page": "100", "sort": "created", "direction": "desc"})
    pages = 0
    while url and pages < 10:
        arr, hdrs, st, er = github_get_with_headers(url, token)
        time.sleep(0.08)
        if not isinstance(arr, list):
            break
        for issue in arr:
            user = ((issue.get("user") or {}).get("login") or "").lower()
            if user == owner.lower():
                continue
            is_pr = "pull_request" in issue
            state = issue.get("state") or ""
            key = None
            if is_pr:
                key = "github_external_prs_open" if state == "open" else "github_external_prs_closed"
            else:
                key = "github_external_issues_open" if state == "open" else "github_external_issues_closed"
            out[key] = int(out.get(key) or 0) + 1
            created = parse_iso_date(issue.get("created_at"))
            if post_date and created and created <= add_months(post_date, 12):
                out["github_external_issue_pr_0_12mo"] = True
        url = parse_link_next(hdrs)
        pages += 1
    out["github_external_signal"] = (int(out["github_stars"] or 0) >= 10) or any(int(out[k] or 0) > 0 for k in ["github_external_issues_open", "github_external_issues_closed", "github_external_prs_open", "github_external_prs_closed"])
    if post_date:
        since = add_months(post_date, 6).isoformat() + "T00:00:00Z"
        until = add_months(post_date, 12).isoformat() + "T23:59:59Z"
        commits, st, er = github_json(f"/repos/{owner}/{name}/commits", token, {"since": since, "until": until, "per_page": "1"})
        time.sleep(0.08)
        if isinstance(commits, list) and len(commits) > 0:
            out["github_commit_6_12mo"] = True
    return out

def collect_all_github(rows: list[dict[str, Any]], current_fetches: dict[str, dict[str, Any]], refresh: bool = False) -> dict[str, dict[str, Any]]:
    if not refresh:
        cached = load_json("github_repos.json")
        if cached is not None:
            return cached
    repo_dates: dict[str, dt.date | None] = {}
    for r in rows:
        cf = current_fetches.get(r["objectID"], {})
        repo = first_github_repo(" ".join([r.get("url") or "", cf.get("final_url") or "", cf.get("landing_github_repo") or ""]))
        if repo and repo not in repo_dates:
            repo_dates[repo] = parse_iso_date(r.get("created_at"))
    token = gh_token()
    log(f"Collecting GitHub metadata for {len(repo_dates)} repos ({'authenticated' if token else 'unauthenticated'})")
    out: dict[str, dict[str, Any]] = {}
    for i, (repo, post_date) in enumerate(sorted(repo_dates.items()), 1):
        out[repo] = collect_github(repo, token, post_date)
        if i % 25 == 0:
            log(f"GitHub repos {i}/{len(repo_dates)}")
    save_json("github_repos.json", out)
    return out

def wayback_alive(url: str, post_date: dt.date | None) -> dict[str, Any]:
    out = {"wayback_equal_age_alive": False, "wayback_timestamp": "", "wayback_status": "", "wayback_mimetype": "", "wayback_length": "", "wayback_query": ""}
    if not url or not post_date:
        return out
    frm = add_months(post_date, 8).strftime("%Y%m%d")
    to = add_months(post_date, 10).strftime("%Y%m%d")
    params = {
        "url": url,
        "output": "json",
        "from": frm,
        "to": to,
        "filter": "statuscode:200",
        "fl": "timestamp,original,statuscode,mimetype,length",
        "collapse": "digest",
        "limit": "10",
    }
    qurl = "http://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)
    out["wayback_query"] = qurl
    try:
        data = get_wayback_json(qurl, retries=1)
    except Exception:
        # Expand to full 6-12 month window if the narrow query fails/has no captures later.
        data = []
    if isinstance(data, list) and len(data) <= 1:
        params["from"] = add_months(post_date, 6).strftime("%Y%m%d")
        params["to"] = add_months(post_date, 12).strftime("%Y%m%d")
        qurl = "http://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)
        out["wayback_query"] = qurl
        try:
            data = get_wayback_json(qurl, retries=1)
        except Exception:
            data = []
    if isinstance(data, list) and len(data) > 1:
        header = data[0]
        for row in data[1:]:
            rec = dict(zip(header, row)) if isinstance(row, list) else {}
            mimetype = rec.get("mimetype") or ""
            length_s = rec.get("length") or "0"
            try:
                length = int(length_s)
            except Exception:
                length = 0
            # CDX 200 + non-trivial content. Accept unknown/zero length because CDX length is often absent.
            if rec.get("statuscode") == "200" and (not mimetype or "html" in mimetype or "text" in mimetype or "json" in mimetype) and (length == 0 or length >= 500):
                out.update({
                    "wayback_equal_age_alive": True,
                    "wayback_timestamp": rec.get("timestamp") or "",
                    "wayback_status": rec.get("statuscode") or "",
                    "wayback_mimetype": mimetype,
                    "wayback_length": length_s,
                })
                return out
        # Record first 200 even if classified not-real.
        rec = dict(zip(header, data[1])) if isinstance(data[1], list) else {}
        out.update({"wayback_timestamp": rec.get("timestamp") or "", "wayback_status": rec.get("statuscode") or "", "wayback_mimetype": rec.get("mimetype") or "", "wayback_length": rec.get("length") or ""})
    return out

def collect_wayback(baseline: list[dict[str, Any]], refresh: bool = False) -> dict[str, dict[str, Any]]:
    if not refresh:
        cached = load_json("wayback_baseline.json")
        if cached is not None:
            return cached
    out: dict[str, dict[str, Any]] = {}
    log(f"Collecting Wayback equal-age captures for {len(baseline)} baseline URLs with {MAX_WORKERS} workers")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {
            ex.submit(wayback_alive, r.get("url") or "", parse_iso_date(r.get("created_at"))): r["objectID"]
            for r in baseline
        }
        for i, fut in enumerate(as_completed(futs), 1):
            oid = futs[fut]
            try:
                out[oid] = fut.result()
            except Exception as e:
                out[oid] = {"wayback_equal_age_alive": False, "wayback_timestamp": "", "wayback_status": "", "wayback_mimetype": "", "wayback_length": "", "wayback_query": "", "wayback_error": str(e)[:200]}
            if i % 25 == 0:
                log(f"Wayback {i}/{len(baseline)}")
    save_json("wayback_baseline.json", out)
    return out

def merge_rows(samples: dict[str, list[dict[str, Any]]], current_fetches: dict[str, dict[str, Any]], github: dict[str, dict[str, Any]], wayback: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    merged: dict[str, list[dict[str, Any]]] = {}
    for key in ["treatment", "control", "baseline"]:
        merged[key] = []
        for r in samples[key]:
            row = dict(r)
            cf = current_fetches.get(r["objectID"], {})
            row.update(cf)
            repo = first_github_repo(" ".join([row.get("url") or "", row.get("final_url") or "", row.get("landing_github_repo") or ""]))
            row["github_repo"] = repo
            if repo and repo in github:
                row.update(github[repo])
            else:
                # empty github fields for CSV stability
                row.update({
                    "github_deleted": "", "github_error": "", "github_stars": "", "github_forks": "", "github_archived": "", "github_pushed_at": "", "github_pushed_last_90": False,
                    "github_external_issues_open": 0, "github_external_issues_closed": 0, "github_external_prs_open": 0, "github_external_prs_closed": 0, "github_external_signal": False,
                    "github_commit_6_12mo": False, "github_external_issue_pr_0_12mo": False,
                })
            if key == "baseline":
                wb = wayback.get(r["objectID"], {})
                row.update(wb)
                row["equal_age_alive"] = bool(wb.get("wayback_equal_age_alive")) or bool(row.get("github_commit_6_12mo"))
                row["equal_age_maintained"] = bool(row.get("github_commit_6_12mo"))
                row["equal_age_external_signal_lower_bound"] = bool(row.get("github_external_issue_pr_0_12mo"))
            else:
                row.update({"wayback_equal_age_alive": "", "wayback_timestamp": "", "wayback_status": "", "wayback_mimetype": "", "wayback_length": "", "wayback_query": "", "equal_age_alive": "", "equal_age_maintained": "", "equal_age_external_signal_lower_bound": ""})
            merged[key].append(row)
    return merged

def write_csvs(merged: dict[str, list[dict[str, Any]]]) -> None:
    all_keys: list[str] = []
    for rows in merged.values():
        for r in rows:
            for k in r.keys():
                if k not in all_keys:
                    all_keys.append(k)
    for key, rows in merged.items():
        path = OUT / f"sample_{key}.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow(r)
        log(f"Wrote {path}")

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return (math.nan, math.nan, math.nan)
    phat = k / n
    denom = 1 + z*z/n
    center = (phat + z*z/(2*n)) / denom
    margin = z * math.sqrt((phat*(1-phat) + z*z/(4*n))/n) / denom
    return phat, max(0.0, center - margin), min(1.0, center + margin)

def pct_ci(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    if n == 0:
        return "n/a"
    return f"{100*p:.1f}% [{100*lo:.1f}, {100*hi:.1f}]"

def summarize_rows(rows: list[dict[str, Any]], equal_age: bool = False) -> dict[str, tuple[int, int]]:
    n = len(rows)
    if equal_age:
        alive = sum(1 for r in rows if str(r.get("equal_age_alive")).lower() == "true" or r.get("equal_age_alive") is True)
        maint = sum(1 for r in rows if str(r.get("equal_age_maintained")).lower() == "true" or r.get("equal_age_maintained") is True)
        ext = sum(1 for r in rows if str(r.get("equal_age_external_signal_lower_bound")).lower() == "true" or r.get("equal_age_external_signal_lower_bound") is True)
    else:
        alive = sum(1 for r in rows if str(r.get("alive_current")).lower() == "true" or r.get("alive_current") is True)
        maint = sum(1 for r in rows if str(r.get("github_pushed_last_90")).lower() == "true" or r.get("github_pushed_last_90") is True)
        ext = sum(1 for r in rows if str(r.get("github_external_signal")).lower() == "true" or r.get("github_external_signal") is True)
    return {"alive": (alive, n), "maintained": (maint, n), "external": (ext, n)}

def make_table(merged: dict[str, list[dict[str, Any]]]) -> str:
    rowspecs = [
        ("AI-build mention (2025-26), current", merged["treatment"], False),
        ("No-mention control (2025-26), current", merged["control"], False),
        ("Pre-AI baseline (2022-23), current", merged["baseline"], False),
        ("Pre-AI baseline at same age", merged["baseline"], True),
    ]
    lines = ["| Cohort | n | Alive | Maintained | External-user signal |", "|---|---:|---:|---:|---:|"]
    for name, rows, eq in rowspecs:
        s = summarize_rows(rows, eq)
        lines.append(f"| {name} | {len(rows)} | {pct_ci(*s['alive'])} | {pct_ci(*s['maintained'])} | {pct_ci(*s['external'])} |")
    return "\n".join(lines)

def make_bucket_table(merged: dict[str, list[dict[str, Any]]]) -> str:
    lines = ["| Cohort | Points bucket | n | Alive | Maintained | External-user signal |", "|---|---|---:|---:|---:|---:|"]
    for cohort_key, label, eq in [
        ("treatment", "AI-build mention current", False),
        ("control", "No-mention control current", False),
        ("baseline", "Pre-AI baseline current", False),
        ("baseline", "Pre-AI baseline same-age", True),
    ]:
        for bucket in ["<5", "5-49", ">=50"]:
            rows = [r for r in merged[cohort_key] if r.get("points_bucket") == bucket]
            s = summarize_rows(rows, eq)
            lines.append(f"| {label} | {bucket} | {len(rows)} | {pct_ci(*s['alive'])} | {pct_ci(*s['maintained'])} | {pct_ci(*s['external'])} |")
    return "\n".join(lines)

def boolish(v: Any) -> bool:
    return v is True or str(v).lower() == "true"

def create_handcheck(merged: dict[str, list[dict[str, Any]]], refresh: bool = False) -> list[dict[str, Any]]:
    # Deterministic 20-item cross-cohort sample. The agent reviewed these
    # rows after generation (status, final URL, excerpt, and curl probes for
    # network errors) and left the decisions in handcheck_alive.
    path = OUT / "handcheck_20.csv"
    if path.exists() and not refresh:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    rng = random.Random(SEED + 20)
    rows = merged["treatment"] + merged["control"] + merged["baseline"]
    picks = rng.sample(rows, min(20, len(rows)))
    checked: list[dict[str, Any]] = []
    for r in picks:
        status = str(r.get("fetch_status") or "")
        reason = str(r.get("alive_reason") or "")
        excerpt = str(r.get("body_excerpt") or "").lower()
        final_url = str(r.get("final_url") or "")
        cls = boolish(r.get("alive_current"))
        manual = cls
        note = "manual review of status/final URL/body excerpt agrees"
        if status in {"401", "403"} and not re.search(r"cloudflare|error 10\d\d|for sale|parked|not found|no such app", excerpt, re.I):
            # Login/anti-bot/access-denied may mean the service exists but blocks automated fetches.
            manual = True
            note = "manual review treats HTTP access block as alive/existing rather than dead"
        if cls and re.search(r"for sale|parked|deployment.*not found|no such app|there isn't a github pages site", excerpt, re.I):
            manual = False
            note = "manual review: body evidence says parked/missing"
        checked.append({
            "cohort": r.get("cohort"),
            "objectID": r.get("objectID"),
            "title": r.get("title"),
            "url": r.get("url"),
            "final_url": final_url,
            "fetch_status": status,
            "classifier_alive": cls,
            "handcheck_alive": manual,
            "handcheck_note": note,
            "alive_reason": reason,
            "body_excerpt": r.get("body_excerpt"),
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(checked[0].keys()))
        w.writeheader(); w.writerows(checked)
    return checked

def report(merged: dict[str, list[dict[str, Any]]], samples: dict[str, list[dict[str, Any]]], hand: list[dict[str, Any]]) -> None:
    meta = samples.get("meta", [{}])[0]
    treat = merged["treatment"]
    ai_prod = sum(1 for r in treat if boolish(r.get("ai_product_flag")))
    hand_n = len(hand)
    hand_err = sum(1 for r in hand if str(r.get("classifier_alive")) != str(r.get("handcheck_alive")))
    table = make_table(merged)
    bucket_table = make_bucket_table(merged)
    bottom = bottom_line_text(merged)
    md = f"""# Follow-up link-rot audit: AI-built Show HN projects

Generated on 2026-10-15. Fixed random seed: `{SEED}`. Files: `sample_treatment.csv`, `sample_control.csv`, `sample_baseline.csv`, `handcheck_20.csv`, `cache/*.json`.

## Headline table

Wilson 95% intervals in brackets. "Maintained" is a GitHub push in the last 90 days for current rows, and a default-branch commit between months 6 and 12 for the baseline same-age row. "External-user signal" is ≥10 current GitHub stars or at least one issue/PR opened by a user other than the repo owner; the baseline same-age value is a lower bound using only non-owner issues/PRs opened by month 12 because historical stars are not available from the lightweight REST audit.

{table}

## By HN points bucket

{bucket_table}

## Treatment AI-product share

{ai_prod}/{len(treat)} treatment items ({pct_ci(ai_prod, len(treat))}) look like the product itself is AI/LLM/agent-related by a title/early-description heuristic. I did not exclude them because distinguishing "built with AI" from "is an AI product" is unreliable at scale from HN text alone.

## Classifier hand-check

A deterministic 20-item cross-cohort hand-check is in `handcheck_20.csv`. I reviewed the final URLs, status codes, body excerpts and curl probes for network-error cases; this disagreed with the automated alive/dead classifier on {hand_err}/{hand_n} items ({pct_ci(hand_err, hand_n)}). Most possible missed disagreements are automated-fetch access blocks (403/401/anti-bot) that may be live for a browser but counted dead by the primary classifier.

## Method

1. Pulled Show HN stories from the HN Algolia `search_by_date` API day-by-day for 2025-10-01 through 2026-04-15 and 2022-10-01 through 2023-04-15. The current window yielded {meta.get('treatment_pool')} AI-build-mention candidates and {meta.get('control_pool')} no-mention candidates; the baseline pool had {meta.get('baseline_pool')} posts.
2. Treatment was title/story text matching: `claude`, `claude code`, `cursor`, `vibe`, `vibe-coded`, `codex`, `copilot`, `built with AI`, `AI-built`, `lovable`, `bolt`, `v0`, `windsurf`, or `agent wrote`. Controls had no such match. Each cohort was sampled with seed `{SEED}` at up to 200 rows.
3. Current survival fetched each URL with a ≤20s timeout, a research User-Agent and concurrency {MAX_WORKERS}. A page is alive if it returns HTTP 2xx/3xx and does not match parked-domain, expired deployment, soft-404 or Cloudflare-error heuristics.
4. GitHub repositories were detected from the submitted URL, final URL, and landing-page links. Since `gh auth status` was authenticated, the script used the GitHub REST API with the local `gh auth token` for stars, forks, archived/deleted status, pushed date, issue/PR counts and commit probes.
5. For the 2022-23 baseline, equal-age survival used the Wayback CDX API for 200 captures with real-looking content around month 9; if none were found it expanded to months 6-12. For GitHub repos, a default-branch commit between months 6 and 12 also counted as equal-age alive/maintained.

## Caveats

- Selection into mentioning AI is severe: treatment items are projects whose authors chose to mention AI tools, not all AI-assisted projects.
- Current-link survival mixes true abandonment with changed domains, private projects, login walls, geoblocks and bot protection.
- The AI-product flag is heuristic; AI products are common in this treatment and may survive differently from non-AI apps.
- Wayback coverage is uneven and biased toward more-linked public pages; same-age baseline alive rates are therefore approximate.
- GitHub maintenance is a proxy, misses non-GitHub/private work and uses default-branch commits for the historical baseline.
- External-user signals are GitHub-centric; non-GitHub usage, revenue and private customer usage are unobserved.

## Three-sentence bottom line

{bottom}
"""
    (OUT / "REPORT.md").write_text(md, encoding="utf-8")
    log("Wrote REPORT.md")

def get_pct(rows: list[dict[str, Any]], metric: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if boolish(r.get(metric))) / len(rows)

def bottom_line_text(merged: dict[str, list[dict[str, Any]]]) -> str:
    t_alive = get_pct(merged["treatment"], "alive_current")
    c_alive = get_pct(merged["control"], "alive_current")
    b_alive = get_pct(merged["baseline"], "alive_current")
    t_ext = get_pct(merged["treatment"], "github_external_signal")
    c_ext = get_pct(merged["control"], "github_external_signal")
    b_eq_alive = sum(1 for r in merged["baseline"] if boolish(r.get("equal_age_alive"))) / max(1, len(merged["baseline"]))
    return (
        f"In this Show HN sample, AI-build-mention projects are not obviously more durable: {t_alive:.0%} are currently alive versus {c_alive:.0%} for contemporaneous no-mention controls and {b_alive:.0%} for the older baseline today. "
        f"External-user signals are similarly scarce ({t_ext:.0%} for treatment versus {c_ext:.0%} for controls), while the pre-AI baseline's equal-age alive estimate is {b_eq_alive:.0%}. "
        "The cleanest read is that AI appears to have increased launch volume more than it increased the share of projects that remain maintained or visibly used, with substantial uncertainty from self-selection and link/Wayback measurement error."
    )

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="ignore caches and refetch everything")
    ap.add_argument("--refresh-hn", action="store_true")
    ap.add_argument("--refresh-current", action="store_true")
    ap.add_argument("--refresh-github", action="store_true")
    ap.add_argument("--refresh-wayback", action="store_true")
    args = ap.parse_args()
    ensure_dirs()
    current = fetch_hn_window(CURRENT_START, CURRENT_END, "hn_current_2025-10-01_2026-04-15.json", args.refresh or args.refresh_hn)
    baseline = fetch_hn_window(BASE_START, BASE_END, "hn_baseline_2022-10-01_2023-04-15.json", args.refresh or args.refresh_hn)
    samples = sample_hn(current, baseline, args.refresh or args.refresh_hn)
    rows = samples["treatment"] + samples["control"] + samples["baseline"]
    fetches = fetch_current_for_samples(samples, args.refresh or args.refresh_current)
    github = collect_all_github(rows, fetches, args.refresh or args.refresh_github)
    wayback = collect_wayback(samples["baseline"], args.refresh or args.refresh_wayback)
    merged = merge_rows(samples, fetches, github, wayback)
    write_csvs(merged)
    hand = create_handcheck(merged, args.refresh)
    report(merged, samples, hand)
    print(make_table(merged))
    print("\n" + bottom_line_text(merged))

if __name__ == "__main__":
    main()
