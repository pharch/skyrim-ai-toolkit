# Protocol

1. Use the strict Python dispatcher to query only the existing configured GOG project in read-only, no-analysis mode. Verify the exact executable identity in query metadata.
2. Inspect the fresh ProcessTrapHit wrapper, handler, handle-table helpers, PlayerCharacter primary and secondary vtables, and the resolved cleanup thunk. Preserve disassembly and decompilation with call-edge counts.
3. Read the preserved helper captures for `FUN_1407ddf50` and `FUN_1407df220`; compare their reads and writes against the initializer's eight-byte clear at HitData `+0x18/+0x1C` and the builder's receiver-derived `+0x1C` write.
4. Treat the first cleanup as route-specific and conditional. Treat `FUN_14072fd60`'s eight indirect sites as unresolved. Do not transfer GOG RVAs to Steam or infer a global no-award result.
5. Preserve raw captures in ignored `.local/`, register hashes and build identity in EV-0319's private local manifest, and keep reproducible interpretation and limits here.
6. Keep the exact Steam positive-damage, effective-protection and raw-AVSK experiment separate; no console forcing, injected scripts, or altered plugins can validate a vanilla candidate.
