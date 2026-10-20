# EV-0636 — Caller 54 tag-0x54 spatial/context route

## Competing models and discriminants

- **H1, combat/armor route:** the Actor+0x128/context payload or a descendant of the tag-0x54 handler reaches HitData, effective protection, AV11/AV12, or UseSkill. It predicts a producer-backed direct/virtual call or data edge from this payload into one of those mapped sinks.
- **H2, spatial/context update:** the producer selects tag 0x54 from process and world-grid predicates; the dispatcher enters a broad Actor update handler and its nested-state helpers. It predicts the observed coordinate tests, Actor/context payload, worker-gated state callbacks, and no mapped direct HitData/armor-skill sink.
- **Cross-domain identity remains a separate question:** Actor slot +0x380 reaches the same FUN_1402e55a0 used by the HitData receiver, but shared code alone predicts neither the same runtime pointer nor a causal hit/XP effect. A verified different owner/type or disjoint continuation would falsify a shared-object model; a same-pointer trace followed into a common HitData/ActorValue continuation would support it.

The discriminants are the builder payload, producer branch predicates, dispatcher target, complete direct/indirect census, the exact Actor slots and the immediate/deferred tag-0x32 continuation.

## Direct GOG evidence

All queries use the existing GOG SkyrimSE.exe Ghidra project for ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Adapter metadata confirms read-only operation with auto-analysis disabled, no import or overwrite, and matching program identity. GOG RVAs are not transferred to Steam AE 1.6.1170.0.

- FUN_140658c50 writes tag 0x54, retains the supplied Actor, and stores zero plus a producer-selected fourth field before submitting the record to FUN_14065b800. Its sole direct producer is FUN_14066b6e0 [EV-0636].
- In FUN_14066b6e0, the first branch requires a nonnull Actor+0x60 object with its byte +0x40 bit 0 clear and Actor flag bit 13 clear. It passes Actor coordinates at +0x54/+0x58 to FUN_1402bec30; a false result calls the tag-0x54 builder. The helper is a no-call predicate: after its +0x40 bit-0 and +0x10 bit-13 checks, it compares the floored horizontal coordinates against a pair of dwords at receiver +0x68 using a 0x1000 shift [EV-0636]. This is a spatial/process-grid interpretation of the field use, not a record-name or gameplay claim.
- On the alternate Actor+0x10 bit-13 branch, FUN_14019ca70 tests horizontal coordinates against a rectangle derived from fields +0xb0/+0xb4 and global DAT_141fd7eb0, unless its +0xc0 pointer is nonzero. In FUN_14066b6e0 this predicate selects other gated worker/direct callbacks; it does not construct tag 0x54 [EV-0636]. The global's concrete type is unknown.
- Dispatcher case 0x54 passes the retained Actor and both queued fields to FUN_1402eb6f0. That target has a complete 63-direct-edge census and 21 unresolved virtual sites. Its captured direct body has no mapped call to the HitData handlers, protection, AV11/AV12, or UseSkill; this is a bounded direct-body result, not a transitive negative [EV-0636].
- The target also has a shared-gate branch that either queues tag 0x32 with Actor and its slot-0x380 context result or, when the gate is clear, invokes Actor slot +0x328 immediately. The retained-context builder FUN_140657f00 adds reference counts for both pointers [EV-0636]. Dispatcher case 0x32 checks the retained/current context, calls FUN_140e88c50 when the current getter returns null, releases the retained reference, then invokes the same Actor slot +0x328 [EV-0636]. The RTTI-verified primary Actor table maps slot 0x65 (+0x328) to FUN_140666770 [EV-0400], [EV-0635]. Its bounded body clears nested state, calls the TLS/nested selector FUN_1402e55a0, and can enter FUN_140e88c50; one virtual site at +0x538 remains unresolved [EV-0636].
- The same FUN_1402e55a0 is primary Actor slot +0x380 and is used by the GOG HitData receiver FUN_1406b9df0 [EV-0512], [EV-0295], [EV-0296]. Caller 54's target reads a nested object's +0x18 state after the selector; the bounded tag-0x32 cleanup path reaches FUN_140e88c50, the recursive object-tree helper mapped on tag 0x3C [EV-0483]–[EV-0486]. These are verified shared-code paths, but no concrete same-pointer result or downstream HitData/armor/skill effect is captured.

## Cross-domain synthesis and result

Model H2 is supported for the captured direct route. The verified connections are code reuse from the tag-0x54 Actor update into the shared TLS/nested selector and recursive object-tree helper; the HitData connection remains a code-reuse edge, not a causal edge. The same returned object, event semantics, and runtime scheduling are not observed. Keep Q79-H46 proposed and update Q79-H47 as the supported conservative shared-helper model.

One of the target's 21 virtual sites, the slot-0x65 target's +0x538 call, and recursive descendants remain open. No causal edge is added to HitData, protection, AV11/AV12, armor skill XP, or OBJ-1 quest state. The clean Steam matched-hit/protection/raw-AVSK test remains outstanding [EV-0260].

## Next action

Continue caller 55/62, FUN_140658c90, with an exact producer/tag/payload trace.
