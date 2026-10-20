# Expected discriminants

1. Build identity: every fresh query must attest the existing GOG AE 1.6.1179.0 binary hash, read-only mode, and disabled auto-analysis.
2. Builder dataflow: the caller's HitData initialization and argument registers must identify the PlayerCharacter receiver; direct writes in the builder and called helper bodies must cover `+0x18` and `+0x1C`.
3. Handler dataflow: the two first refcount-gated slot `+0x8` calls must be tied to their local handle sources and branch conditions.
4. Receiver class: the handle table's owner offset and the PlayerCharacter `+0x20` secondary-vtable writes must identify the slot `+0x8` thunk and slot-0 target.
5. XP boundary: direct calls can be classified, but unresolved virtual sites must remain explicit. No absence claim is warranted while teardown descendants are unresolved.
6. Gameplay boundary: only a matching Steam AE 1.6.1170.0 test with positive damage, effective protection, controlled hit counts, and raw Armor AVSK can establish the requested functional behavior.
