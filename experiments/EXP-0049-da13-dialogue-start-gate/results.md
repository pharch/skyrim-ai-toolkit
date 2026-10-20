# Results — EXP-0049

## Source result

The ordinary main-quest Story Manager node is `Skyrim.esm SMQN 000C4CC5 DA13IncreaseLevelNodeSHARES`, with `GetLevel >= DA13MinLevel` (GLOB `000C4CC4` = 12) and child QUST `0008998D DA13` [EV-0307]. Main DA13 and helper `Da13Intro` both have Start Game Enabled clear. This is not the only serialized startup route: WEJS14 has its own `GetLevel >= 10` condition and its Afflicted Refugee dialogue can set WEJS14 stage 100; the stage fragment sets `Da13Intro` stage 1; the helper starts its intro scene; the scene sets helper stage 100; and the helper stage-100 fragment calls `DA13.Start()` [EV-0307].

This supports H1 and falsifies H2 only for the bounded official-record/base-Misc-PEX source model: the captured Refugee handoff can start main DA13 below level 12 at the serialized level-10 threshold. It is not a level-one result or live event observation.

The complete group-aware DA13 DIAL/INFO join and captured TIF set found main-owned stage writers for stages 1, 5, 10, 15, 20, 21, 31, 40, 45, 81 and 100, but no main-owned TIF `Start()` call. One unconditioned main-owned INFO (`000A1A65`) requests stage 21. Its availability while the quest is stopped remains unresolved. The Empty Vessel also requests stage 21, but REFR `000E6C89` is Initially Disabled and its only identified enabler is `DA13KeshSCRIPT` on the main quest's Kesh alias. Goo, Orchendor, and WEJS15 callbacks are later-stage paths. The generic Orchendor alias script extraction was attempted through the supported Skyrim - Misc.bsa route and failed with `no supported PEX stream found`; the alias properties show prerequisite stage 40 and target stage 75, but callback semantics remain unverified.

## Limits and next discriminators

- Exact Steam 1.6.1170.0 handling of `SetStage` on stopped DA13 and whether main-owned INFO is offered before DA13 runs.
- Actual level-10 WEJS14 event/alias/Refugee availability and whether the route executes without altering level or quest state.
- A clean level-one test, physical access to Kesh/Refugee, exact active-profile winner, and repeated vanilla reproduction.
- The generic `defaultsetstageondeathrefalias` callback outside the tested base-Misc extractor scope.

No causal edge to OBJ-2 is justified by this source result.
