import json, re, subprocess, difflib, time
from pathlib import Path
root=Path('/Users/seangoedecke/Code/where-is-the-software/niche-usage/decky')
plugins=json.load(open(root/'cache/plugins_downloads.json'))
text=(root/'cache/decky-plugin-database/.gitmodules').read_text()
mods=[]
for block in re.split(r'\n(?=\[submodule)', text):
    pm=re.search(r'path\s*=\s*([^\n]+)', block); um=re.search(r'url\s*=\s*([^\n]+)', block)
    if pm: mods.append({'path':pm.group(1).strip(),'base':pm.group(1).strip().split('/')[-1], 'url':um.group(1).strip() if um else ''})
pathmap={m['path']:m for m in mods}
def norm(s):
    s=s.lower()
    for token in ['steamdeck','steam-deck']:
        s=s.replace(token,'deck')
    s=re.sub(r'^(sdh-|decky-|deck-|steamdeck-)', '', s)
    s=re.sub(r'(-decky|-plugin|-plugins|-for-deck|deck)$','',s)
    return re.sub(r'[^a-z0-9]+','',s)
manual={
 'Decky-Framegen':'plugins/Decky-Framegen','Decky LSFG-VK':'plugins/decky-lsfg-vk','PlayCount':'plugins/playcount-decky','Deck Settings':'plugins/decky-game-settings','HueSync':'plugins/HueSync','Picture in Picture':'plugins/decky-pip','Virtual Surround Sound':'plugins/decky-virtual-surround-sound','LetMeReShade':'plugins/LetMeReShade','Music Control':'plugins/MusicControl','Decky Sunshine':'plugins/decky-sunshine','DeckSP':'plugins/DeckSP','Better Keyboard':'plugins/BetterKeyboard','Speed Test':'plugins/decky-speed-test','WiFi Locker':'plugins/decky-wifi-locker','Decky-Lookup':'plugins/Decky-Lookup','Decky Proton Launch':'plugins/decky-proton-launch','Non-Steam Badges':'plugins/decky-nonsteam-badges','Simple Timer':'plugins/simple-timer','Deck Shelves':'plugins/Deck-Shelves','Launch Options':'plugins/decky-launch-options','Dimmer Deck':'plugins/DimmerDeck','Crosshair':'plugins/Crosshair','Decky Ludusavi':'plugins/decky-ludusavi','MuraDeck':'plugins/MuraDeck','Decky Translator':'plugins/decky-translator','Deck Progress Tracker':'plugins/deck-progress-tracker','Game Sync':'plugins/SDH-GameSync','Network Sentinel':'plugins/network-sentinel','Steam Status':'plugins/steamstatus-decky','Download All':'plugins/decky-download-all'
}
mods_by=[(norm(m['base']),m) for m in mods]
def map_mod(name):
    if name in manual and manual[name] in pathmap: return pathmap[manual[name]]
    nx=norm(name)
    return max(mods_by, key=lambda nm: difflib.SequenceMatcher(None,nx,nm[0]).ratio())[1]
def gh_repo(url):
    m=re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', url)
    if not m: return None
    return f'{m.group(1)}/{m.group(2)}'
recent=sorted([x for x in plugins if x['created']>='2025-01-01'], key=lambda x:x['downloads'], reverse=True)[:30]
cache_file=root/'cache/repo_metadata.json'
meta=json.load(open(cache_file)) if cache_file.exists() else {}
rows=[]
for x in recent:
    mod=map_mod(x['name'])
    repo=gh_repo(mod['url'])
    if repo and repo not in meta:
        r=subprocess.run(['gh','api',f'repos/{repo}','--jq','{created_at,updated_at,pushed_at,stargazers_count,description,html_url}'], text=True, capture_output=True)
        if r.returncode==0:
            try: meta[repo]=json.loads(r.stdout)
            except Exception: meta[repo]={'error':'parse','stdout':r.stdout}
        else:
            meta[repo]={'error':r.stderr.strip()[:300]}
        cache_file.write_text(json.dumps(meta,indent=2,sort_keys=True))
    rows.append({**{k:x[k] for k in ['id','name','created','downloads','description','tags']}, 'submodule_path':mod['path'], 'submodule_url':mod['url'], 'github_repo':repo, 'repo_meta':meta.get(repo) if repo else None})
(root/'data/top_recent_repos.json').write_text(json.dumps(rows,indent=2))
print('wrote', len(rows), 'rows', 'meta', len(meta))
for r in rows:
    cr=(r.get('repo_meta') or {}).get('created_at')
    print(r['name'], r['downloads'], r['created'][:10], r['github_repo'], cr)
