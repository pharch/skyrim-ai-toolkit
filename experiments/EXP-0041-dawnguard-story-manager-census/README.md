# EXP-0041 — Dawnguard Story Manager level-gate census

**Status:** Completed bounded direct-parser census. Exactly one `GetLevel` condition appears across the SMEN/SMQN records physically present in Dawnguard.esm: `DLC1VQ00Node`, which selects the Durak messenger helper.

**Question:** Do other Dawnguard.esm Story Manager nodes encode independent player-level gates for quests or encounters?

**Result:** The Dawnguard.esm file contains 36 SMQN records and one SMEN record. The sole function-index-80 (`GetLevel`) CTDA belongs to `DLC1VQ00Node`; its `>= 10` global operand and Durak helper child are mapped in EV-0298. The AM/PM vampire-attack nodes contain `GetGlobalValue`, not `GetLevel`. This closes only the Dawnguard.esm record-file census, not BSA script, dynamic, profile, or live gameplay routes.

See [hypothesis](hypothesis.md), [predicted outcomes](predicted-outcomes.md), [protocol](protocol.md), [results](results.md), and [implications](implications.md).
