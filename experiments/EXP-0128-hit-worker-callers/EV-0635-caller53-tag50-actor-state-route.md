# EV-0635 — Caller 53 tag-0x50 Actor state route

## Competing models and discriminants

- H1: tag `0x50` is part of an ordinary player-hit/effective-armor/armor-skill path. It predicts a producer-backed HitData/protection/AV11/AV12/UseSkill data or control edge, or a recipient path that performs this work on the PlayerCharacter.
- H2: tag `0x50` is an Actor/process state callback that is queued from an Actor virtual method and enters a separate state/update routine. It predicts an Actor-vtable producer, object-pointer payload, process-state predicates and no direct mapped HitData/armor-skill sink.

The discriminants are the exact builder payload, dispatcher callee, producer vtable identity and slot, target's direct/indirect call census, and its guard against the PlayerCharacter receiver.

## Direct GOG evidence

The captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project with verified SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Queries were read-only with auto-analysis disabled and did not import or overwrite the project. These GOG RVAs are not transferred to Steam AE 1.6.1170.0.

- Builder `FUN_140658c10` writes tag `0x50`, increments the retained object's reference count at `+0x28`, and queues the object through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_140664cf0` [EV-0635].
- `FUN_140664cf0` has no analyzed direct code callers. It is referenced as a function pointer at GOG address `0x14189f068` in the already identity-validated primary `VTABLE::Actor` table RVA `0x189ec20` [EV-0400], [EV-0635]. A bounded pointer capture beginning at RVA `0x189f020` confirms this is zero-based Actor slot `0x89` (`+0x448`). It excludes global `DAT_143138a98` and objects with bit 11 set at `+0x10`, then queues the remaining object [EV-0635].
- Dispatcher case `0x50` reads the object pointer from payload `+0x8` and calls thunk `FUN_140664d20`, which jumps to `FUN_1402ec610` [EV-0635]. This is the handler for the Actor-slot producer's retained pointer.
- `FUN_1402ec610` has 51 direct call edges and 17 unresolved virtual sites. Its entry guard skips the body if receiver flag bit 11 is set or the receiver equals `DAT_143188918`; that global is independently identified as PlayerCharacter [EV-0344]. Its remaining direct body compares Actor/process state, updates process/resource/object state, and calls helpers including `FUN_1406c21c0` and `FUN_14073a380`. No mapped HitData/protection/AV11/AV12/UseSkill direct target appears in the captured body [EV-0635].
- An initial RTTI query incorrectly treated interior Actor slot RVA `0x189f060` as a vtable start; its invalid COL bytes are superseded by the correct table-base/slot capture [EV-0635]. The separate data references to `FUN_1402ec610` do not establish its exact vtable slot or class. Keep its dynamic descendants open.

## Result and limits

H2 is supported for the captured direct route. The producer is an Actor primary-vtable method, and the worker handler skips PlayerCharacter receivers before performing its Actor/process state work. H1 has no direct support in the captured body. The handler still has 17 unresolved virtual sites, so this is not a global no-hit result; it does not establish Steam behavior, effective armor protection, armor XP, or a vanilla exploit. Caller 53 is closed as a bounded actor-state route, with no causal OBJ-2 edge.

## Next action

Continue with worker caller 54/62 `FUN_140658c50` and record its exact tag, payload and producer.
