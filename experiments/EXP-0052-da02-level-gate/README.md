# EXP-0052 — DA02 level-30 gate and ordinary entry paths

## Question

Does the level-30 DA02 Story Manager node gate quest startup and Sacellum presence, or can the Boethiah's Proving book, shrine dialogue, or cultist-death path start or advance DA02 independently?

## Scope

The five-master census and local UESP revision 3564723 identify a level-30 threshold and report book, priestess, and cultist routes. Treat the wiki text as a route lead only. This experiment uses prepared official master records and the tested Skyrim - Misc.bsa classic PEX route. It cannot establish a profile-specific winner or level-one in-game state transition.

Read [hypothesis](hypothesis.md), [expected discriminants](expected-discriminants.md), and [protocol](protocol.md). Raw outputs are in ignored `.local/alignment/transactions/TX-20261016-0045/` and are tied to EV-0300's five-master hashes.

## Result

EV-0310 resolves the static shape of the ordinary book and Wilderness Encounter routes. DA02 has a level-30 Story Manager node and its Start Game Enabled flag is clear. WEDA02 is an event-driven helper, but its quest conditions require main DA02 to be running below stage 1. The four fixed book placements disable below the same level-30 global; a book `OnRead` callback still calls `DA02.SetStage(1)` when the current stage is below 1, and whether this starts a stopped quest is unknown. The leveled-list entries have a minimum level of 24, while `QABooksContainer` is placed only in `QASmoke`. No level-one start, functional progression, or Sacellum access was reproduced.

See [results](results.md) for source paths, the unresolved book callback, and the exact live discriminator.
