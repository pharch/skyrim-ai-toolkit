# EV-0632 — Caller 51 tag-0x4b PlayerCharacter state route

## Competing models and discriminants

- H1: tag `0x4b` reaches a PlayerCharacter state transition and object-hierarchy update. It predicts a PlayerCharacter receiver, state-field predicates/writes, and bounded direct callees that are not the HitData/AV11/AV12/UseSkill sinks.
- H2: the same event is a hidden ordinary-hit or armor-skill route. It predicts a mapped HitData/protection/skill sink in the exact direct path, or a producer-backed dynamic call target that feeds one of those sinks.

The discriminants are caller/builder payload agreement, dispatcher receiver identity, RTTI-verified PlayerCharacter virtual slot targets, and complete direct/indirect call-site counts on the producer and its shared state helper.

## Direct GOG evidence

The four captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project with verified binary SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; queries were read-only, auto-analysis disabled, and performed no import or overwrite. GOG RVAs are not transferred to the separately verified Steam AE 1.6.1170.0 executable.

- Builder `FUN_140658b50` writes tag `0x4b` and one byte argument; its sole analyzed worker caller is `FUN_140738380` [EV-0632]. The worker dispatcher case `0x4b` calls `FUN_140738380(DAT_143188918, payload_byte)` [EV-0632]. The global is constructed with PlayerCharacter vftable, and PlayerCharacter slot `+0x378` returns `FUN_1407371f0` [EV-0344], [EV-0337].
- `FUN_140738380` returns through the event builder when shared gate `FUN_1406d4110` is set. Its clear-gate path obtains two objects from PlayerCharacter virtual slot `+0x378` with selectors 1 and 0; when the byte parameter is nonzero, PlayerCharacter slot `+0x4c8` gates the transition. It compares and changes bit 0 in both objects' `+0xf4` dwords and updates PlayerCharacter byte `+0xbe3`. It then builds paired state records, calls `FUN_140cb41c0`, iterates four pointers at PlayerCharacter `+0x1a8` through `FUN_1405b4900`, and reaches `FUN_140744180`, `FUN_140661f60` and a conditional `FUN_14074dd30` [EV-0632].
- The complete producer body has 12 direct edges and 10 unresolved virtual call sites; the complete incoming census reports 13 caller functions, including the worker dispatcher [EV-0632].
- RTTI-validated primary PlayerCharacter table RVA `0x18acd70`, slot `0x99` (`+0x4c8`), resolves to `FUN_140677100`. Its complete body checks `PlayerCharacter+0xc8 & 0x1e00000` against a small state-value set that depends on the byte argument, and has no direct calls or HitData/ActorValue/UseSkill sink [EV-0632].
- Recursive helper `FUN_1402df6d0` has three direct callees, two unresolved virtual sites and one recursive direct edge. Its bounded body walks a nested object collection, searches for a marker object, consults a keyed record bit at `+0x7a`, and on a match updates the selected object and calls `FUN_140e2bd10`; it has no direct HitData/protection/AV11/AV12/UseSkill edge [EV-0632]. The helper has multiple callers, so this is generic object-state infrastructure, not a tag-specific combat result.
- A cross-caller configuration lead remains: caller 50's fallback factory and caller 51's `FUN_140cb41c0` path both pass the same adjacent global tuple `DAT_1432740d8..+8` to different helpers [EV-0626], [EV-0632]. Its schema and relationship are unresolved; this observation adds no causal edge to armor or HitData.

## Result and limits

H1 is supported for the captured bounded static route. H2 has no direct support in this route and is narrowed: no direct mapped combat, HitData, protection, AV11/AV12 or UseSkill sink appears. Caller 51 is bounded for the worker-caller census, with dynamic virtual targets and deeper callback effects explicitly open. The result does not establish a global no-hit result, Steam behavior, effective armor protection, armor XP, or a vanilla exploit.

## Next discriminant

Query `FUN_140cb4ae0`, which receives the shared `DAT_1432740d8` tuple through `FUN_140cb41c0`. Compare that helper with caller 50's `FUN_1402c6810` route to determine whether the tuple participates in a shared keyed registration/update primitive or is only common static configuration. Preserve each caller's receiver and event context; do not infer a combat link from the tuple alone. Then resume worker caller 52/62.
