# EXP-0036 — Ebony Warrior level-80 Story Manager and quest-stage trace

**Frontier / transaction:** Q-0028 / TX-20261016-0024  
**Status:** Completed as a bounded static trace; alternate starts and runtime remain open.  
**Question:** Where does the Ebony Warrior's reported level-80 condition run, and how does that event connect to the quest, city greeting, and Last Vigil relocation?

## Result

The installed `Dragonborn.esm` `DLC2EbonyWarriorNode` (`SMQN 0202C49F`) is under a `CLOC` Story Manager event and has one child, `DLC2EbonyWarriorQuest` (`QUST 0202C49E`). Its first condition decodes to `GetLevel >= 80` on PlayerRef. The child quest is not Start Game Enabled and has no `GetLevel` predicate in its own CTDAs. A stage-10 fragment enables the Ebony Warrior alias, moves it to the city alias, and adds the pickpocket modifier; a later `OnLocationChange` callback handles relocation to Last Vigil at quest stage 100. The full 4,421-record Dragonborn INFO scan contains no `GetLevel` CTDA. These source-file observations locate the gate at Story Manager event selection, but do not exclude every separate start path or establish a profile winner or live result ([EV-0288]).

The UESP revision's level-80 encounter statement is consistent with the record gate, but remains secondary grounding ([EV-0134], [EV-0288]). The source/parser and PEX limitations are documented in [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md).

## Continuation

Q-0029 follows the unresolved discriminator: whether an ordinary vanilla `Quest.Start`/`SetStage` caller can start this CLOC event quest before its level-gated Story Manager child. Debug console or injected-script interventions will not count as vanilla candidates.
