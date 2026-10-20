# Protocol

1. Read EV-0295 and EV-0302 plus the exact TX-20261016-0037 raw Ghidra captures and manifest. Extract the 28 unresolved `FUN_1406b9df0` sites, preserving callsite address, instruction, receiver/register context, and the query's direct/indirect classification.
2. Verify the captured executable and Address Library identities still match GOG AE 1.6.1179.0. Use the configured Ghidra project with `-process SkyrimSE.exe -noanalysis -readOnly`; do not import or reanalyze a binary and do not transfer RVAs to Steam AE 1.6.1170.0.
3. Rank sites by whether the call is through Actor/PlayerCharacter subobjects, an initialized callback table, or a generic function pointer carrying the receiver or HitData. Reuse valid captures; query only the highest-information unresolved families first.
4. For each target, follow fresh vtable/Address Library mappings or initialization stores to concrete targets. Capture disassembly, decompilation, direct callees, and bounded descendants. Search for `Actor::UseSkill` slot `0xF7`, the PlayerCharacter skill-progress sink, AV11/AV12 arguments, and any direct return to `FUN_1406bcaa0`.
5. Treat AV15 Sneak and AV9 Block as separate skills. A generic skill sink without a proven skill ID is unresolved, not an armor award.
6. Record every resolved, unresolved, and failed site with source identity and raw hashes. Do not claim all-handler absence while relevant dynamic or indirect targets remain.
7. Keep the runtime discriminator separate: exact Steam executable, complete target-specific load order, clean level-one save, positive unblocked trap damage, a protection control, and raw Light/Heavy Armor AVSK measurements with restoration and repetition. No console forcing, injected script, or altered plugin can validate a vanilla candidate.
