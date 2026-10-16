# Niche communities: is the new software being used? (2026-10-15)

Data and method are in `niche-usage/`. This applies the "count only what people use" test to the two niche registries with the biggest supply jumps.

## Home Assistant community store (HACS) integrations
Usage comes from Home Assistant's opt-in analytics, which count installations per custom integration. I measured each cohort at **equal age**, about 6 months after the quarter it was added to the HACS default list, using Wayback snapshots. The opted-in user base itself grew 2.4× between Aug 2024 and Oct 2026, so the thresholds are scaled to that base.

| Cohort | Added (still listed) | ≥100 installs, scaled | ≥1,000 installs, scaled |
|---|---|---|---|
| 2023 Q4 | 57 | 30 | 6 |
| 2024 Q1 | 29 | 11 | 0 |
| 2024 Q3 | 39 | 17 | 5 |
| 2024 Q4 | 57 | 18 | 3 |
| 2025 Q1 | 126 | 33 | 7 |
| 2025 Q2 | 353 | 75 | 6 |
| 2025 Q3 | 186 | 30 | 3 |
| 2025 Q4 | 202 | 35 | 1 |
| 2026 Q1 | 371 | 50 | 3 |

- **Additions** went up about 5×.
- **Integrations with ~100+ reporting installs** went up about 2.3×, from roughly 19 per quarter to roughly 45.
- **Integrations with ~1,000+ installs** stayed flat at 0–7 per quarter.
- **The share of new integrations that reach 100 installs** fell from about 40% to about 15–25%.
- **Mixed attribution.** Several of the top 2025–26 entries are vendor or long-standing projects newly added to the default list, not new hobby code. Examples are `xiaomi_home` (official Xiaomi), `scheduler` and `homematicip_local`.

## NVDA screen-reader add-on store
Usage is GitHub release downloads of the `.nvda-addon` files. 98% of add-ons are hosted on GitHub. "Early" counts only releases published within 180 days of the add-on's first store listing.

| Cohort (first in store) | Added | Still listed | ≥100 early downloads | ≥1k early | ≥10k early |
|---|---|---|---|---|---|
| 2024 H1 | 47 | 35 | 35 | 34 | 8 |
| 2024 H2 | 27 | 20 | 20 | 19 | 1 |
| 2025 H1 | 38 | 34 | 30 | 17 | 0 |
| 2025 H2 | 65 | 61 | 53 | 36 | 2 |
| 2026 H1 | 152 | 148 | 135 | 78 | 2 |
| 2026 H2 (to Oct 15) | 110 | 107 | 89 | 32 | 2 |

- **Add-ons reaching 1,000 early downloads** went from about 18–34 per half-year to 78 in 2026 H1, roughly 2.5–4×. That is the clearest rise in *used* new software anywhere in this investigation.
- **Add-ons reaching 10,000 downloads** stayed flat at about 2 per half-year. In 2024 H1 the figure was 8, but that cohort includes established add-ons migrating into the store, which launched in 2023.
- **The share of new add-ons reaching 1,000 downloads** fell from about 97% to about 55%.
- **Top 2026 H1 add-ons:** WhatsApp Enhancer (30k downloads), WhatsApp NG (19k), two YouTube accessibility add-ons (about 9–10k each), Drag and Drop (8k), NVDA Coach (8k) and translation tools. These are mundane, useful accessibility fixes for mainstream apps, which is exactly what you'd hope for.
- **Caveats.**
  - Download counts include downloads from before the store listing. For example, freeAudio and MathCAT show large counts despite only just joining the store.
  - Downloads are not active users.
  - No add-on is AI-attributed individually. Attribution rests on timing and on community testimony (Double Tap, the store-crowding issue).

## Verdict
In niche communities the pattern changes from "more stuff, same use" to **"many more lightly-used tools, no more big hits"**:
- **Modestly used new tools:** up about 2–4×. That means 100+ Home Assistant installs or 1,000+ NVDA downloads.
- **Widely used new tools:** flat.

This fits the theory that AI lets people with small, specific needs build for themselves and a few hundred others. Those small tools are where the new good software is. It is spread across a long tail, so it never appears in aggregate charts.
