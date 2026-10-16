# Are there more official ports / remasters? (2026-10-14)

Question: regardless of whether studios *say* they use AI, are they shipping more ports, remasters and re-releases of old games?

**Answer: no measurable increase.** The only rise is ports to the new Switch 2, which launched June 2025. Every other measure is flat or noisy. That contrasts sharply with the hobbyist scene (~10–20× more unofficial ports; see `02-game-hobbyist-catalogue.md`).

## 1. Gematsu headlines (all posts Jan 2021–Oct 2026, ~22k titles; `data/gematsu_titles.tgz`, `scripts/gematsu.py`, `scripts/analyse_ports.py`)
Gematsu covers nearly every official platform announcement. Headlines classified by regex, Jan–Sep each year.

| Year | Posts | Remaster/remake/collection headlines | Port headlines (Switch 2) | Port headlines (other) | Other ports as share of posts | Port headlines mentioning PC |
|---|---|---|---|---|---|---|
| 2021 | 3,958 | 161 (4.1%) | 0 | 420 | 10.6% | 151 |
| 2022 | 3,126 | 164 (5.2%) | 0 | 339 | 10.8% | 136 |
| 2023 | 3,251 | 165 (5.1%) | 0 | 320 | 9.8% | 109 |
| 2024 | 3,209 | 152 (4.7%) | 0 | 378 | 11.8% | 124 |
| 2025 | 3,474 | 202 (5.8%) | 92 | 344 | 9.9% | 101 |
| 2026 | 3,661 | 181 (4.9%) | 210 | 304 | 8.3% | 88 |

Excluding Switch 2, port headlines are *down*. Remaster/remake headlines are flat at about 5%.

## 2. Steam store: remaster-type titles by release date (`data/steam_remasters.json`, `scripts/steamsearch.py`)
Titles matching remaster/remake/definitive/enhanced/anniversary edition, director's cut, HD, redux or complete edition, Jan–Sep:
2019 23 · 2020 34 · 2021 39 · 2022 38 · 2023 49 · 2024 59 · 2025 71 · 2026 51.
This tracks overall Steam release growth, with no 2026 jump. Many matches are small indies.

## 3. GOG catalogue additions (`data/gog_all.json`, `scripts/gog.py`)
Games added Jan–Sep whose original release was at least 5 years earlier:
2021 110 · 2022 92 · 2023 92 · 2024 84 · 2025 60 · 2026 117.
2026 is up about 30% on the 2022–24 average, but 2025 was low, so this is noisy. GOG's Preservation Program has run since Nov 2024. The catalogue only lists products still for sale.

## 4. Wikidata platform-qualified release dates (`data/wd_dates.csv`)
Games getting a release on some platform at least 3 years after first release: 2022 219, 2023 151, 2024 150, 2025 127, 2026 YTD 120. Wikidata lags badly for recent years (2026 "new games" is only 2,072 vs ~10k in 2025), so this can't show a change. At most, 2026 is not obviously lower.

## 5. Steam patching of old games (from round 1)
The share of popular pre-2018 games posting patch or update notes was flat at about 19% for 2024–2026. The rate of revival after 2+ years dormant was flat at about 10–12%.

## Caveats
- Headline regex is approximate.
- Announcements lag development by 1–3 years, so AI-accelerated studio porting started in mid-2026 wouldn't show up in announcements yet.
- The Witcher 3 Remastered (5 weeks from announcement to release) and Diablo II: Resurrected's Warlock DLC are anecdotes, not trend evidence.
- Hobbyists can ship in days, which is one reason they show the effect first.
