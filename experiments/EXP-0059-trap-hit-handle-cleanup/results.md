# Results

## Direct observations

1. The fresh GOG `FUN_140679da0` caller initializes HitData with `FUN_1407dcd60`, then calls `FUN_1407dd110` with the PlayerCharacter receiver in R8 / parameter 3.
2. The initializer clears eight bytes beginning at HitData `+0x18`. The builder writes a receiver-derived handle at `+0x1C`; it does not write the low DWORD at `+0x18`.
3. The captured bodies of `FUN_1407ddf50` and `FUN_1407df220` read/resolve handles but do not write HitData `+0x18`. On this captured ProcessTrapHit construction path, `+0x18` remains zero.
4. In `FUN_1406b9df0`, the first refcount-gated `+0x8` call at `0x1406BA047` uses `local_3c0`, resolved from HitData `+0x18`; its release is therefore skipped on this route.
5. The second refcount-gated release at `0x1406BA070` uses the handle derived from receiver `param_1`. The handle table recovers owner+`0x20`; the PlayerCharacter secondary table at RVA `0x18AD6F0` has slot 1 / `+0x8` targeting `FUN_140d28f40`.
6. `FUN_140d28f40` tail-dispatches secondary-table slot 0 with the disposal flag. PlayerCharacter slot 0 is adjustor thunk `FUN_140758824`, which subtracts `0x20` and jumps to `FUN_140758a60`. That function calls `FUN_14072fd60` and conditionally frees the `0xBE8`-byte object.
7. `FUN_14072fd60` has eight unresolved virtual sites. No direct armor skill-progress sink is established by the resolved thunk/adjustor path, but the teardown boundary remains open.

## Assessment

H1 is supported for the captured ProcessTrapHit construction route: the HitData-derived first cleanup is skipped, while the receiver cleanup conditionally reaches a PlayerCharacter teardown chain. H2 is falsified for that captured route because neither called builder helper writes `+0x18`. The evidence does not resolve whether an unresolved teardown descendant reaches armor skill progress. No global zero-XP claim, effective-protection result, Steam equivalence, active-profile winner, or vanilla reproduction is established. No OBJ-1/OBJ-2 causal edge is added.

## Remaining discriminant

Resolve the eight virtual sites in `FUN_14072fd60` only if class/dataflow evidence can identify their concrete targets without broadening into an unbounded whole-program search. Separately capture the exact Steam 1.6.1170.0 ordinary-hit protocol: repeated positive-damage attacks, effective armor protection, and raw Armor AVSK before/after. EV-0260 records the missing profile/save/Observer prerequisites.
