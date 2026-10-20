# EXP-0029 — Enchanting craft to skill-progress path

**Status:** Static GOG screen complete; raw XP observation blocked by missing verified instrumentation and disposable test state (EV-0260).

**Objective:** Q-0005 / OBJ-3. Determine whether enchanting credit varies with item value, soul size, or selected effects, how credit accumulates toward skill levels 16 and 21, and whether a useful enchantment can be crafted below those thresholds.

**Competing models:** H1 predicts craft-input-sensitive or quantized credit. H2 predicts one station-selected skill-use award per craft confirmation, accumulated in raw skill progress before the displayed skill level advances.

**Static result:** GOG 1.6.1179.0 code has one `Actor::UseSkill` dispatch site in the craft-confirm callback. It reads the skill ID from the workbench's `usesSkill` byte and passes a shared global float as points. The PlayerCharacter override rejects non-positive points and forwards positive points into the skill-progress helper. The installed base Skyrim.esm workbench record `FURN:000BAD0D` supplies AV23/Enchanting (EV-0280, EV-0281).

The trace narrows input-sensitive credit at the call site and supports cumulative progress beneath the level threshold. It does not resolve the points value or measure raw XP, and no GOG RVA is transferred to Steam 1.6.1170.0. See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [expected discriminants](expected-discriminants.md), [results](results.md), and [implications](implications.md).
