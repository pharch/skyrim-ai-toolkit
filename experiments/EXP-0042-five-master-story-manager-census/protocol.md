# Protocol

1. Use the strict Python dispatcher to query all `SMEN` and `SMQN` records from the exact five official master files. Preserve raw output JSON, source file hashes, record counts, and command errors under ignored `.local/`.
2. Decode each 32-byte CTDA function index at bytes 8–9. Use the version-pinned TES5Edit condition schema for type-byte comparison/flag interpretation: high nibble selects comparison, low bit `0x04` means Use Global, and function index 80 is GetLevel.
3. For every function-80 row, retain CTDA bytes, comparison constant or global FormID, Run On/reference, parent (`PNAM`), and child (`NNAM`) references. Resolve GLOB operands and QUST children using direct record queries; compare overrides in official load order.
4. Attempt native xEdit only for a limited set of exact promising records and label that separate evidence lane. Direct-parser results remain raw-file observations.
5. Rank a candidate only as a lead until its player-accessible route and level-one transition are tested against an ordinary no-trigger control, with numeric level and quest/encounter state captured and repeated.

The targeted child/global mapping also scans `SMBN` records so `PNAM` parent links can be classified where the parent is a branch node. The current source-copy scan observed 99 Skyrim.esm, zero Update.esm, 11 Dawnguard.esm, two HearthFires.esm, and 15 Dragonborn.esm SMBN records.
