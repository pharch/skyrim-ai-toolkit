# Protocol

1. Verify EV-0302's GOG executable SHA, Address Library SHA, read-only existing-project method and ten-site inventory before new queries.
2. Reuse `.local/ghidra/gog-query-20261016T144839Z.stdout.raw` to preserve the exact RVAs. Never transfer them to Steam 1.6.1170.0.
3. Resolve the `Actor +0xA0` vtable and slot `0x4` target at GOG RVA `0x1407de518`. Trace its return condition and the stores to HitData `+0x50`, `+0x58`, `+0x60`, and `+0x68` that follow it.
4. Resolve the object at `HitData +0x30`, its `+0xC0` subobject, and slot `0x4` call at GOG RVA `0x1407de2fc`. Identify the return-value use in the auxiliary `+0x5c` calculation without assuming the subobject type.
5. Confirm the ActorValueOwner calls at `0x1407de331`, `0x1407de34a`, and `0x1407de472` pass indices `0x42`, `0x09`, and `0xA3`. Inspect the call at `0x1407de113`, where the index is loaded dynamically from the object at `HitData +0x30`, offset `+0x194`.
6. Classify refcount release sites `0x1407de43e`, `0x1407de554`, and `0x1407de579` from their decrement/zero guards; do not treat a release target as a gameplay writer without contrary evidence.
7. Record every new query's exact target identity, command, metadata, stdout/stderr/log hashes and call-edge checks in the transaction capture manifest. Keep raw captures under ignored `.local/` and summarize only durable findings in tracked results.
8. Do not infer live protection or XP from GOG static output. The Steam clean-save test needs independent positive-damage, effective-rating/protection, and raw Light/Heavy Armor AVSK controls.
