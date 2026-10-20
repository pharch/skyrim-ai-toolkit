# EV-0641 — Caller 59/tag-0x5B disarm-related Actor action

## Competing models and discriminants

- H1, deferred Actor action with a disarm-related player outcome: the tag carries two handles into an Actor method that reports “You have been disarmed.” when its receiver is the PlayerCharacter global. It predicts the exact dispatcher call and player-global message branch.
- H2, level-gate or armor-XP/protection mechanism: the event or its Actor virtual descendants directly inspect player level, start a gated quest/encounter, change effective armor protection, or reach HitData/AV11/AV12/UseSkill. It predicts a mapped direct call or producer-backed state edge to those systems; a disarm message alone does not support it.
- H3, immediate/deferred parity: the producer's immediate helper converges on the tag-0x5B handler. It predicts a direct path from FUN_1405aed00/FUN_1405b0730 to FUN_14067aea0 with equivalent resolved handle arguments.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. All query metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. This build is distinct from Steam AE 1.6.1170.0; no GOG RVA is transferred to Steam.

- Caller 59 `FUN_140658e10` writes worker tag 0x5B and copies one dword from each of its two payload arguments before enqueueing through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_1405b93a0`. The producer resolves the object stored at `param_1+0x50`, tests bit 13 at the resolved object's `+0xCC`, derives the two payloads through `FUN_140676b60` and `param_1+0x34`, queues tag 0x5B, then calls `FUN_1405aed00(param_1,0)` [EV-0641].
- Dispatcher case 0x5B resolves both stored dwords as object handles and calls `FUN_14067aea0(resolved_first,resolved_second)` [EV-0641]. In the successful-result branch, `FUN_14067aea0` invokes the primary Actor virtual slot `+0x658` with a form/object and context arguments, continues object/effect and manager updates, and emits the literal “You have been disarmed.” message when the first Actor pointer equals `DAT_143138a98` [EV-0641].
- The primary Actor vtable is independently identified at GOG RVA 0x189EC20 [EV-0400]. A bounded continuation capture from `0x189F020` reaches absolute table slot 0xCB (`+0x658`) at RVA 0x189F278, whose function pointer is `FUN_14067a400` [EV-0641]. That method has 25 direct call edges and 16 unresolved indirect sites. Its captured direct body contains no explicit Player-level comparison or mapped direct HitData, effective-protection, AV11/AV12, or UseSkill call [EV-0641].
- The producer's immediate `FUN_1405aed00(param_1,0)` path sets/tests state bit `0x40000` and can tail-call `FUN_1405b0730(param_1,0)`. The bounded helper/worker captures do not call `FUN_14067aea0`; direct immediate/deferred handler convergence is therefore not established. `FUN_1405aed00` has 37 analyzed incoming caller functions, so its meaning is broader than this producer [EV-0641].

## Result and limits

H1 is supported for the captured deferred route: the PlayerCharacter branch's explicit message identifies a disarm-related outcome, and the dispatch target applies a primary Actor virtual operation. H3 is not supported by the bounded direct path; the immediate helper performs separate state/update work. H2 has no mapped direct level, quest-start, HitData, protection, AV11/AV12, or UseSkill edge in the captured bodies, but 16 virtual sites in `FUN_14067a400`, deeper descendants, and runtime effects remain unresolved. This is not a vanilla level-one bypass, armor-XP result, effective-protection result, Steam result, or bounty resolution. No OBJ-1/OBJ-2 causal edge is added.

## Next action

Continue the exact worker-caller census at caller 60/62, `FUN_140658e50`; prioritize explicit level/quest and armor protection/skill discriminants while retaining the two remaining uninspected callers and Q-0079's independent open status.
