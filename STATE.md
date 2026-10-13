# Active Research State

Status: INITIAL / UNVERIFIED. The fork's legacy research, probes and Discord corpus have **not** yet been ingested here. Do not treat seeded frontier entries as discovered facts.

## Operating environment

- Game edition/version: **TO BE RECORDED**
- Mod manager/load order: **TO BE RECORDED**
- Game paths and test save: **TO BE RECORDED IN LOCAL UNTRACKED CONFIG**
- SKSE/native probe environment: **TO BE AUDITED**
- Static-analysis binaries and Ghidra project: **TO BE AUDITED**
- Existing DevBench availability: **UNKNOWN**
- UESP access: **API ENDPOINT NOT VALIDATED FROM LOCAL ENVIRONMENT**
- Apocrypha export location and format: **UNKNOWN**

## Existing research to migrate

Check legacy repo for `shifting.md`, research notes on poison resistance, float/ULP AV perturbation, enchanting and alchemy XP, active-effect lifecycles, quest requirements, armor XP, and prior SKSE probe outputs. Preserve original evidence and caveats.

## P0 active themes

OBJ-1: Enumerate specific gates and the distinct pathways that initiate real quests/events. Separate a level gate from quest completion, event spawn, and player-facing journal state.

OBJ-2: Trace the native XP grant for armor hits and determine whether damage mitigation can remain while skill XP award is independently suppressed.

## Next actions

1. Validate retained upstream tooling works from a **separate checkout** and never from the game root.
2. Import legacy research/source paths with provenance, not guessed summaries.
3. Run source-verification baseline for top quest and armor assumptions.
4. Expand `FRONTIER.json` from actual evidence.

## Blockers / user-controlled operations

No real in-game actions have been authorized or performed in this bootstrap.

## Recent checkpoint

This file is a template generated before installation. Replace with evidence-backed operational status at the first real research session.
