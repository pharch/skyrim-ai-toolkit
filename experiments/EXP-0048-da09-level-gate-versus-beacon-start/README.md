# EXP-0048 — DA09 level-12 gate versus Beacon and statue starts

## Question

Does the level-12 `DA09IncreaseLevelNodeSHARES` gate main quest DA09 startup, or can the Meridia Beacon or statue interaction start the quest below level 12?

## Scope

The retained local UESP *The Break of Dawn* revision 3539493 is gameplay context only. This investigation compares that lead with exact Skyrim.esm/Update.esm records and scripts available through tested read-only routes. Direct parsing is not an active-profile winner; the base Misc BSA PEX route does not cover every archive or dynamic caller. No live quest state or level-one transition is assumed.

## Status

Bounded static-source phase completed under EV-0306. The DA09 level-12 Story Manager route is the only main-quest startup path identified in the screened official records/scripts. Beacon and statue alias callbacks request stages but do not prove a stopped event-scoped quest starts; the CLOC placement helper requires main DA09 stage 0. Exact Steam behavior, low-level item availability, active-profile winners, and level-one gameplay remain open. See `results.md` for the scope and next discriminator.
