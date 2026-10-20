# Protocol

1. Verify GOG 1.6.1179.0 and matching Address Library identity for each Ghidra query; use the existing project in read-only/no-analysis mode.
2. Read EV-0324 and EV-0293/EV-0295/EV-0315 before querying. Resolve only indirect/descendant routes tied to HitData, ActorValue updates, player damage, armor, or slot 0x7B8.
3. Preserve unresolved virtual sites and distinguish direct edges, mapped vtable targets, inference, and live behavior.
4. Keep the Steam AE 1.6.1170.0 test separate. It requires a complete exact active order, disposable level-one save, raw AVSK before/after, positive damage, and effective protection; EV-0260 records the current readiness gap.
5. Do not use console forcing, injected scripts, or altered plugins as vanilla validation.
