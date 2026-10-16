# Brawl rollback netcode: Orca vs Brawlback (research, 2026-10-14)

**Summary.** The AI-coded project was **Orca** (Luis "Crunch" Rosias, YouGame). **Brawlback** is the 5-year human project it was accused of bypassing. Brawlback hasn't announced any AI use. But on Oct 7, a day after Orca's source went public, Brawlback merged Orca's snapshot code (YouGame copyright headers kept). That is what got Brawlback's rollback working. Brawlback has still not shipped a playable build ("ETA: NONE").

Search engines and Reddit were blocked for the agent. Sources: GitHub, X via fxtwitter, Bluesky, YouTube, Medium.

## Pre-2026
- Nov 2021: Brawlback-Team org created.
- Progress reports:
  - **#1 (Dec 2022):** PiNE's prototype played a match "albeit slow and finnicky". Problems were desyncs and 20+ MB savestates. https://medium.com/@whitetpoison72/brawlback-progress-report-1-fd7965a581f9
  - **#2 (Apr 2023):** the code injector put code at the wrong addresses; switched to the Syriinge loader.
  - **#3 (Dec 2023):** rollback still crashed and desynced in edge cases.
- Why Brawl is hard: poorly documented compared with Melee, talks to the Wii's system software during matches, and drawing code modifies game memory. Slippi-style rollback would need deep reverse engineering.

## 2026 before October
- Apr: FAQ says no donations, Alpha "Current ETA: NONE" (https://x.com/BrawlbackTeam/status/2046775326974304317).
- May–Jun: PiNE commit burst; GekkoNet forked in.
- Jul 31, Report #4: switched to emulator-level delta-state rollback, still "heavily desyncs" (https://medium.com/@whitetpoison72/brawlback-progress-report-4-3008e0272901).
- Aug–Sep, `rollback` branch: "Still desyncs for some reason" (Aug 27).
- Crunch, Sep 9: "Binaries are becoming ridiculously easy to decompile and/or modify with Astra" (https://x.com/CrunchBuilds/status/2097554464886473140).

## Oct 6–14
- **Oct 6, ~04:22 UTC:** Hungrybox posts a promo for Rollback Brawl/P+ on Orca, then deletes it.
- **Oct 6, 05:48:** Crunch says there is "no code from brawlback WHATSOEVER" and that he worked solo for about a week.
- **Oct 6, 06:48:** Hungrybox apologizes. He says a "rollback solution with vibe coding does not feel correct" and that "AI has no place in the world of gaming" (https://x.com/LiquidHbox/status/2107362457580695653).
- **Oct 6:** Orca docs corrected: its prototype was a fork of Brawlback's rollback branch, and Orca restarted from Dolphin 2609 on Oct 1.
- **Oct 6:** Brawlback statement thread. It credits WhiteTPoison and PiNE, says nothing about AI, and accepts Hungrybox's tournament prize-pool money (https://x.com/BrawlbackTeam/status/2107385182684873090).
- **Oct 7:** Brawlback merges PR #5, "Implement GekkoNet Rollback Using Orca Snapshots" (+12k lines; files marked `// Copyright 2026 YouGame`). Review note: "Has existing code from Orca, but will work to remove over time." Nyx: "what if I took the code that actually worked from the thing and ported it" (https://x.com/NyxTheShield/status/2107633622383780326).
- **Oct 7:** Crunch's hindsight post includes "Be transparent about AI use and explain how agents would try to fix all the bugs" (https://x.com/CrunchBuilds/status/2107636082594472411).
- **Oct 7:** Orca PR #2 removes Dolphin's AI policy; the PR body says "Generated with Claude Code".
- **Oct 7–8:** Brawlback PRs #7 (JIT dirty-page tracking, 30–40% faster) and #8 ("Functional Dolphin Wide Rollback") merged.
- **Oct 9:** Nyx says "I just took a part of the snapshot system"; the same day Nyx posts a viral joke mocking AI vibe-coded recomps.
- **Oct 11:** Nyx says the determinism issues are fixed (1 frame at ~170 ping). Crunch announces the "FIRST EVER P+ rollback tournament" on Orca.
- **Oct 14:** PiNE opens PR #9 (Tracy profiler).

## Takeaway for "where is the software?"
A ~5-year-stuck hobby problem (deterministic emulator-level rollback for Brawl) went from "ETA: NONE" to working rollback in about two weeks of October 2026.
- The breakthrough came from an AI-agent-built project.
- The established human team then adopted that code within 24 hours.
- The adoption was publicly framed as non-AI, and the community is strongly anti-AI.

## Gaps
- Hungrybox's original post text.
- How much of Orca is AI-written.
- Discord and Reddit discussion.
- Press articles (search was blocked).
