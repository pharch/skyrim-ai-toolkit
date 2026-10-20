# Protocol

1. Reuse EV-0321's complete official-master `GetLevel` census and fixed official-source-layer comparison; verify the exact Skyrim.esm hash before targeted joins.
2. Decode the WE13 QUST record, event type, level CTDA, and aliases. Treat the serialized top-level condition as evidence about the record only until its parent/start transition is mapped.
3. Search the official masters for Story Manager parents/children, direct record references, alias-fill providers, and location/encounter placements. Preserve raw IDs and source hashes; do not infer profile winners.
4. Inspect `WEScript` and any alias/parent PEX only through the tested bounded base-Misc-BSA extractor. A missing stream is scoped to that extractor, not a complete archive/loose-file negative.
5. Distinguish quest scheduling, quest running state, alias fill, encounter actor enablement, and physical access. No console forcing, injected scripts, or plugin changes validate a vanilla exploit.
6. Keep the level-one player test as a separate natural-exploration/no-event control requiring a complete target order and read-only Observer.
