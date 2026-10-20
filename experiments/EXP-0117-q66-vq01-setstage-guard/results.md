# Results — Q-0066 VQ01 SetStage startup guard

## Rival models and discriminant

- **H1:** Fort Dawnguard's mapped dialogue callback calls `DLC1VQ01.SetStage(10)`. In the GOG AE 1.6.1179.0 callback, an accepted `Quest.SetStage` request can call `TESQuest::EnsureQuestStarted` in start-now mode before the requested stage is written. VQ01's source fields and constructor state satisfy the initial event/ready-state predicates, with no level comparison in the bounded callback.
- **H2:** a startup eligibility or required-alias/reference preflight can still reject the stopped quest, leaving stage 10 un-applied or a start incomplete.
- The static discriminator is the exact QUST source data against the callback and helper predicates. A natural, clean level-one run must separately show the quest running state, stage, required aliases, and useful crypt access; a journal/map marker alone is insufficient.

## Source-linked findings

The five-official-master source export identifies Dawnguard.esm `DLC1VQ01` as form `0200352A`, Run Once, and not Start Game Enabled [EV-0326, EV-0379]. Its direct TES4 parser capture has no `ENAM` subrecord. The VQ01 export contains 14 aliases: six required, including DimhollowCrypt, Tolan, Adalvald, Serana, Book, and DimhollowEntrance; the alias export has no alias-node CTDA/function rows. Serana is an external alias to the start-enabled `DLC1NPCMentalModel` alias `ResponsiveNPC`, whose source fill is the forced `DLC1SeranaRef` in DimhollowCrypt02 [EV-0379]. These are source fill definitions, not proof of live alias initialization.

The mapped Fort Dawnguard route in the fixed official-master source scope runs through the VQ00 Durak dialogue helper and requests `DLC1VQ01.SetStage(10)`; the separate level-10 Story Manager helper is not on that mapped callback chain [EV-0326]. The GOG callback candidate `FUN_14034de90` checks `(quest + 0xDC bit 0) OR (quest + 0xE0 == -1)`, and its accepted path calls `FUN_1403c9d30` (`TESQuest::EnsureQuestStarted`) with mode 1 before stage application [EV-0313, EV-0380].

The GOG `TESQuest` constructor candidate initializes `+0xE0` to `0xFFFFFFFF`, sets bit `0x100` in `+0xDC`, and zeros `+0x22A`. With the VQ01 record's absent `ENAM`, these constructor defaults satisfy the observed initial SetStage predicate and the helper's inner `(bit 0x100 clear) OR (+0x22A == 0)` check in this GOG model [EV-0381]. The GOG helper then performs further state/readiness and alias/reference work before `BeginStartUpQuest`; it is not an unconditional start [EV-0380, EV-0382].

The alias/reference processor `FUN_1403d0c10` includes data-driven fill/condition paths, five unresolved indirect call sites in the bounded query, and paths that return zero. Its caller treats a failed nonoptional entry as a failed preflight [EV-0382]. No direct `GetLevel` comparison appears in the bounded SetStage callback/helper code examined, but that does not prove all source-driven or deferred startup behavior is level-independent.

## Decision and limits

H1 is supported as a **conditional GOG/source candidate**: the callback can request startup before stage 10, and the exact VQ01 source/constructor inputs pass the initial callback predicates. H2 remains live because required-alias/reference preflight and actual startup completion are dynamic. The evidence does not establish a Steam AE 1.6.1170.0 result, a level-one reproduction, quest-running state, alias fill, or functional crypt access. Stage 10's objective/map-marker change is not itself proof that the content can be entered or progressed [EV-0326].

No causal edge to OBJ-2 is supported. The next discriminating test is a clean level-one Steam run using only the natural Fort dialogue sequence, with a no-dialogue control and read-only capture of player level, VQ01 running/stage state, each required alias, and actual Dimhollow entrance/progression. No console stage/start command, script injection, modified plugin, or altered save may be part of the candidate run; current live prerequisites remain unavailable [EV-0260].
