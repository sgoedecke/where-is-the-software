#!/usr/bin/env python3
"""Nexus Mods category-cohort fetch for the niche-usage study.

Uses Nexus' public GraphQL v2 API, caches all responses under this output folder,
and writes CSVs plus REPORT.md. No API key is required for the fields used here.
"""
from __future__ import annotations

import csv, datetime as dt, hashlib, json, re, time, urllib.request, urllib.error
from pathlib import Path

API = "https://api.nexusmods.com/v2/graphql"
UA = "where-is-the-software-niche-study/1.0 (Nexus cohort research; polite cached script)"
BASE = Path(__file__).resolve().parent
CACHE = BASE / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
TODAY = dt.datetime(2026, 10, 15, 6, 41, 44, tzinfo=dt.timezone.utc)
GAMES = {
    "skyrimspecialedition": "Skyrim Special Edition",
    "stardewvalley": "Stardew Valley",
    "cyberpunk2077": "Cyberpunk 2077",
    "baldursgate3": "Baldur's Gate 3",
    "fallout4": "Fallout 4",
}

SCHEMA_QUERY = """
query IntrospectionLite {
  query: __schema { queryType { fields { name args { name type { kind name ofType { kind name ofType { kind name } } } } } } }
  modsFilter: __type(name:"ModsFilter") { inputFields { name type { kind name ofType { kind name ofType { kind name } } } } }
  modsSort: __type(name:"ModsSort") { inputFields { name type { kind name ofType { kind name ofType { kind name } } } } }
  modType: __type(name:"Mod") { fields { name type { kind name ofType { kind name ofType { kind name } } } } }
}
"""
FACET_QUERY = """
query Facets($game: String!) {
  mods(filter:{gameDomainName:[{value:$game}]}, facets:{categoryName:["categoryName"], tag:["tag"]}, count:1) {
    facets { facet value count }
  }
}
"""
GAME_QUERY = "query Game($game:String!){ game(domainName:$game){ id name domainName modCount downloadCount uniqueDownloadCount } }"

last_request = 0.0

def cname(prefix: str, payload: object) -> Path:
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:20]
    return CACHE / f"{prefix}_{h}.json"

def gql(query: str, variables: dict | None = None, prefix: str = "q") -> dict:
    global last_request
    variables = variables or {}
    payload = {"query": query, "variables": variables}
    path = cname(prefix, payload)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    wait = 0.08 - (time.time() - last_request)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json", "User-Agent":UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
            last_request = time.time()
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return data
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt); continue
            raise RuntimeError(f"HTTP {e.code}: {body[:500]}") from e
        except Exception:
            if attempt < 3:
                time.sleep(2 ** attempt); continue
            raise
    raise AssertionError

def epoch(d: dt.datetime) -> str: return str(int(d.timestamp()))

def half_years():
    for y in range(2021, 2027):
        starts = [(f"{y}H1", dt.datetime(y,1,1,tzinfo=dt.timezone.utc), dt.datetime(y,7,1,tzinfo=dt.timezone.utc)),
                  (f"{y}H2", dt.datetime(y,7,1,tzinfo=dt.timezone.utc), dt.datetime(y+1,1,1,tzinfo=dt.timezone.utc))]
        for label, s, e in starts:
            if s < TODAY:
                yield label, s, min(e, TODAY), TODAY < e

CODE_CAT = re.compile(r"\b(utilities|utility|modding tools|modders resources|resources|scripts|patches|bug fixes|user interface|gameplay mechanics|gameplay|cheats|performance|perks|skills and leveling|combat|spells|classes|crafting|framework|library|tools)\b", re.I)
ASSET_CAT = re.compile(r"\b(armou?r|weapons?|clothing|body|face|hair|models?|textures?|visuals?|graphics|appearance|characters?|character customisation|presets?|audio|sfx|music|voice|portraits?|maps?|locations?|buildings?|interiors|furniture|livestock|animals|pets|horses|crops|items|equipment|accessories|dice|vehicles?|animation|animations|weather|lighting|enb|reshade|tattoos?|poses|icons?)\b", re.I)

def class_for_category(cat: str) -> str:
    # Asset-heavy categories win when both regexes match (e.g. Weapons and Armour).
    if ASSET_CAT.search(cat): return "asset_only"
    if CODE_CAT.search(cat): return "code_tool"
    return "other_mixed"

def gql_str(s: str) -> str:
    return json.dumps(s)

def field_filter(field: str, values: list[str]) -> str:
    if not values:
        return "{modId:[{value:\"__no_such_mod__\"}]}"
    parts = ["{" + field + ":[{value:" + gql_str(v) + "}]}" for v in values]
    return parts[0] if len(parts) == 1 else "{op:OR, filter:[" + ",".join(parts) + "]}"

def range_filter(metric: str | None = None, threshold: int | None = None, class_filter: str | None = None, ai_filter: str | None = None) -> str:
    parts = ["{gameDomainName:[{value:$game}]}", "{createdAt:[{value:$start,op:GTE},{value:$end,op:LT}]}" ]
    if class_filter: parts.append(class_filter)
    if ai_filter: parts.append(ai_filter)
    if metric: parts.append("{" + metric + ":[{value:" + str(threshold) + ",op:GTE}]}")
    return "{op:AND, filter:[" + ",".join(parts) + "]}"

def count_query(class_filter: str, ai_filter: str | None = None) -> str:
    aliases = {
        "n": range_filter(class_filter=class_filter, ai_filter=ai_filter),
        "dl100": range_filter("downloads", 100, class_filter, ai_filter),
        "dl1000": range_filter("downloads", 1000, class_filter, ai_filter),
        "dl10000": range_filter("downloads", 10000, class_filter, ai_filter),
        "end10": range_filter("endorsements", 10, class_filter, ai_filter),
        "end100": range_filter("endorsements", 100, class_filter, ai_filter),
    }
    body = "\n".join(f"{a}: mods(filter:{flt}, count:0) {{ totalCount }}" for a, flt in aliases.items())
    return "query Counts($game:String!, $start:String!, $end:String!){\n" + body + "\n}"

def top_query(class_filter: str) -> str:
    flt = range_filter(class_filter=class_filter)
    return "query Top($game:String!, $start:String!, $end:String!){ mods(filter:" + flt + ", sort:[{downloads:{direction:DESC}}], count:12){ nodes { modId gameId name createdAt updatedAt downloads endorsements category author summary tags { name } } } }"

def detail_query() -> str:
    return "query Detail($modId:ID!, $gameId:ID!){ mod(modId:$modId, gameId:$gameId){ modId gameId name description summary category author downloads endorsements createdAt tags { name } } }"

def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"]*len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c,"")) for c in cols) + " |")
    return "\n".join(out)

def main():
    schema = gql(SCHEMA_QUERY, prefix="schema")
    (BASE / "schema_introspection_lite.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    mod_fields = {f["name"] for f in schema.get("data",{}).get("modType",{}).get("fields",[])}
    filter_fields = {f["name"] for f in schema.get("data",{}).get("modsFilter",{}).get("inputFields",[])}
    sort_fields = {f["name"] for f in schema.get("data",{}).get("modsSort",{}).get("inputFields",[])}

    game_meta, cat_rows, class_filters, ai_filter = {}, [], {}, field_filter("tag", ["AI-Generated Content", "AI Assisted", "AI Media"])
    tag_rows = []
    for domain, game_name in GAMES.items():
        game_meta[domain] = gql(GAME_QUERY, {"game":domain}, f"game_{domain}").get("data",{}).get("game") or {}
        facets = gql(FACET_QUERY, {"game":domain}, f"facets_{domain}").get("data",{}).get("mods",{}).get("facets",[])
        cats = sorted({f["value"] for f in facets if f["facet"] == "categoryName"})
        tags = sorted({f["value"] for f in facets if f["facet"] == "tag"})
        for c in cats:
            cat_rows.append({"game_domain":domain, "game":game_name, "category":c, "class":class_for_category(c)})
        for t in tags:
            if re.search(r"AI|Generated|SMAPI|SKSE|F4SE|Script|RED|CET|Code|Framework", t, re.I):
                tag_rows.append({"game_domain":domain, "game":game_name, "tag":t})
        class_filters[domain] = {
            klass: field_filter("categoryName", [c for c in cats if class_for_category(c) == klass])
            for klass in ["code_tool", "asset_only", "other_mixed"]
        }
    with (BASE/"category_classification.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["game_domain","game","category","class"]); w.writeheader(); w.writerows(cat_rows)
    with (BASE/"notable_tags.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["game_domain","game","tag"]); w.writeheader(); w.writerows(tag_rows)

    rows = []
    for domain, game_name in GAMES.items():
        for cohort, start, end, partial in half_years():
            for klass in ["code_tool", "asset_only", "other_mixed"]:
                q = count_query(class_filters[domain][klass])
                data = gql(q, {"game":domain, "start":epoch(start), "end":epoch(end)}, f"counts_{domain}_{cohort}_{klass}")
                if data.get("errors"):
                    raise RuntimeError(json.dumps(data["errors"], indent=2)[:1000])
                d = data["data"]
                n = d["n"]["totalCount"]
                rows.append({
                    "game_domain":domain, "game":game_name, "cohort":cohort, "cohort_partial":"yes" if partial else "no", "class":klass,
                    "still_listed_n":n,
                    "downloads_ge_100_n":d["dl100"]["totalCount"],
                    "downloads_ge_100_share":round(d["dl100"]["totalCount"]/n,4) if n else 0,
                    "downloads_ge_1000_n":d["dl1000"]["totalCount"],
                    "downloads_ge_1000_share":round(d["dl1000"]["totalCount"]/n,4) if n else 0,
                    "downloads_ge_10000_n":d["dl10000"]["totalCount"],
                    "downloads_ge_10000_share":round(d["dl10000"]["totalCount"]/n,4) if n else 0,
                    "endorsements_ge_10_n":d["end10"]["totalCount"],
                    "endorsements_ge_10_share":round(d["end10"]["totalCount"]/n,4) if n else 0,
                    "endorsements_ge_100_n":d["end100"]["totalCount"],
                    "endorsements_ge_100_share":round(d["end100"]["totalCount"]/n,4) if n else 0,
                })
            print(domain, cohort, "done", flush=True)
    with (BASE/"cohorts_by_game_class.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    agg = []
    for cohort, partial in sorted({(r["cohort"], r["cohort_partial"]) for r in rows}):
        for klass in ["code_tool", "asset_only", "other_mixed"]:
            subset = [r for r in rows if r["cohort"]==cohort and r["class"]==klass]
            n = sum(r["still_listed_n"] for r in subset)
            a = {"cohort":cohort, "cohort_partial":partial, "class":klass, "still_listed_n":n}
            for field in ["downloads_ge_100_n","downloads_ge_1000_n","downloads_ge_10000_n","endorsements_ge_10_n","endorsements_ge_100_n"]:
                a[field] = sum(r[field] for r in subset)
                a[field.replace("_n","_share")] = round(a[field]/n,4) if n else 0
            agg.append(a)
    with (BASE/"cohorts_aggregate.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(agg[0].keys())); w.writeheader(); w.writerows(agg)

    # AI tag share in recent code/tool category cohorts.
    ai_rows = []
    recent_start = dt.datetime(2025,7,1,tzinfo=dt.timezone.utc)
    for domain, game_name in GAMES.items():
        base_q = count_query(class_filters[domain]["code_tool"])
        ai_q = count_query(class_filters[domain]["code_tool"], ai_filter=ai_filter)
        vals = {"game":domain, "start":epoch(recent_start), "end":epoch(TODAY)}
        total = gql(base_q, vals, f"ai_total_{domain}")["data"]["n"]["totalCount"]
        ai = gql(ai_q, vals, f"ai_tags_{domain}")["data"]["n"]["totalCount"]
        ai_rows.append({"period":"2025H2-2026YTD", "game":game_name, "class":"code_tool", "n":total, "ai_tagged_n":ai, "ai_tagged_share":round(ai/total,4) if total else 0})
    alln, allai = sum(r["n"] for r in ai_rows), sum(r["ai_tagged_n"] for r in ai_rows)
    ai_rows.append({"period":"2025H2-2026YTD", "game":"ALL", "class":"code_tool", "n":alln, "ai_tagged_n":allai, "ai_tagged_share":round(allai/alln,4) if alln else 0})
    with (BASE/"ai_tag_share.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(ai_rows[0].keys())); w.writeheader(); w.writerows(ai_rows)

    # Top recent code/tool mods by current downloads.
    top = []
    for domain, game_name in GAMES.items():
        data = gql(top_query(class_filters[domain]["code_tool"]), {"game":domain, "start":epoch(recent_start), "end":epoch(TODAY)}, f"top_{domain}")
        if data.get("errors"):
            raise RuntimeError(json.dumps(data["errors"], indent=2)[:1000])
        for m in data["data"]["mods"]["nodes"]:
            top.append({"game_domain":domain, "game":game_name, **m, "url":f"https://www.nexusmods.com/{domain}/mods/{m['modId']}"})
    top = sorted(top, key=lambda m:(m["downloads"], m["endorsements"]), reverse=True)[:12]
    detailed = []
    ai_re = re.compile(r"\b(AI[- ]?Generated Content|AI Assisted|AI Media|made with AI|created with AI|generated by AI|ChatGPT|Claude|Copilot|Midjourney|Stable Diffusion)\b", re.I)
    established_re = re.compile(r"\b(port|reupload|redux|continued|update|updated|conversion|converted|backport|next-gen|revived|remake|reborn|successor|framework|library|extension|script extender)\b", re.I)
    for m in top:
        detail = gql(detail_query(), {"modId":str(m["modId"]), "gameId":str(m["gameId"])}, f"detail_{m['game_domain']}_{m['modId']}").get("data",{}).get("mod") or {}
        desc = re.sub(r"<[^>]+>", " ", detail.get("description") or "")[:2500]
        tags = ", ".join(t["name"] for t in m.get("tags") or [])
        text = " | ".join([m.get("name") or "", m.get("summary") or "", tags, desc])
        detailed.append({
            "game":m["game"], "cohort":"2025H2-2026YTD", "mod_id":m["modId"], "name":m["name"], "author":m.get("author") or "", "category":m.get("category") or "",
            "downloads_current_total":m["downloads"], "endorsements_current":m["endorsements"], "tags":tags, "url":m["url"],
            "origin_judgement":"likely established/port/update/framework" if established_re.search(text) else "appears newly listed",
            "ai_judgement":"explicit AI-assisted/generated tag/text found" if ai_re.search(text) else "no explicit AI-built claim found",
            "summary":m.get("summary") or "",
        })
    with (BASE/"recent_top_code_mods.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(detailed[0].keys())); w.writeheader(); w.writerows(detailed)

    write_report(agg, rows, detailed, ai_rows, mod_fields, filter_fields, sort_fields)
    print("Wrote report and CSVs under", BASE)

def write_report(agg, rows, top, ai_rows, mod_fields, filter_fields, sort_fields):
    condensed=[]
    for r in agg:
        if r["class"] in ("code_tool","asset_only"):
            condensed.append({"cohort":r["cohort"]+("*" if r["cohort_partial"]=="yes" else ""), "class":r["class"], "N":r["still_listed_n"], ">=100 dl":r["downloads_ge_100_n"], ">=1k dl":r["downloads_ge_1000_n"], ">=10k dl":r["downloads_ge_10000_n"], ">=10 end":r["endorsements_ge_10_n"], ">=100 end":r["endorsements_ge_100_n"]})
    baseline=[f"{y}H{h}" for y in range(2022,2025) for h in (1,2)]
    recent=["2025H2","2026H1"]
    def avg(klass, cohorts, field):
        xs=[r[field] for r in agg if r["class"]==klass and r["cohort"] in cohorts]
        return sum(xs)/len(xs) if xs else 0
    code_base, code_rec = avg("code_tool",baseline,"still_listed_n"), avg("code_tool",recent,"still_listed_n")
    asset_base, asset_rec = avg("asset_only",baseline,"still_listed_n"), avg("asset_only",recent,"still_listed_n")
    code_10k_base, code_10k_rec = avg("code_tool",baseline,"downloads_ge_10000_n"), avg("code_tool",recent,"downloads_ge_10000_n")

    top_md=[{"game":t["game"], "mod":f"[{t['name']}]({t['url']})", "downloads":t["downloads_current_total"], "end":t["endorsements_current"], "category":t["category"], "origin":t["origin_judgement"], "AI":t["ai_judgement"]} for t in top[:10]]
    unique_note = "`uniqueDownloads` appears as a sort input but not as a `Mod` field or `ModsFilter`; the public unauthenticated API exposes `downloads`, so thresholds below use current cumulative total downloads rather than unique downloads."
    if "uniqueDownloads" in mod_fields:
        unique_note = "`uniqueDownloads` was exposed and used."
    report = [
        "# Nexus Mods niche usage cohorts", "",
        "Source folder: `nexus`. Games: Skyrim Special Edition, Stardew Valley, Cyberpunk 2077, Baldur's Gate 3, and Fallout 4.", "",
        "## Cohort table (selected games combined)", "",
        "Counts are public still-listed mods created in each half-year. `2026H2*` is partial through 2026-10-15. Download counters are current cumulative totals, so older cohorts are age-advantaged.", "",
        md_table(condensed, ["cohort","class","N",">=100 dl",">=1k dl",">=10k dl",">=10 end",">=100 end"]), "",
        "Full per-game rows are in `cohorts_by_game_class.csv`; combined rows are in `cohorts_aggregate.csv`.", "",
        "## Method", "",
        "I introspected `https://api.nexusmods.com/v2/graphql`, then queried `mods` by `gameDomainName`, `createdAt` epoch-second ranges, category filters and threshold filters. Each cohort/class request batched six counts (`N`, three download thresholds, two endorsement thresholds) into one GraphQL call; responses are cached under `cache/` with a fixed User-Agent and pacing. Removed/hidden mods are not recoverable from the public listing, so `N` means still listed. " + unique_note, "",
        "Classification is category-based and reproducible in `category_classification.csv`: utility/tool/framework/script/patch/bug-fix/UI/gameplay categories are `code_tool`; texture/model/preset/armour/clothing/appearance/audio/location/weapon/equipment categories are `asset_only`; other categories are kept as `other_mixed` in the CSVs. This deliberately separates code/tool-like mod work from asset-heavy categories, but many mods are mixed.", "",
        "I did not use Wayback for the cohort table: Nexus pages are dynamic and CDX snapshots do not expose reliable download counters at scale. Therefore recent cohorts beating older cohorts is robust, while recent cohorts trailing older ones is inconclusive.", "",
        "## Top recent code/tool mods", "", md_table(top_md, ["game","mod","downloads","end","category","origin","AI"]), "",
        "## AI-assisted tag share", "",
        "The public facets expose tags including `AI-Generated Content`, `AI Assisted`, and `AI Media`; the table reports the share of recent code/tool-category mods carrying one of those tags.", "", md_table(ai_rows, ["period","game","class","n","ai_tagged_n","ai_tagged_share"]), "",
        "## Confounders", "",
        "- Nexus GraphQL returns public still-listed mods only; deleted, hidden, adult/user-blocked, or policy-removed items are a survivorship blind spot.",
        "- Current cumulative downloads/endorsements are age-confounded and discovery-confounded; older cohorts had more time to accrue usage.",
        "- Game events matter: Fallout 4's April 2024 next-gen update, BG3 official modding tools and patches in 2024-25, Skyrim Anniversary Edition/runtime churn, Stardew 1.6, and Cyberpunk 2.x/Phantom Liberty framework churn.",
        "- Nexus Collections, search/ranking changes, and AI-content policy/tagging can affect visibility and metadata independently of AI coding.",
        "- Category boundaries are fuzzy: some gameplay mods are data-only; some armour/weapon mods contain plugins; Content Patcher/SMAPI ecosystems blur code vs asset packs.", "",
        "## Verdict", "",
        f"Across these five stable modding scenes, code/tool-category cohorts rose from a 2022-24 mean of {code_base:.0f} still-listed mods per half-year to {code_rec:.0f} in 2025H2-2026H1 ({(code_rec/code_base if code_base else 0):.1f}x); asset-heavy cohorts rose from {asset_base:.0f} to {asset_rec:.0f} ({(asset_rec/asset_base if asset_base else 0):.1f}x). High-download code/tool hits did not show the same break: ≥10k-download code/tool mods averaged {code_10k_base:.0f} per half-year in 2022-24 versus {code_10k_rec:.0f} in 2025H2-2026H1, despite the metric favouring older cohorts. This supports the hypothesis for Nexus: many more small/recent mods, including code/tool mods, but no clear surge of new breakout hits.", "",
        "## Files", "", "- `fetch_nexus.py`: reproducible script", "- `schema_introspection_lite.json`: introspection evidence", "- `cohorts_aggregate.csv`, `cohorts_by_game_class.csv`: cohort counts", "- `category_classification.csv`, `notable_tags.csv`: classification evidence", "- `recent_top_code_mods.csv`, `ai_tag_share.csv`: recent top mods and AI tag checks",
    ]
    (BASE/"REPORT.md").write_text("\n".join(report)+"\n", encoding="utf-8")

if __name__ == "__main__": main()
