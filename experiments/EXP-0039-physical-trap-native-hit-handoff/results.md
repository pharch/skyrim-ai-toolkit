# EXP-0039 results

## GOG caller context

In the hash-attested GOG 1.6.1179.0 project, the only observed direct caller of `FUN_1406bcaa0` is `FUN_1406bb690`. The latter is reached from event-dispatch case 11 in `FUN_140659160` and from `FUN_1407ba3e0` after an Actor vtable state predicate and process-target comparison. These direct caller traces do not identify an ordinary physical attack or a trap source. The existing query's address and decompilation checks do not enumerate indirect callers ([EV-0291]).

## Vanilla trap route

Skyrim.esm ACTI `00079923` `TrapFallingRockLg01` attaches `PhysicsTrap` and `PhysicsTrapHit`. Its VMAD gives `LvlDamage1`–`LvlDamage6` values 20, 26, 30, 36, 44 and 50, with thresholds 6, 10, 14, 18 and 22. The PEX resolves an encounter level, selects a damage tier, and assigns the result to the `PhysicsTrapHit.damage` property. `PhysicsTrapHit.OnTrapHitStart` checks summed squared impact velocity against `damageVelocityThreshold` (default 6), checks ghost/faction conditions, then calls `ProcessTrapHit` on `akTarget` with the trap reference, damage, pushback and impact data. `TrapHitBase` extends `ObjectReference` and also calls `ProcessTrapHit`; the local `ObjectReference.psc` declares it `native` ([EV-0292]).

The captured PEX bodies contain no direct `DamageActorValue`, `DamageAV` or `UseSkill` call. The actual damage/mitigation behavior is inside the unresolved native implementation. The configured positive damage values do not prove positive live damage, effective armor mitigation, HitData creation, or an AVSK delta.

## GOG native binding and receiver route

The exact `ProcessTrapHit` literal has one occurrence in initialized GOG memory and a data reference inside `FUN_140a33590`. That registration constructs the `ObjectReference.ProcessTrapHit` native and stores `FUN_140a30e80` as its implementation. The implementation dispatches through receiver virtual slot `0x58`; the GOG Actor and PlayerCharacter vtables map that slot to `FUN_140679da0`. This route calls `FUN_1407dd110` before the distinct receiver handler `FUN_1406b9df0`. `FUN_1407dd110` calls `FUN_1407ddf50`, independently identified as common HitData population/resistance work including armor-related calculations (EV-0261, EV-0293).

The captured `FUN_1406b9df0` body has a conditional AV15 Sneak `UseSkill` call through Actor slot `0xF7`. The bounded body/helper screen did not identify AV11/AV12, but it does not cover all descendants or indirect dispatch. EV-0291 separately found only `FUN_1406bb690` as an observed direct caller of `FUN_1406bcaa0`.

## Receiver convergence and conditional Health damage

A fresh GOG query found direct calls into `FUN_1406b9df0` from both the ProcessTrapHit PlayerCharacter handler `FUN_140679da0` and the known inline receiver resolver `FUN_1406bcaa0`. The latter's captured body executes its AV11/AV12 receiver branch before its later `FUN_1406b9df0` call; the trap route reaches `FUN_1406b9df0` directly after common HitData construction ([EV-0222], [EV-0293], [EV-0294]).

`FUN_1406b9df0` reads HitData `totalDamage` at `+0x50` and conditionally calls `FUN_1406b49d0` with a computed value. That helper dispatches Actor slot `0x104` (`HandleHealthDamage`, EV-0217) when the selected ActorValue is Health (`0x18`, EV-0218) and its delta is negative. `FUN_1406bc140` and `FUN_1406bc400` also contain conditional Actor slot `0xF7` calls with AV15 in their Sneak branches; `FUN_1406be430` has no identified skill-use call in its captured body (EV-0294). This establishes a static conditional health-damage route and a direct-call-chain convergence after the known armor/Block resolver, not positive live damage or protection.

## ActorValue callback and HealthDamage descendants

The complete outgoing-edge census of `FUN_1406b9df0` found 89 direct callsite edges and 28 unresolved indirect callsites. Its direct call list contains no edge to `FUN_1406bcaa0`. The handler's visible virtual call at byte offset `0x7B8` is Actor::UseSkill slot `0xF7` and passes AV15 in the Sneak branch. Other indirect callsites remain unresolved and are not covered by this negative.

`FUN_1406b49d0` writes the selected ActorValue and calls `FUN_1406b4c70`, which invokes a function pointer from the table at `0x14319b880` indexed by that value. The static pointer bytes are zero, but startup code clears and then populates the table. It assigns AV11 and AV12 to `FUN_1406b65c0`, a callback that tail-dispatches Actor vtable slot `0xCA`. The base Actor target is a `RET`; the PlayerCharacter target `FUN_140729110` writes `-1.0` to fields at `this+0x270` and `this+0x274`, then calls `FUN_1406d2850(this+0x208, 0x27)`. The selected chain does not contain `UseSkill` or return to `FUN_1406bcaa0` (EV-0295).

Health AV24 is initialized to callback `FUN_1406b6050`. Its selected body and PlayerCharacter `HandleHealthDamage` target `FUN_1406bbb80` were screened with full direct-call-edge output and up to eight direct-callee decompilations; no AV11/AV12 `UseSkill` or return to `FUN_1406bcaa0` was identified in those branches (EV-0295). This supports H2 only for the mapped ActorValue callback and HealthDamage route. It does not resolve the other virtual calls in `FUN_1406b9df0`, prove that the callback path executes in a live trap hit, or show positive final damage, effective armor protection, unchanged AVSK, Steam equivalence or vanilla reproduction.

## Actor and PlayerCharacter receiver-slot targets

The EV-0295 `FUN_1406b9df0` census shows the `param_1` Actor receiver using slots `0x99`, `0x5C`, and `0x70`; the separate visible `UseSkill` dispatch is slot `0xF7` with AV15. Actor slot `0x99` previously resolved to `FUN_140677100`, a masked state-bit predicate at `this+0xC8` (EV-0291). The new PlayerCharacter slot-`0x99` query resolves to the same target.

Actor and PlayerCharacter slot `0x5C` both resolve to `FUN_1406c4300`. It retrieves a cached per-actor pointer or initializes/allocates a context and calls `FUN_1405b2a70`, whose decompilation writes `ActorMagicCaster::vftable`. The three direct callees of the target are initialization/allocation/constructor helpers. Actor slot `0x70` resolves to leaf `FUN_1402e55a0`, which returns thread-local or object state. PlayerCharacter slot `0x70` resolves to `FUN_140737170`, which reads slot `0x71` and then delegates to `FUN_1402e55a0`; PlayerCharacter slot `0x71` is leaf `FUN_14075a650`, returning bit 0 from `this+0xBE3` (EV-0296).

The selected target bodies and captured direct callees contain no AV11/AV12 `UseSkill` call or direct edge to `FUN_1406bcaa0`. This supports H2 only for the mapped receiver slots and bounded call depth. The ActorMagicCaster object-provider is now a concrete follow-up branch; it does not itself prove spell application or a skill award. The other indirect receiver objects in the 28-site census remain unclassified and are not covered by this result.

## ActorMagicCaster update methods

The matching GOG Address Library resolves `VTABLE::ActorMagicCaster` to RVA `0x187CCF0` (EV-0297). `FUN_1406b9df0`'s slot-`0x5C` provider returns this context object; the trap handler passes HitData `+0x38` to `FUN_1405c0b30`, which stores the pointer at `this+0x28` and dispatches ActorMagicCaster slots `0x14` and `0x10`.

Slot `0x14` resolves to `FUN_1405b4040`, which checks owner/state fields and either clears two caster fields or calls `FUN_1405c0cb0`. That helper reads a value through a nested virtual call, checks ActorMagicCaster slot `0x16`, gets its owner through slot `0x0C`, and calls leaf `FUN_14041af40`, a global scalar multiply/add. Slot `0x10` resolves to `FUN_1405b4a60`, which can update an integer in a global player-caster list. Slots `0x0C` and `0x16` are leaf owner/flag readers. None of these selected bodies or bounded direct callees shows AV11/AV12 `UseSkill` or direct return to `FUN_1406bcaa0`.

The concrete subtype of the pointer supplied from HitData `+0x38` is not established. A candidate `VTABLE::MagicItem` base query resolves slot `0x57` to `_purecall`, so that result does not supply the runtime target. Nested virtual calls at byte offsets `0x298`, `0x320`, and `0x2B8` remain unresolved; this is a bounded ActorMagicCaster branch result, not a whole-function descendant negative.

## Model status

- **H2, “trap damage skips HitData construction”: falsified** for this GOG PlayerCharacter route; the binding reaches common HitData construction and armor-related calculation before receiver handling.
- **H1, shared HitData and armor-XP route:** shared HitData/armor-calculation construction is supported. No AV11/AV12 call was identified in the mapped callback, HealthDamage, or Actor/PlayerCharacter receiver-slot screens; remaining indirect receiver objects are unresolved.
- **H2, skips HitData builder: falsified** for the traced GOG PlayerCharacter route.
- **H3, shared builder and separate receiver handler: supported** as the observed path shape. The handler has a conditional HitData-derived Health-damage path; mapped slot targets show no AV11/AV12 award, but the full dynamic route and live effect are not settled.
- **Q-0036-H2, ActorMagicCaster methods are state/effect setup with no armor-credit route: supported** for the queried GOG methods and captured direct call depth. Q-0036-H1 is falsified for those selected targets; unresolved nested subtype dispatch is not included.

This is static path classification, not a positive live-damage measurement, effective protection, a zero-armor-XP result, a profile-specific result, or a vanilla reproduction. The HitData `+0x38` subtype and other indirect receiver objects remain for selective tracing; Steam target mapping and live AVSK/protection measurements remain outstanding.
