Method (run 2026-10-15; commands were run ad hoc from /tmp, reproduced here):

HACS / Home Assistant
- First-added date per repo: `git clone https://github.com/hacs/default` then `git log --reverse --format='C %aI' -p -- integration`, first `+"owner/repo"` line per repo.
- repo -> integration domain: https://data-v2.hacs.xyz/integration/data.json (current listings only; removed repos lost).
- Usage: https://analytics.home-assistant.io/custom_integrations.json (opted-in installs per domain). Historical snapshots from Wayback (CDX: url=analytics.home-assistant.io/custom_integrations.json); some are gzipped.
- Equal age: installs in the snapshot nearest cohort-quarter-end + 182 days (within 75 days). "Scaled" thresholds multiply by (snapshot total installs / 1M) to correct for growth of the opted-in base (0.82M -> 1.99M, Aug 2024 -> Oct 2026).

NVDA add-on store
- First-added per addon: blobless clone of nvaccess/addon-datastore, `git log --diff-filter=A --name-only -- addons`.
- Repo per addon: GitHub release URL in current addons/*/*.json.
- Downloads: `gh api --paginate repos/{repo}/releases`, summing download_count of *.nvda-addon assets; "early" = releases published within 180 days of store add.
