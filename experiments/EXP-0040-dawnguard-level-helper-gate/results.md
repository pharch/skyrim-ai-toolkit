# EXP-0040 results

## Story Manager gate

Dawnguard.esm SMQN `0200D911` (`DLC1VQ00Node`) includes CTDA function 80, `GetLevel`. Its type byte `0x64` decodes through the versioned xEdit schema as `>=` plus `Use global`, and its comparison operand is GLOB `0200D912`. That GLOB is `DLC1VQMinLevel` with value 10.0. The node's child is QUST `0200D90B` (`DLC1VQ00ChangeLocation`); its `Messenger` alias uses ALUA reference `0201541D`, NPC_ `DLC1Durak`.

## Captured quest and dialogue conditions

QUST `0200D90E` (`DLC1VQ00`) has a `GetStageDone` condition for `DLC1VQ01MiscObjective` stage 10 plus one unresolved CTDA function; no `GetLevel` condition is present in the record. QUST `0200352A` (`DLC1VQ01`) has four `GetInCell` conditions that reference `DLC1DimHollowCrypt01`/`02`; no `GetLevel` condition appears. The targeted VQ00/VQ01 INFO records use `GetIsID` conditions for Durak, Isran, Celann, or Tolan. These are scoped record observations, not a complete PEX or call-path census.

The local UESP page revision 3603039 reports a level-10 Durak approach, but separately describes guard-rumor and Agmaer/Dayspring Canyon routes and a Fort Dawnguard path that can start `Awakening` without the starter quest appearing in the journal. That secondary account supports an alternate-path candidate; it does not prove the transition at level 1.

The native five-master xEdit query failed before process enumeration with the WSL `UtilBindVsockAnyPort` socket error. Direct-parser outputs are not native field exports or profile winners. Dawnguard BSA/PEX bodies, complete active order, and live level-one state remain unresolved ([EV-0298]).
