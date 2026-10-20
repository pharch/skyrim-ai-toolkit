# Competing models

## H1 — GOG load/finalization dispatch

TESQuest vtable slot 19 runs during GOG file-load finalization after QUST record parsing and type-array registration. Its clear can therefore occur after the serialized `Start Game Enabled` value is loaded. Whether this pass returns before the first natural `Quest.SetStage` callback is delivered remains a separate ordering question.

**Predicted discriminant:** a TESQuest-compatible slot-19 dispatch appears in the load-manager chain after the QUST parser and form registration, rather than only in a later quest transition.

## H2 — Later lifecycle dispatch only

Slot 19 runs only during a later quest lifecycle operation; the load-manager chain does not invoke it after QUST parsing, so the loaded bit can remain visible to an earlier guard.

**Predicted discriminant:** no TESQuest slot-19 call appears in the post-file-load type-array sweep; all class-resolved calls belong to later start/stop/reset transitions.

## Result

EV-0318 supports H1's GOG parse-to-finalization component and falsifies H2 as an exclusive model. The first natural `Quest.SetStage` callback order is not directly observed, so this result does not claim that the slot-19 pass precedes callback delivery for a particular quest.
