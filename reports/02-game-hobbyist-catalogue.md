# Game & hobbyist catalogue (research agent report, 2026-10-14)

NOTE: The Brawl section is being corrected — user says the well-known story is **Brawlback**, not (only) Orca. See `03-brawlback.md` once written.

## Diablo II
- Feb 11 2026: **"Reign of the Warlock" DLC for Diablo II: Resurrected** revealed and released same day at Diablo 30th Anniversary Spotlight ($24.99). First new D2 class in 25 years; reworked Terror Zones; new uber boss; loot filter; stackable stash; D2R launched on Steam same day. IGN: "the biggest surprise" (https://www.ign.com/articles/blizzard-launches-warlock-dlc-for-diablo-2-resurrected-25-years-after-the-original-games-release-and-its-also-now-on-steam). No AI statement found. No new D2 *remaster* in 2025–26 (D2R is 2021).
- Sep 15 2026: Blizzard teases 200+ unique item changes (https://www.tweaktown.com/news/113518/).
- Sep 27–Oct 12: fan D2R 3D camera (github.com/emmericp/D2R-3D) and VR port (github.com/natpoh/diablo2-vr-port).
- Blizzard union contract (Sep 9 2026) includes AI bargaining (https://kotaku.com/blizzard-workers-union-contract-microsoft-2000732422).

## Publisher/studio side
| Date | Item | AI status | Source |
|---|---|---|---|
| Oct 13 2026 | Xbox Labs memo (Asha Sharma): "games rapidly decompiled and rebuilt to run on hardware they were never originally designed to support… Apple Silicon… WebAssembly and WebGPU" — "unmistakably good outcomes for players" | Confirmed response to agents | https://news.xbox.com/en-us/2026/10/13/introducing-xbox-labs/ |
| Oct 12 2026 | Epic Disney shooter goes "no more hand-written code" (Bloomberg via Ars); delayed indefinitely | Confirmed | https://arstechnica.com/gaming/2026/10/report-epic-games-goes-all-in-on-ai-for-disney-collaboration/ |
| Aug 25 → Sep 29 2026 | Witcher 3 Remastered (path tracing, Switch 2), ~5 weeks announce→release | Unknown | https://www.techtimes.com/articles/325602/20260826/ |
| Sep 17 2026 | CESA: 85.8% of Japanese devs use genAI (51% a year earlier); debugging top use | Survey | https://kotaku.com/over-85-percent-of-japanese-game-developers-are-using-ai-2000736041 |
| Aug 2026 | Square Enix + Google AI QA automation | Announced | PC Gamer/MSN |
| Apr 30 2026 | Krafton "AI-first" but Subnautica 2 says no genAI | Denied | Eurogamer/MSN |
| Sep 28–Oct 1 | Bethesda C&D (Fallout: New York); Activision takedown of AI-decompiled MW2 footage | Pushback | https://kotaku.com/activision-and-bethesda-crackdown-on-genai-mw2-and-fallout-projects-2000739580/ |
| Oct 6 | GTA V browser port (playgta5.com) offline within hours | Claimed AI | https://startupfortune.com/ai-reverse-engineering-turns-gta-5-and-halo-into-browser-games-overnight/ |

## Hobbyist games
- Kotaku ~Oct 5 2026: "hundreds of vibe-coded, AI-decompiled emulators and games have appeared out of thin air… because Claude Opus 5.5 is extremely good at decompiling." Browser ports of Halo CE, CoD:BO, GTA VC, Skate 3, Simpsons: Hit & Run (https://kotaku.com/we-might-be-cooked-as-these-vibe-coded-web-browser-ports-of-halo-the-simpsons-hit-and-run-and-gta-vice-city-seem-to-work-perfectly-2000743300).
- Mashable Oct 12: PS5 jailbreaks speeding up; AI suspected, unconfirmed (https://mashable.com/tech/ps5-jailbreaks-flooding-in-thanks-to-ai).

| Date | Project | AI | Source |
|---|---|---|---|
| Oct 6–7 | Bloodborne native Windows port (2.5k★) | Confirmed (44 Claude commits) | github.com/Supermedo/bloodborne_pc |
| Oct 8–12 | God of War III Remastered PC (1.75k★) | Partial | github.com/FelipePrado0/gow3_pc |
| Oct 7–8 | P.T. native PC port (1.67k★) | Confirmed (README) | github.com/LoreanXavier/pt-pc |
| Oct 8 | Metroid Prime native port (on PrimeDecomp) | Confirmed (README) | github.com/Odrannnn/MetroidPrimePort |
| Oct 1/9 | First native Switch ports: Mario Wonder, Odyssey | Unknown | https://www.dsogaming.com/news/super-mario-bros-wonder-is-getting-an-unofficial-pc-native-port/ |
| Oct 14 | Mario Galaxy PC port "nebula" | Confirmed (100/100 AI commits) | github.com/keepvaibin/nebula |
| Sep 28 | Rival Galaxy port "AstroCore", "100% coded by humans" | Denied | dsogaming |
| Oct 1–3 | GalaxyQuest (Galaxy on Quest VR), "100% made by AI (Opus 5.5)" | Confirmed | github.com/bigmak94/GalaxyQuest |
| Oct 1–3 | AstroQuest (Astro Bot on Quest 3) | Confirmed | github.com/bigmak94/AstroQuest |
| Sep 22 | Fable 2 native PC port via ReXGlue + local Qwen3.8 27B | Confirmed | github.com/himdo/Fable-2-Recomp |
| Sep 30 | Halo CE in browser, 128-player | Partial | github.com/bnunu/halo-ce-universal |
| Oct 12 | PS2 → WebAssembly static recomp (Show HN 307) | Partial | github.com/snuri00/ps2-web-recomp |
| Sep–Oct | King Kong 360, CoD3, Pilotwings 64, Link's Awakening, Namco System 22 decompile | Mostly confirmed | DSOGaming |
| Oct 9 | momo5502 AI decompile of MW2-like FPS: 99% functions, 83% byte-exact, ~600–700B tokens | Confirmed | https://momo5502.com/posts/2026-10-09-game-decompilation/ |
| Feb 2026 | Crimsonland decompiled in ~4 days, codex/gpt-5.2 | Confirmed | https://banteg.xyz/posts/crimsonland/ |
| Sep 20 | RE4 (GC) byte-identical decomp | Unclear | github.com/adonis-singh/re4 |

Emulators/homebrew: PS5SX2 (PCSX2 on PS5, 100/100 AI commits); PS5_Vulkan (Mesa/RADV for PS5, AI); XPSemu; BryKytyPS5 (AI-assisted, runs Astro Bot/Demon's Souls); SharpEmu (6.3k★, "AI-assisted"); RPCS3 on PS4; PS5X.

Fan translations: DQXI 3DS English (Claude, Oct 11); Super Robot Taisen OG Gaiden PS2 English (Claude+Codex, Jun); DQMJ3P fixes; Korean retro patch Claude skill.

Blind-gamer accessibility mods: some new in 2026 but none notable / AI-credited.

Backlash: Zelda/Banjo Recompiled devs "We have not, do not and will not use AI", call AI Banjo-Tooie "slopcomp" (https://kotaku.com/zelda-and-banjo-recompiled-devs-go-to-war-with-ai-vibe-coded-slopcomps-2000739936). Dolphin no-AI policy Mar 8 2026. N64Recomp Discord bans AI showcases.

## Outside games
- Gravity Linux on M4 Mac mini (Codex + Claude Code), Sep 21 (https://www.phoronix.com/news/Gravity-Linux-M4-Mac-Mini-Alpha)
- ArtCraft: 7 OSS Adobe clones with Opus 5.5, Oct 7 — "ambitious, familiar, and buggy" (https://arstechnica.com/ai/2026/10/software-is-over-bold-ai-developer-takes-aim-at-adobe-with-open-source-clones/)
- C&C Generals on macOS/iOS (Claude Fable), Jul 4 (github.com/ammaarreshi/Generals-Mac-iOS-iPad)
- Claude-written macOS driver for HP printer, Aug 18 (HN 49344643)
- Counterexamples (human-made): Mac OS X on Wii (Apr), scooter firmware in Rust.

## Rate of change
DSOGaming "unofficial PC port" articles/month: 2025 0–2; Apr–Jul 2026 3–5; Aug 9; Sep 21; Oct 1–14 22.

GitHub repos created:
| Month | recomp | decomp | "pc port" |
|---|---|---|---|
| Sep 2024 | 21 | 184 | 4 |
| Sep 2025 | 41 | 289 | 7 |
| Mar 2026 | 111 | 404 | 34 |
| Jun 2026 | 212 | 461 | 52 |
| Aug 2026 | 606 | 519 | 68 |
| Sep 2026 | 617 | 684 | 134 |
| Oct 1–13 2026 | 474 | 539 | 169 |

Unverified: Kotaku "hundreds" not counted independently; keyword counts noisy; Reddit not accessed.
