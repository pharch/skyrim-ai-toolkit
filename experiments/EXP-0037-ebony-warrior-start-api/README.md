# EXP-0037 — Ebony Warrior event-scoped quest-start APIs

**Frontier / transaction:** Q-0029 / TX-20261016-0025  
**Status:** Bounded static result; the GOG wrapper path supports an event-scope guard. Steam runtime and other record types remain open.  
**Question:** Can ordinary Papyrus `Quest.Start` or `Quest.SetStage` schedule the Ebony Warrior CLOC quest before its level-gated Story Manager selection?

## Result

In GOG AE 1.6.1179.0, two inferred Papyrus wrappers reach `TESQuest::EnsureQuestStarted` only after their event-scope checks. The wrapper inferred as `Quest.Start` rejects a quest whose runtime event ID is not `-1`; the existing `Quest.SetStage` trace has a corresponding guard with an additional flag-bit condition. Accepted calls use deferred startup scheduling, but a CLOC event quest does not reach that route through these outside-event wrapper branches ([EV-0272], [EV-0289]).

The installed Steam Dragonborn.esm QUST `0202C49E` serializes `ENAM=CLOC`. Direct-parser scans across the five official master file outputs found no external QUST reference to that FormID; DIAL and INFO references were confined to the known Dragonborn dialogue records. This is bounded source-file evidence, not a profile winner or complete caller census ([EV-0288], [EV-0289]).

The GOG runtime wrappers and installed Steam plugin records are distinct source identities. Their relationship is an inference; no Steam runtime quest-start behavior was measured. The work does not establish a level-one bypass. See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md).

## Continuation

Q-0030 screens the remaining placed actor/reference, package, scene, and other VMAD-bearing record paths for an independent Ebony Warrior start or pre-event placement.
