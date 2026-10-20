# EXP-0033 — Armor points before mitigation

**Status:** Static GOG dataflow question resolved; conditional whole-HitData clear found; gameplay and Steam results open.

**Question:** Which HitData field supplies the player receiver's Heavy/Light Armor `UseSkill` points argument, and is it read before or after armor mitigation?

**Result:** In the default and alternate hit-population paths, the receiver reads `physicalDamage` (`HitData+0x54`), which `FUN_1407ddf50` snapshots from the current `totalDamage` before AV39 and armor-base-factor mitigation. A later conditional helper can clear the 8-byte pair at `+0x50`, zeroing both fields before the receiver call. Its actor/process predicate is not yet semantically mapped ([EV-0285], [EV-0222], [EV-0223], [EV-0261]).

This experiment is static GOG AE 1.6.1179.0 analysis. It establishes neither Steam behavior nor a measured armor-XP or protection result. See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md). Raw Ghidra captures remain under ignored `.local/`.
