# Quest finalization and first natural callback order

**Frontier:** Q-0059, OBJ-1. **Status:** completed as a bounded GOG AE 1.6.1179.0 loader/caller trace; H1 and H2 remain unresolved.

EV-0320 ties the QUST-inclusive slot-19 pass to two GOG loader paths. `FUN_1401b9510` calls `FUN_1401bdf20` after its per-file record loop and returns after post-pass bookkeeping. `FUN_1401be290` also processes records through `FUN_1401bb4f0` and then calls `FUN_1401bdf20`; its sole direct caller `FUN_1403753b0` conditionally invokes it after a path helper and then calls `FUN_1401bb490`.

The inspected loader chains contain no direct, class-identified call to the registered `Quest.SetStage` callback. `FUN_1403753b0` has no analyzed direct code caller and only a data reference in an unclassified metadata/table region. The generic callback table for `FUN_14034de90` also lacks indexed code xrefs [EV-0313]. The capture does not resolve whether the first natural SetStage callback runs before or after load finalization. A read-only observer on the exact Steam target and complete order remains necessary for the runtime answer [EV-0260].
