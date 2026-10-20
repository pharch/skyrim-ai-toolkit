# EV-0634 — Caller 52 tag-0x56 retained-object/list route

## Competing models and discriminants

- H1: tag `0x56` is an ordinary incoming-hit or armor-skill path. It predicts a producer-backed HitData/protection/AV11/AV12/UseSkill target in the resolved recipient or its callback descendants.
- H2: tag `0x56` handles retained objects in a manager collection/lifecycle route. It predicts an object pointer payload, immediate/deferred calls to one object callback, and collection membership/refcount work under a manager context.

The discriminants are the builder/producer field agreement, dispatcher case, exact immediate/deferred virtual slot, direct/indirect call censuses for producer and manager helpers, and the only analyzed direct caller of the collection owner.

## Direct GOG evidence

The five captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project with verified SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Queries were read-only with auto-analysis disabled and did not import or overwrite the project. GOG addresses are not transferred to Steam AE 1.6.1170.0.

- Builder `FUN_140658be0` writes tag `0x56`, increments the retained object's reference count, and calls `FUN_14065b800`; its sole analyzed direct producer is `FUN_140778a20` [EV-0634].
- `FUN_140778a20` tests shared gate `FUN_1406d4110`. If queued, it submits the object through tag `0x56`; otherwise it invokes the object's virtual slot `+0x138` with the object as receiver and no explicit argument. Its body has two direct call edges, one unresolved virtual site, two callsites from one direct caller, and no other analyzed direct callers [EV-0634].
- Dispatcher case `0x56` reads the same retained object from the event payload, calls `FUN_140777f40(DAT_1420f7db0, object)`, then invokes that object's slot `+0x138`, again without an explicit argument. The deferred path therefore matches the producer's receiver/slot call, with an extra manager helper first [EV-0634]. The full dispatcher has many unrelated cases and 81 indirect sites; those counts are not attributed to case `0x56`.
- The wrapper's only analyzed direct caller function is `FUN_140774b80`, which walks a pointer collection at receiver `+0xe8`, calls the wrapper on each element, decrements object references, and clears the collection. `FUN_140774b80` itself is directly called by `FUN_140643ec0` with `DAT_1420f7db0` during a broad cleanup sequence [EV-0634]. This supports a lifecycle/collection interpretation for the captured producer source; treating the outer routine as shutdown remains an inference.
- `FUN_140777f40` has 12 direct edges, two unresolved virtual sites, and two analyzed caller functions. It checks object slots `+0x160` and `+0x180`, then uses locked manager collections at `+0x108`, `+0x128`, or `+0xe8` with keyed lookup/removal and an additional manager update. This is collection-membership/state work; object class and dynamic callback targets remain unknown [EV-0634].
- No mapped HitData/protection/AV11/AV12/UseSkill target appears in the captured tag-specific producer, wrapper, or manager helper direct edges. The object's slot `+0x138` is unresolved, so the result is bounded and cannot exclude a dynamic descendant.

## Result and limits

H2 is supported for the captured direct route. H1 has no direct support in the producer/manager path, but the recipient's `+0x138` virtual target and deeper callbacks remain unresolved. The evidence establishes immediate/deferred receiver-slot parity, not the callback's terminal behavior, effective protection, armor XP, Steam behavior, or a vanilla exploit. Caller 52 is reviewed as a bounded object-list/lifecycle path; Q-0079 remains open.

## Next action

Continue with worker caller 53/62 `FUN_140658c10` and record its exact tag, payload and producer.
