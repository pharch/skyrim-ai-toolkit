# EV-0633 — Shared global tuple has distinct direct consumers

## Competing models and discriminants

- H1: caller 50 fallback construction and caller 51's queued callback use the same tuple as one shared registration/update mechanism. It predicts a shared helper path or matching direct field transformation.
- H2: the adjacent global dwords are reused as common configuration input in distinct mechanisms. It predicts different direct consumers and context-specific field handling, while leaving scalar meanings unresolved.

The discriminants are the exact direct call graph and field copies in `FUN_140cb4ae0` and `FUN_1402c6810`, caller 50's fallback arguments, and the bounded address query for `DAT_1432740d8`.

## Direct GOG evidence

Three captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project, verified SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Queries were read-only with auto-analysis disabled; they did not import or overwrite the project. These GOG addresses are not transferred to the separately verified Steam AE 1.6.1170.0 executable.

- `FUN_140cb4ae0` has four direct callees and no unresolved indirect call site in its body. Its queueing path allocates an event record, copies all three dwords from `param_7` to record dwords `+0x20`, `+0x24`, and `+0x28`, retains a separate object pointer, and submits the record through `FUN_140cbc770`. Its analyzed incoming callers include `FUN_140cb41c0`, which supplies `DAT_1432740d8` [EV-0633]. The helper has 42 call edges across 39 caller functions.
- Caller 50's factory `FUN_1402c6810` is a separate function with 26 direct call edges, two unresolved virtual sites, and two analyzed direct caller functions. Its caller `FUN_1402c65b0` copies `DAT_1432740d8`, `+4`, and `+8` into a local three-dword input, then invokes the factory with second argument zero [EV-0626], [EV-0633]. The false/fallback factory path copies the first two dwords to fields passed by `FUN_140e854e0`; it sets the third field to zero. The factory's other construction branch assigns the third input dword. The full semantic names of the three fields are not established.
- A bounded address-context query for image RVA `0x32740d8` reports 1,349 xrefs to the first dword, but no instruction context or initialized scalar values [EV-0633]. This does not identify the tuple's values or names.
- The two direct helper paths and field transformations differ. The evidence falsifies the specific shared-direct-registration/update model; it supports reuse of the same adjacent storage by distinct callers only. Caller 51's dynamic virtual callbacks and any transitive relation remain unresolved.

## Result and limits

H2 is supported for the captured direct call paths; H1's shared-direct-primitive prediction is falsified. The `DAT_1432740d8..+8` values and schema remain unknown. The result adds no causal edge to HitData, effective armor protection, AV11/AV12, UseSkill, armor XP, or OBJ-1 quest/encounter gates; it does not resolve Q-0079 or the bounty.

## Next action

Continue worker caller 52/62 at `FUN_140658be0`, record its exact tag and producer, and resume independent caller review.
