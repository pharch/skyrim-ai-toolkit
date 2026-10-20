# EXP-0127 — MS06 ordinary start route and level gate

- **Frontier:** Q-0078 (OBJ-1)
- **Question:** Can the level-10 Story Manager node be bypassed by an ordinary MS06Start dialogue, note, scene, or placed-trigger route while MS06 is stopped?
- **Scope:** Official Skyrim, Update, Dawnguard, HearthFires, and Dragonborn master records; the Update.esm five-master winners for MS06 and MS06Start; attached PEX bodies available through the tested base Skyrim - Misc.bsa route; and the existing GOG AE 1.6.1179.0 `Quest.SetStage` trace. This is not an active-profile or Steam-runtime result.
- **Starting evidence:** EV-0300 maps SMQN `000D91D2` to MS06 at level 10. EV-0313, EV-0314, and EV-0316 preserve the GOG SetStage entry predicate and its QUST field inputs. EV-0260 preserves the unavailable clean level-one Observer lane.
- **Protocol and outcomes:** [protocol](protocol.md), [hypotheses](hypothesis.md), [discriminants](expected-discriminants.md), [results](results.md), and [implications](implications.md).

The bounded source screen now includes the five-master SMQN/QUST, DIAL/INFO/TIF, placed-reference, and SCEN routes. It identifies the Falk-note `SetStage(10)` request and helper self-progress scenes, but does not establish a low-level Steam transition or a profile-specific winner.

