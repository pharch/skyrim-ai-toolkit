# Protocol

## Objective

Determine whether the same ordinary incoming hit can receive physical armor mitigation from equipped armor, then miss AV11/AV12 skill credit because equipment changes before the resolver scans worn armor. Keep ordinary unblocked hits separate from the blocked AV9 branch and from the later `FUN_1406b9df0` health/trap route.

## Competing models and predicted discriminants

- **H1 — interposition window:** a synchronous callback, queued event drained inline, or player-accessible transition occurs between mitigation and the receiver's worn-ARMO scan. A GOG call-order trace should identify that code path; a verified Steam diagnostic run should then show a landed qualifying hit, positive armor-caused protection, unchanged raw AV11/AV12, and numeric level still 1 across repetitions.
- **H2 — one resolver pass:** mitigation and the unblocked receiver scan/UseSkill branch run synchronously within one hit-resolution pass, with no player input/yield between them. Synchronous perk entrypoint callbacks are bounded to numeric values for official selector rows; their typed virtual predicate must be inspected before making a universal side-effect claim. A clean Steam trace should show the same equipped state at protection and XP selection.
- **H3 — blocked-hit routing:** protection calculation may precede the blocked flag, but a blocked player-receiver hit selects AV9 Block and skips AV11/AV12. This predicts a distinct AV9 delta and no armor-skill dispatch on that branch. It remains a control route unless positive armor-caused protection, actual landed-hit qualification, Block XP, and both raw armor AVSK values are measured.

## Offline source procedure

1. Verify the GOG executable identity before any native interpretation: ProductVersion 1.6.1179.0 and SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Keep that project separate from installed Steam AE 1.6.1170.0.
2. Trace `FUN_1407ddf50` through its builder return and caller into `FUN_1406bcaa0`; record every direct call and indirect site between damage mitigation and the worn-ARMO/AV11/AV12 branch. Keep `FUN_1406b9df0` as a separate comparator.
3. Follow selector values 0x25/0x27 through the entrypoint visitor, PlayerCharacter list walk, entry-function dispatcher, and every function ID present in matching official-master PERK rows. Preserve raw rows and EPFD payloads.
4. Parse only Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm with the retained read-only TES4 parser. Do not resolve winners or describe this as a complete active order. Use CommonLib-generated documentation only for mutable enum/layout labels; retain its source note and uncertainty.
5. Preserve the correction that `PRKE` is the three-byte entry header. The initial screen mistakenly treated that header as the selector/function pair; the corrected screen reads selector from `DATA[0]` and the operation from `EPFT`. No result from the initial misparse is used.

## Runtime discriminator and action boundary

No in-game action is scheduled because the exact Steam profile/order, disposable verified level-one save, and read-only live Observer capture are unavailable [EV-0260]. Once those prerequisites exist, use a disposable copy and rollback point; log verified executable identity, full active order, level, armor type/slot/condition, incoming source, hit/contact outcome, pre/post Health and effective protection, raw Heavy/Light/Block AVSK, and sample completeness. Compare naked and equipped controls, blocked and unblocked attacks, both armor classes, enough repetitions to exceed display rounding, and a no-hit negative control. Do not use console, script injection, altered plugins, or save edits as vanilla-positive evidence.

## Evidence and interpretation

Raw captures and source hashes are recorded in EV-0670–EV-0676. Keep live measurement requirements attached to EV-0260. A static source result is mechanism evidence only; a blocked branch alone is not a qualifying positive result.
