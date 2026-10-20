# EXP-0018 — DA14 alternate writer and scene screen

**Status:** bounded static screen recorded; one cross-quest DA14 alias caller remains unresolved; no gameplay result.

**Objective:** Q-0002 / OBJ-1. Determine whether the DA14Start scene chain contains an independent start transition before the Story Manager level gate.

**Current result:** DA14Start stages 30 and 50 start the two Sam drinking scenes; scene fragments advance DA14Start to stages 40 and 60; DA14Start stage 70 sets DA14 stage 5 then stops DA14Start. An exact raw VMAD FormID search also found a DA14 alias-3 property on Dragonborn QUST `DLC2DialogueRavenRock`. Its script body was not recovered by the tested base Misc BSA extraction route. See [protocol](protocol.md), [results](results.md), and EV-0264.

**Boundary:** These offline five-master observations do not prove an active-profile winner, enumerate native/dynamic writers, or reproduce a level-one transition. No live game, save, plugin, archive, or profile was modified.
