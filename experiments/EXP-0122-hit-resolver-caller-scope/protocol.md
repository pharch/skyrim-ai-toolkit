# Read-only procedure

1. Confirm the configured analysis binary remains GOG AE 1.6.1179.0 and query only the existing Ghidra project with auto-analysis disabled and read-only mode.
2. Capture function `FUN_1406bb690` with a complete direct-call-edge census and decompilation; record each observed direct call to `FUN_1406bcaa0`.
3. Capture `FUN_140659160` and identify the exact case that calls `FUN_1406bb690`, including the data fields passed at that case.
4. Capture `FUN_14065b800` to determine the direct dispatch relationship and whether the dispatcher is called after a callback declines to consume its event.
5. The original incoming-caller query requested up to 32 additional caller decompilations and stored at most 64 unique caller functions. EV-0423 verifies 95 direct callers, 33 decompiled bodies including the separately selected caller, and 62 remaining. Preserve those exact limits and do not treat the returned subset as exhaustive.
6. Capture `FUN_1407ba3e0`, its direct callers, and its data-reference context. Record the exact Actor state predicate and process-target comparison without assigning an undocumented semantic name.
7. Compare only these bounded caller findings with EV-0222 and EV-0261. Do not infer all incoming-hit coverage, Steam code equivalence, protection, or XP results.
8. Preserve the clean Steam blocked/unblocked hit, effective-protection, and raw AV9/AV11/AV12 measurement as an external runtime discriminator under EV-0260.

## Controls

No game process, save, plugin, archive, or profile was modified. No live gameplay test was run. This was mechanism inference from a build-identified GOG executable, not Steam runtime evidence.
