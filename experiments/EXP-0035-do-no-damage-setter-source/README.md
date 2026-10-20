# EXP-0035 — doNoDamage setter source

**Status:** The only observed direct nonzero setter caller is a process-level-gated action-data callback; its parameter schema and dispatch source remain unresolved.

**Question:** What input and caller path can set `AIProcess.middleHigh.doNoDamage` through `FUN_14048a5b0`, and does the bounded GOG trace connect it to ordinary hit resolution?

**Result:** `FUN_14048a5b0` reads bit 1 from parameter slot 7 and passes it to the doNoDamage setter. Its only observed direct caller is `FUN_14048a390`, gated on the actor's current process level being High or MiddleHigh. That callback constructs TESActionData/BGSActionData values, but the action dispatcher and meaning of parameter slot 7 are not identified. Neither function has an observed direct call to the GOG hit resolver. Ordinary attack-animation dispatch and natural occurrence remain open ([EV-0287], [EV-0286]).

This is static GOG AE 1.6.1179.0 evidence only. It does not establish a vanilla gameplay route, effective armor protection, zero XP, or Steam equivalence. See [hypotheses](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md).
