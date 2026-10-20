# EXP-0031 — Zero effective armor rating and hit XP selection

**Status:** Bounded private-lead screen and GOG source comparison complete; Steam runtime measurement remains open.

**Objective:** Determine whether reducing a worn Heavy/Light armor item's effective or displayed armor rating to zero suppresses hit-earned armor XP while retaining protection.

**Current result:** The bounded private export contains a build-unspecified report that a Heavy Armor item at displayed rating zero still earned XP on hit, plus a level-one negative-rating report that XP increased. GOG AE 1.6.1179.0 source analysis independently identifies a positive base-DNAM worn-ARMO selector before AV11/12 routing. This narrows the mechanism; it does not verify Steam AE 1.6.1170.0 behavior, raw XP, or protection in a live test ([EV-0283], [EV-0222]).

See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [expected discriminants](expected-discriminants.md), [results](results.md), and [implications](implications.md). Private source pointers and raw exports remain in ignored `.local/alignment/transactions/TX-20261016-0019/`.
