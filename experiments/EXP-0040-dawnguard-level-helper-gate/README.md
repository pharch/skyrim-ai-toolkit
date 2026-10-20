# EXP-0040 — Dawnguard level helper versus quest start

**Status:** Static result. The level-10 Story Manager predicate starts a Durak messenger/location helper; the captured Dawnguard quest records do not put `GetLevel` on the selected VQ00/VQ01 conditions. Alternate low-level paths are revision-cited leads, not a verified level-one reproduction.

**Question:** Does Dawnguard's level-10 requirement govern actual DLC quest startup, or only the Durak recruitment path?

**Result:** SMQN `0200D911` (`DLC1VQ00Node`) checks `GetLevel >= DLC1VQMinLevel` (10) and selects QUST `0200D90B` (`DLC1VQ00ChangeLocation`), whose Messenger alias points to NPC_ `0201541D` (`DLC1Durak`). QUST `DLC1VQ00` and `DLC1VQ01` have stage/cell conditions in the captured fields, not a `GetLevel` condition. Local UESP revision 3603039 describes guard-rumor, Dayspring Canyon/Agmaer, and Fort Dawnguard alternatives, including Awakening progression without the starter quest journal entry. EV-0298 contains raw captures and limitations.

This narrows the serialized gate to a helper route. Whether those alternate paths execute at level 1 and produce actual `Awakening` progression remains untested. See [hypothesis](hypothesis.md), [predicted outcomes](predicted-outcomes.md), [protocol](protocol.md), [results](results.md), and [implications](implications.md).
