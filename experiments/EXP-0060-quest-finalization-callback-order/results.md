# Results

## Direct observations

1. The EV-0318 capture records `FUN_1401b9510` calling `FUN_1401bdf20` after its `FUN_1401bb4f0` per-file loop, then performing post-pass bookkeeping and returning.
2. Fresh GOG query `FUN_1401be290` has 90 direct and 12 indirect call sites. Its decompilation calls `FUN_1401bb4f0` for file record processing and later `FUN_1401bdf20` for the type-indexed pass. Its only direct code caller is `FUN_1403753b0`.
3. Fresh query `FUN_1403753b0` has three direct calls, zero indirect sites, and no direct code callers in the analyzed project. Its body calls path helper `FUN_14033e470`; if accepted, it calls `FUN_1401be290` and then `FUN_1401bb490`. Its only incoming reference in the capture is a data reference in an unclassified function-metadata/table region.
4. The EV-0313 binding evidence associates `FUN_14034de90` with the `Quest.SetStage` callback row, but its initialized table reference is data, not an indexed code callsite. No class-identified pre-finalization event/callback dispatch was found in the bounded loader traces.

## Assessment

The captures establish that both inspected file-load paths perform their QUST-inclusive finalization pass after their per-file record work. They do not establish the temporal position of the first natural callback relative to the completion/return of those paths. H1 and H2 remain proposed. No level-one bypass, target quest reachability, Steam behavior, or functional access result is established.

## Remaining discriminant

Resolve the metadata/table owner for the `FUN_1403753b0` reference and any startup scheduler connection only if receiver/class provenance is available. The exact Steam test requires a clean level-one start and read-only observation of post-load completion, the first natural SetStage callback target, `TESQuest+0xDC.0/+0xE0`, running/stage, and aliases under the complete target order [EV-0260].
