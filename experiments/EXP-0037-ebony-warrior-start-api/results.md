# EXP-0037 results

## Direct observations

- Installed Dragonborn.esm QUST `0202C49E` is serialized with `ENAM=CLOC` and Start Game Enabled clear ([EV-0288]).
- In GOG AE 1.6.1179.0, the function inferred as Papyrus `Quest.Start` checks the quest event ID. A nondefault event ID takes a branch that logs `attempting to start event scoped quest outside of story manager` and does not call `EnsureQuestStarted`. For event ID `-1`, it calls `EnsureQuestStarted` in deferred mode and queues work when startup is pending ([EV-0289]).
- The GOG wrapper previously inferred as `Quest.SetStage` has the same event-scope rejection when the tested flag bit is clear, then uses deferred startup for accepted calls ([EV-0272]).
- Ghidra reports eight observed direct caller functions to `BeginStartUpQuest` and seven to `EnsureQuestStarted` in the analyzed project. This count is bounded to analyzed direct call references; it does not close every indirect or data-driven call path ([EV-0289]).
- `TESQuest::Start` was not available as a named CommonLib AE relocation. The failed lookup does not establish method absence ([EV-0289]).
- The raw five-master parser screen covered 2,391 QUST, 19,844 DIAL, and 41,188 INFO records. No other QUST record directly contains the target FormID; six DIAL and three INFO target references are confined to Dragonborn.esm ([EV-0289]).

## Result and limits

H1 is supported for the inspected GOG wrapper code. H2 is not supported in the screened direct QUST/DIAL/INFO classes. The Steam CLOC record and GOG native event-ID guard are separate source/build observations; their interaction is an inference. The scan does not cover placed-reference, actor, scene, package, other VMAD-bearing, Creation Club, or user-plugin records, nor dynamic form lookup or runtime alias state. No level-one bypass is established.
