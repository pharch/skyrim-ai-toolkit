# EV-0644 — Caller 62/tag-0x62 shared Actor reaction route

## Competing models and discriminants

- H1, a distinct serialized event reuses an Actor handler also reached from HitData: caller 62 writes tag 0x62, its sole analyzed producer is `FUN_1406c72d0`, and dispatcher case 0x62 calls `FUN_1406bc400`; the exact target also has a direct caller in mapped HitData handler `FUN_1406b9df0`. This predicts the producer, tag, dispatcher edge, shared target, and a bounded Actor/process response body.
- H2, tag 0x62 is itself an ordinary incoming HitData/AV11/AV12 continuation: this predicts that its producer or dispatcher forwards the mapped HitData context/resolver arguments or that the bounded target reaches the mapped armor-skill sink. A shared callee alone does not meet that prediction.
- H3, tag 0x62 changes level eligibility or effective armor protection: this predicts a mapped level/quest predicate or protection calculation in the producer/dispatcher/target path.

## Direct GOG evidence

The identity-checked read-only captures use GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`, with auto-analysis disabled. This project is separate from Steam AE 1.6.1170.0; no RVA transfers to Steam.

- Caller 62 `FUN_140658fb0` writes payload tag `0x62`, retains its two object arguments, stores the remaining scalar/pointer payload, and queues through `FUN_14065b800`. Its one analyzed producer is `FUN_1406c72d0`; the captured branch submits the tag after process/event filters and passes an object pair plus a value resolved from the producer context [EV-0644].
- Dispatcher case 0x62 resolves the queued payload fields and calls `FUN_1406bc400`. The builder tag is `0x62`, not `0x0B` [EV-0644].
- `FUN_1406bc400` has 39 direct outgoing calls and 13 unresolved indirect sites. Its three direct callers include dispatcher case 0x62, `FUN_1405bab90`, and mapped HitData handler `FUN_1406b9df0`. It calls `FUN_140672640` on several Actor/process-conditioned branches [EV-0644]. This establishes exact code reuse, not identity of caller arguments or event cause.
- `FUN_140672640` has 55 direct outgoing calls and five unresolved indirect sites. Its captured body checks receiver/target state, PlayerCharacter identity and Actor flags, traverses related Actor entries, and submits event code `0x2A` through a direct helper. Exact helper semantics and dynamic virtual effects remain unresolved [EV-0644].
- The bounded tag-0x62 producer/dispatcher/target bodies contain no explicit level or quest-start gate and no mapped effective-protection or AV11/AV12/UseSkill sink. The 13 and five unresolved virtual sites, deeper descendants, ordinary-hit coverage, and Steam runtime effects remain outside this evidence [EV-0644], [EV-0260].
- The underlying caller inventory is 95 unique direct callers into `FUN_14065b800`; 33 were decompiled in the earlier sample and the exact remaining partition contains 62 bodies. This is the final body in that remaining partition; the full 62-body/tag review still does not resolve the clean Steam matched-hit test [EV-0397], [EV-0423], [EV-0644].

## Result and limits

H1 is supported for the captured static call route: a distinct tag-0x62 producer reaches an Actor reaction handler that is also called from mapped HitData code. H2 is not established: caller 62 does not construct tag 0x0B, and the shared handler does not identify the same runtime event, HitData fields, or armor-skill side effect. H3 is unsupported by the bounded bodies. No level-one access, effective-protection result, armor-XP bypass, ordinary-hit result, Steam result, or bounty resolution follows. Record the within-event producer/dispatcher/handler relationship; add no OBJ-1/OBJ-2 causal edge.

## Next action

Verify the exact 95-function caller set and its 62-body remaining partition against the preserved identity-checked census, close Q-0079 as a bounded static caller review, and begin the highest-priority ready P0 line Q-0080. The live Steam matched-hit/protection/raw-AVSK test remains open under EV-0260.
