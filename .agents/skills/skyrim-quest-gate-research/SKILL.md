---
name: skyrim-quest-gate-research
description: Investigate level-locked vanilla Skyrim quests, encounters and events, locate actual gate mechanisms, and develop reproducible level-one bypass experiments.
---

# Skyrim AE quest/event gate research

1. Choose a precisely identified quest/encounter with a plausible level prerequisite; verify from UESP and game data.
2. Distinguish quest startup, journal display, dialogue availability, alias fill, story-manager event and actual world encounter spawn.
3. Enumerate all entry points and their conditions (QUST, SM nodes, INFO branches, aliases, scripts, native callbacks).
4. Identify when the player-level predicate is read; whether result is cached, reevaluated, or bypassed by alternate vanilla event sources. Do not invent native offsets.
5. Write rival hypotheses and predicted observations; test in an isolated diagnostic save with tagged interventions only if approved.
6. Attempt player-available unmodified-game reproduction; `setstage`/`startquest` do not qualify.
7. Capture quest instance state, stage transitions, alias/world changes, level and XP throughout. Repeat from clean baseline.
8. Generalize only after a second independent gate case and a shared mechanism are supported.
