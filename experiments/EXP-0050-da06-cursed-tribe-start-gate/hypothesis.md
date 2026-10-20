# Competing models

- **H1 — ordinary pre-gate start:** although the level-9 Story Manager node selects main DA06, the quest is Start Game Enabled or the giant assault, Atub dialogue, fixed alias, or attached script can independently call `Start()`/`SetStage()` below level 9.
- **H2 — node-required start:** the level-9 node is the only configured main-DA06 start; the assault and Atub dialogue appear only after the quest starts, or their callbacks only advance a running quest.

The discriminant is the full serialized start path across the main QUST, alias fills, stages/QF, NPC/reference/trigger records, dialogue INFO conditions and PEX scripts. A static pre-gate writer supports H1; absence within the bounded official-record/base-Misc scope supports H2 only within that scope. A vanilla level-one transition requires a separate exact-target test.
