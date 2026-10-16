#!/usr/bin/env python3
import csv, datetime as dt, hashlib, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path.home() / "Code/where-is-the-software/stalled-projects"
DATA = ROOT / "data"
CACHE = DATA / "cache_github_search"
CACHE.mkdir(parents=True, exist_ok=True)

REPOS = [
    "microsoft/vscode", "rust-lang/rust", "golang/go", "kubernetes/kubernetes", "flutter/flutter",
    "godotengine/godot", "home-assistant/core", "neovim/neovim", "microsoft/TypeScript",
    "nodejs/node", "electron/electron", "bevyengine/bevy", "python/cpython", "react/react", "ansible/ansible",
]
TOP_REPOS = ["microsoft/vscode", "rust-lang/rust", "golang/go", "godotengine/godot", "flutter/flutter", "home-assistant/core"]

START = dt.date(2022,1,1)
END_EXCL = dt.date(2026,10,1)


def gh_token():
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception as e:
        print(f"could not get gh token: {e}", file=sys.stderr)
        return None
TOKEN = gh_token()

last_request_at = 0.0

def request_json(url, cache_key, min_interval=2.15):
    global last_request_at
    p = CACHE / (hashlib.sha1(cache_key.encode()).hexdigest() + ".json")
    if p.exists():
        return json.loads(p.read_text())
    elapsed = time.time() - last_request_at
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "stalled-projects-research"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    while True:
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                last_request_at = time.time()
                data = json.loads(resp.read())
                p.write_text(json.dumps(data, indent=2, sort_keys=True))
                return data
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            if e.code in (403, 429):
                wait = 65
                print(f"rate limited; sleeping {wait}s for {url}: {body[:200]}", file=sys.stderr)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code} {url}: {body[:500]}")


def search_count(q):
    params = urllib.parse.urlencode({"q": q, "per_page": 1})
    data = request_json(f"https://api.github.com/search/issues?{params}", "count:"+q)
    return int(data.get("total_count", 0))


def search_items(q, per_page=50, sort=None, order="desc"):
    params = {"q": q, "per_page": per_page}
    if sort:
        params["sort"] = sort
        params["order"] = order
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(params)
    data = request_json(url, "items:"+json.dumps(params, sort_keys=True))
    return data.get("items", [])


def quarter_starts(start, end_excl):
    y, m = start.year, ((start.month-1)//3)*3 + 1
    d = dt.date(y, m, 1)
    while d < end_excl:
        nm = d.month + 3
        ny = d.year + (nm-1)//12
        nm = ((nm-1)%12)+1
        nxt = dt.date(ny, nm, 1)
        yield d, min(nxt, end_excl)
        d = nxt


def iso(d): return d.isoformat()
def minus_years(d, n):
    try:
        return d.replace(year=d.year-n)
    except ValueError:
        return d.replace(year=d.year-n, day=28)

def qlabel(start): return f"{start.year}Q{((start.month-1)//3)+1}"


def collect_closures():
    rows = []
    mass_rows = []
    for repo in REPOS:
        print(f"repo {repo}", file=sys.stderr, flush=True)
        for qs, qe in quarter_starts(START, END_EXCL):
            end_inc = qe - dt.timedelta(days=1)
            closed_range = f"{iso(qs)}..{iso(end_inc)}"
            old_cutoff = minus_years(qs, 3)
            base = f"repo:{repo} is:issue reason:completed closed:{closed_range}"
            denom = search_count(base)
            oldq = base + f" created:<{iso(old_cutoff)}"
            old = search_count(oldq)
            adj_old = old
            adj_denom = denom
            flagged = []
            if old >= 1000:
                # Check for one-day mass triage bursts among old issues.
                d = qs
                daily = []
                while d < qe:
                    dq = f"repo:{repo} is:issue reason:completed closed:{iso(d)}..{iso(d)} created:<{iso(old_cutoff)}"
                    c = search_count(dq)
                    if c:
                        daily.append((d, c))
                    d += dt.timedelta(days=1)
                for d, c in daily:
                    if c >= max(500, int(old * 0.30)):
                        denom_day = search_count(f"repo:{repo} is:issue reason:completed closed:{iso(d)}..{iso(d)}")
                        adj_old -= c
                        adj_denom -= denom_day
                        sample = search_items(f"repo:{repo} is:issue reason:completed closed:{iso(d)}..{iso(d)} created:<{iso(old_cutoff)}", per_page=5)
                        flagged.append(iso(d))
                        mass_rows.append({
                            "repo": repo, "quarter": qlabel(qs), "date": iso(d), "old_completed_count": c,
                            "all_completed_count": denom_day, "sample_titles": " | ".join(i.get("title", "") for i in sample),
                            "sample_urls": " | ".join(i.get("html_url", "") for i in sample),
                        })
            rows.append({
                "repo": repo, "quarter": qlabel(qs), "start": iso(qs), "end": iso(end_inc),
                "old_cutoff_created_before": iso(old_cutoff),
                "completed_old_ge3y": old, "completed_all": denom,
                "adjusted_completed_old_ge3y": adj_old, "adjusted_completed_all": adj_denom,
                "old_share": (old/denom if denom else ""),
                "adjusted_old_share": (adj_old/adj_denom if adj_denom else ""),
                "excluded_mass_cleanup_dates": ";".join(flagged),
                "query_old": oldq, "query_all": base,
            })
    out = DATA / "github_old_issue_closures_quarterly.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    mout = DATA / "github_mass_cleanup_events.csv"
    with mout.open("w", newline="") as f:
        fields = ["repo","quarter","date","old_completed_count","all_completed_count","sample_titles","sample_urls"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(mass_rows)
    print(f"wrote {out} and {mout}")


def collect_top_issues():
    rows = []
    for repo in TOP_REPOS:
        print(f"top issues {repo}", file=sys.stderr, flush=True)
        items = search_items(f"repo:{repo} is:issue", per_page=50, sort="reactions-+1", order="desc")
        for rank, it in enumerate(items, 1):
            rows.append({
                "repo": repo, "rank": rank, "number": it.get("number"), "title": it.get("title"),
                "url": it.get("html_url"), "state": it.get("state"), "state_reason": it.get("state_reason"),
                "created_at": it.get("created_at"), "closed_at": it.get("closed_at"),
                "plus_one": (it.get("reactions") or {}).get("+1"),
                "total_reactions": (it.get("reactions") or {}).get("total_count"),
                "comments": it.get("comments"), "user": (it.get("user") or {}).get("login"),
            })
    out = DATA / "github_top_reacted_issues.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    # hazard by year
    hrows = []
    for repo in TOP_REPOS:
        subset = [r for r in rows if r["repo"] == repo]
        for year in range(2022, 2027):
            start = dt.datetime(year,1,1,tzinfo=dt.timezone.utc)
            end = dt.datetime(year+1,1,1,tzinfo=dt.timezone.utc) if year < 2026 else dt.datetime(2026,10,1,tzinfo=dt.timezone.utc)
            at_risk = 0; completed = 0
            for r in subset:
                created = dt.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
                closed = dt.datetime.fromisoformat(r["closed_at"].replace("Z", "+00:00")) if r["closed_at"] else None
                if created < start and (closed is None or closed >= start):
                    at_risk += 1
                    if closed and start <= closed < end and r["state_reason"] == "completed":
                        completed += 1
            hrows.append({"repo":repo,"year":year,"top50_at_risk_start":at_risk,"closed_completed_during_year":completed,"hazard":(completed/at_risk if at_risk else "")})
    hout = DATA / "github_top_reacted_hazard.csv"
    with hout.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hrows[0].keys()))
        w.writeheader(); w.writerows(hrows)
    print(f"wrote {out} and {hout}")


def collect_spotcheck():
    rows=[]
    for repo in REPOS:
        q = f"repo:{repo} is:issue reason:completed closed:2025-01-01..2026-09-30 created:<2022-01-01"
        for it in search_items(q, per_page=5, sort="updated", order="desc"):
            rows.append({
                "repo":repo,"number":it.get("number"),"title":it.get("title"),"url":it.get("html_url"),
                "created_at":it.get("created_at"),"closed_at":it.get("closed_at"),"state_reason":it.get("state_reason"),
                "labels":";".join(l.get("name","") for l in it.get("labels",[])),"comments":it.get("comments")
            })
    out=DATA/"github_old_issue_spotcheck.csv"
    with out.open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"wrote {out}")

if __name__ == "__main__":
    collect_closures()
    collect_top_issues()
    collect_spotcheck()
