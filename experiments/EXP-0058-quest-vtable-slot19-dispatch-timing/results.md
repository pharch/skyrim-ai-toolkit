# Results

## Finding

EV-0318 supports GOG AE 1.6.1179.0 load-finalization dispatch of TESQuest vtable slot 19 after QUST parsing and registration. The QUST parser is TESQuest vtable entry 6 (`FUN_1403c7a50`, RVA `0x3C7A50`); slot 19 (`FUN_1403c8420`, RVA `0x3C8420`) can clear `TESQuest+0xDC.0` [EV-0316], [EV-0318].

## Direct call chain

1. `FUN_1401b9510` processes eligible source-file nodes by calling `FUN_1401bb4f0`; after its file loop it calls `FUN_1401bdf20` [EV-0318].
2. `FUN_1401bb4f0` iterates file records and dispatches them through `FUN_1401bb8d0`. The new-form path calls `FUN_1401b1020(form, recordBuffer)` and then registers the form with `FUN_1401b12f0` [EV-0318].
3. Disassembly of `FUN_1401b1020` preserves the form in `RCX` and the record buffer in `RDX` through `CALL qword ptr [RAX + 0x30]` at GOG VA `0x1401B1041`. TESQuest vtable entry 6 at RVA `0x17E7D40` resolves to the QUST parser `FUN_1403c7a50` [EV-0318].
4. `FUN_1401bdf20` iterates FormType-indexed manager arrays for values `0..0x89`, skipping `0x13`, `0x47`, and `0x5B`. For every object in each included array it invokes vtable `+0x98`. SKSE `FormType.psc` maps `kQuest` to decimal 77 (`0x4D`), so registered TESQuest objects are included [EV-0318].

## Model outcome and limits

H1's GOG load/finalization component is supported. H2, defined as slot 19 being invoked only during a later quest lifecycle transition, is falsified for this build. The slot-19 sweep follows file record parsing and registration. The first natural `Quest.SetStage` callback's timing relative to this manager pass is not directly captured; describing the pass as preceding that callback remains a load-order inference.

The whole-program `+0x30` screen reports 27,290 object-relative accesses and prints only the first 2,048. It does not support a global negative about other slot-6 sites. The selected class-specific call path is instead established by the function and vtable captures. No Steam RVA transfer, runtime quest state, callback reachability, alias fill, useful access, level-one transition, or OBJ-2 causal edge is established. The required exact-target Steam observer remains a read-only before/after capture of the target quest's `+0xDC.0` around natural file load and natural callback delivery, with complete active order.
