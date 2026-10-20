# EXP-0034 — Conditional doNoDamage hit clear

**Status:** Static GOG caller predicate mapped; the flag's natural setter route remains open.

**Question:** Which actor/process state calls `FUN_1407dda40` and clears both HitData damage floats before receiver-skill routing?

**Result:** The hit resolver consumes `currentProcess->middleHigh->doNoDamage`; it then clears HitData if the attacker is not in combat or its AIProcess `ignoringCombat` byte is set. `FUN_1407dda40` zeros the adjacent total and physical damage fields. This is an attacker-side whole-hit cancellation state, not an armor or AV39 condition. The only observed direct setter that can pass a nonzero value is an unresolved bit-based input route ([EV-0286], [EV-0285]).

Static GOG AE 1.6.1179.0 analysis only. It does not establish natural occurrence, Steam behavior, useful armor protection, or a zero-XP exploit. See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md).
