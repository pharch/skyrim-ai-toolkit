# Results — Q68 WE13 gate-layer screen

Transaction: TX-20261018-0004

The native fixed-five-master exports map the ordinary path WEStart/WERoadStart -> SMEN 0001379A -> WEQuestNode 000896A8 -> WEQuests 0004A601 -> WE13 QUST 0009F32F. The Solstheim path runs through DLC2WENode 0401E7D9 -> DLC2WERegionNorthNode 0401E7DF -> DLC2WERegionNorthQuestNode 0401E7E1 -> the same WE13 QUST. That QUST has the GetLevel >= LevelGateTrollCave (12) condition recorded by EV-0321. The second Story Manager selector is a separate scheduling context; it does not bypass the same QUST condition.

The hash-verified official-five-master census parsed 1,178,548 records and found 12 raw WE13 FormID candidates. Native field exports validate the two selector records. Remaining candidates are the QUST VMAD and two quest-owned PACK records. This exact-reference scan does not cover EditorID-based Papyrus lookups, every native caller, other archives, loose scripts, or a profile winner.

The placement extractor found 167 direct REFR WETriggerScript source records resolving to 158 logical references: 148 WETrigger, 7 WETriggerOnLoad, 12 DLC2WETrigger. It decoded all 167 REFR VMADs after correcting schema order. Four base ACTIs define the event keywords. Source placement and persistence do not establish loaded state or physical cave access.

Four bounded classic PEX 3.2 files from Skyrim - Misc.bsa show WETriggerScript dispatching Story Manager events, no direct StartQuest or SetStage writer in the other linked file bodies, a no-op WE13 startup fragment, and encounter cleanup in another fragment. This is not a full archive or loose-file census.

Q68-H1 is supported within the two mapped Story Manager paths: both select the same level-12 QUST. Q68-H2 remains proposed because direct starts outside the bounded source screens and physical access are unresolved. Q68-H3 is supported: event scheduling, quest eligibility, alias fill, actor spawn, and physical cave access are separate transitions. No level-one runtime result exists (EV-0260). No causal edge to OBJ-2 armor XP is supported.
