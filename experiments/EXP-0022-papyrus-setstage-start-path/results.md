# Results

## Observed

- The matching GOG Address Library maps `TESQuest::EnsureQuestStarted` (CommonLib AE ID 25003) to `0x3C9D30` and `BGSStoryTeller::BeginStartUpQuest` (ID 32485) to `0x532E60`.
- In `FUN_140a48aa0`, the inferred `Quest.SetStage` wrapper rejects a request when `(flags & 1) == 0` and the quest event ID is not `-1`, logging `attempting to start event scoped quest outside of story manager`.
- Accepted requests call `EnsureQuestStarted` with the start-now argument clear. When the output byte is zero, the wrapper calls `FUN_1403c9e40` for the requested stage. When nonzero, it queues work through `FUN_1409b2150`; its diagnostic says the quest will be started first.
- `EnsureQuestStarted` has a separate immediate branch which calls `FUN_1403ccd90` and then the mapped `BeginStartUpQuest` entry. Its non-immediate branch sets the result byte and calls helper routines.
- `FUN_1403c9e40` requires the tested quest flag bit and a matching stage record before calling the stage routine.

## Result and limits

The GOG trace supports automatic start scheduling for an eligible stopped quest and a deferred stage request. The Event-ID guard means this path is not an unrestricted bypass for a Story Manager-scoped quest. Haknir's two identified main-stage-10 writers still run only behind their own `>=36` checks ([EV-0271]). The queried per-entry routines are not symbolically identified as alias filling; no alias-fill conclusion follows. The Papyrus native registration was not recovered, so `FUN_140a48aa0` remains an inference. No Steam equivalence, profile winner, runtime state, vanilla candidate, or reproduction was established.

## Evidence

See [EV-0272](../../research/EVIDENCE.json) for the hashed note, CommonLib/address mappings, raw Ghidra stdout hashes, build identity, and the exact remaining test boundary. EV-0260 records missing exact-profile, disposable-save, and Story Manager/alias observer prerequisites.
