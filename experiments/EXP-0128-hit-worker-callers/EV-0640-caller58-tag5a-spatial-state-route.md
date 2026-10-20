# EV-0640 — Caller 58 tag-0x5A spatial-state update

## Competing models and discriminants

- H1, spatial/physics state: tag 0x5A updates a handle-keyed coordinate record after a geometry or object-state predicate. It predicts the Player/object coordinate reads, shared manager collection, Actor threshold producer, and Havok contact-list producer.
- H2, progression/quest gate: the threshold or callback changes level eligibility or starts level-gated content. It predicts a Player-level comparison or a producer-backed edge into a mapped Story Manager/quest-start transition.
- H3, incoming-hit/armor route: the event reaches HitData, effective protection, AV11/AV12, or UseSkill. It predicts a producer-backed edge to those mapped sinks; the handler's unresolved virtual calls alone are not sufficient.

## Direct GOG evidence

All captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. No GOG RVA transfers to Steam AE 1.6.1170.0.

- FUN_140658dd0 writes tag 0x5A with a dword copied from an object and one boolean byte, then queues through FUN_14065b800 [EV-0640]. Worker case 0x5A resolves the object handle and calls FUN_1405259c0 with the manager DAT_1420f9d78 and the byte [EV-0637], [EV-0640].
- FUN_1405259c0 has five direct calls and 13 unresolved indirect sites. When the handle resolves and the boolean is true, it reads PlayerCharacter position at +0x54/+0x58 and the resolved object's +0x54/+0x58/+0x5C coordinates, creates or updates a record in the manager's keyed collections, and stores coordinate-derived floats. A null handle or false boolean follows a cleanup/removal branch. Its dynamic manager callbacks are unresolved [EV-0640].
- One producer is FUN_140686320, verified as primary VTABLE::Actor slot 0x9C (+0x4E0) under RTTI type .?AVActor@@ and subobject offset zero. The method checks object-form type bits, Actor process presence, two process virtual results, and a float threshold derived from FUN_1406751a0(Actor), Actor+0x5C, and a scale constant. It queues tag 0x5A with an object identifier and the threshold result [EV-0640]. Its sole analyzed direct caller is FUN_140731e80; that method compares a supplied float with a geometry-derived value and calls FUN_1405257b0 on the same manager. FUN_140731e80 itself has no analyzed incoming direct caller; its owner remains unknown [EV-0640].
- The second producer FUN_14051df20 removes a matching object/member from a keyed manager collection and may emit tag 0x5A with a false byte while cleaning the last entry. One of its four analyzed direct callers, FUN_14051d8c0, builds an hkpAllCdBodyPairTempCollector and processes collision-body pairs before calling this helper. Other callers include FUN_14051e3b0, FUN_14051e650 and FUN_14051f800; their wider runtime roles remain open [EV-0640].

## Result and limits

H1 is supported for the bounded spatial/coordinate-state path. H2 is not supported by the captured bodies: no Player-level predicate or mapped quest-start edge appears. H3 has no mapped direct HitData/protection/AV11/AV12/UseSkill sink, but 13 manager virtual sites and descendants remain unresolved. The result is not a vanilla level-one bypass, effective-protection/armor-XP result, Steam result, or bounty resolution. No OBJ-1/OBJ-2 causal edge is added.

## Next action

Continue the exact worker-caller census at caller 59/62, FUN_140658e10; keep the manager virtual sites scoped and prioritize any caller with an explicit level or combat/skill discriminator.
