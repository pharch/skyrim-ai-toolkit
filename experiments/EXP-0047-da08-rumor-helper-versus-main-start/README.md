# EXP-0047 — DA08 level-20 rumor helper versus main-quest start

## Question

Does the level-20 `DA08KickerNode` gate only `DA08RumorPointer`, or does the same level requirement control every ordinary path that starts main quest DA08?

## Scope

The lead is the five-official-master Story Manager census EV-0300 and local UESP revision 3578672 for *The Whispering Door*. UESP is gameplay context only. The source route is the strict, read-only direct TES4 parser; it reads official source files and does not resolve active-profile winners. The live Steam target is separately identified in EV-0109, but no live transition or profile order is part of this static episode.

## Result

EV-0305 supports the helper-only interpretation for main DA08 startup: the level-20 node selects separate helper QUST `DA08RumorPointer`, while main DA08 QUST `0004A37B` has the serialized Start Game Enabled bit set. Seventeen of 18 DA08-named DIAL topics are owned by main DA08, while the Balgruuf rumor topic is owned by the helper. The helper's PEX sets a `PlayerGotRumor` property on main DA08 and stops; it does not start main DA08. The main QUST's serialized startup setting is not a live quest-state observation, and dialogue INFO conditions, physical access, profile winner, and a level-one transition remain untested.
