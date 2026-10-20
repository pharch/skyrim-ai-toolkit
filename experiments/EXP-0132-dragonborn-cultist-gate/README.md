# Dragonborn cultist CLOC gate and actor-template chain

This experiment separates three questions that had been conflated in the
cultist lead: whether the main-quest CLOC path has a Player-level predicate
before its quest starts, whether the separate world encounter has a level
predicate, and whether the CLOC aliases select level-dependent actors.

The official five-master records and loose Dragonborn PSC source show distinct
CLOC and SCPT branches. The CLOC node selects `DLC2CultistAmbush`; its parent,
node, QUST, and screened stage fragments contain no `GetLevel` predicate. The
separate `DLC2WE09` world quest has the previously decoded
`GetLevel >=25 OR Solstheim` condition group [EV-0654]–[EV-0669]. Revision-pinned
UESP pages likewise distinguish the post-Way-of-the-Voice pair from random
world encounters [EV-0679].

New record captures show the CLOC aliases' `TPLT` links lead through
`DLC2LvlCultist*` NPCs to leveled NPC records. Their root lists have entries at
levels 1, 18/19, 27, 36, and 46, and the aliases have `LVLF=0x03` list roots
and template-use masks [EV-0677]. The GOG 1.6.1179.0 `TESNPC` template-copy
override reads a base-template pointer and per-field template-use mask, while
also branching on the ACBS `Use Template` bit [EV-0678]. The CLOC alias records
have that ACBS bit clear. This makes actual alias-to-list runtime resolution a
live competing model; the static records and GOG code do not identify which
actor base the Steam runtime fills into the aliases.

The result is bounded source evidence, not a level-one exploit or a vanilla
reproduction. It does not prove any hidden native callback or profile override
cannot add a gate, and it does not establish a Steam actor-selection result.
The exact natural level-one transition remains part of EV-0260.

Raw parser, UESP, Address Library, and Ghidra captures remain below ignored
`.local/`. The scripts here produce concise evidence summaries and keep the
GOG and Steam identities separate.
