# EXP-0038 — Ebony Warrior placement and record-reference screen

**Frontier / transaction:** Q-0030 / TX-20261016-0026  
**Status:** Bounded official-master static result; profile and runtime behavior remain open.  
**Question:** Does an independent placement or record-configured start path expose the Ebony Warrior before the CLOC Story Manager gate?

The installed Dragonborn.esm file contains one ACHR using NPC base `020285C3`: `02030CC9` (`DLC2EbonyWarriorRef`). Its record header sets the TES5Edit-defined Initially Disabled bit and contains no XESP Enable Parent subrecord. The Ebony Warrior quest alias is serialized as a Unique Actor fill using the same NPC base; EV-0288 shows its stage-10 fragment enabling and moving that alias reference. A direct raw-subrecord scan across all five official masters found no second placement or independent quest record path for the scanned FormIDs ([EV-0290]).

This supports the gated alias path for the installed official source files. The parser does not resolve overrides or record parent-cell groups; the scan does not inspect arbitrary PEX bodies, Creation Club/user plugins, dynamic FormID lookups, or runtime state. It does not prove a level-one start or a live disabled state.

See [hypotheses](hypothesis.md), [predicted outcomes](predicted-outcomes.md), [protocol](protocol.md), [results](results.md), and [implications](implications.md). The raw captures remain under ignored `.local/alignment/transactions/TX-20261016-0026/`.
