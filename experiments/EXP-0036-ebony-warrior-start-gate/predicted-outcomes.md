# EXP-0036 predicted outcomes

| Hypothesis | Predicted observation | Discriminant |
|---|---|---|
| H1: the level check gates initial Story Manager selection | A `GetLevel >= 80` condition appears on `DLC2EbonyWarriorNode`; the node's child is the Ebony Warrior QUST; later stage/alias scripts handle city appearance and relocation. | Decode the node CTDAs, parent event, child QUST, QUST start flags, fragment-stage mapping, and attached PEX. |
| H2: the check is only downstream, or another early start route exists | No level predicate appears on the initial selection node, or a separate start-capable quest/alias/script/API/placed actor path appears before the node. | Inspect QUST/dialogue/alias conditions and scripts, search directly linked record conditions, and continue the caller audit for ordinary start APIs. |

Static record evidence can distinguish where the serialized level predicate resides. It cannot alone prove that every possible game path is absent or that a level-one playthrough can start the quest.
