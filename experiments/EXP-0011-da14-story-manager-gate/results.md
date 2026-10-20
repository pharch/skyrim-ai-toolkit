# EXP-0011 results

## Record observations

- Skyrim.esm `DA14QuestStartNode` (SMQN `0003FA1A`) has three CTDAs and one child. Its first CTDA raw bytes are `60ef6514000060415000000000000000000000000200000014000000ffffffff`; the parser reads function index 80, comparison float 14.0 and reference form `00000014`. xEdit's source condition table maps index 80 to `GetLevel`; its release notes identify form `00000014` as PlayerRef (EV-0214). The corrected historical CTDA decoder EV-0108 reports the matching DA14 gate as `>=14`.
- The node's only child link resolves to QUST `DA14Start` (`0003FA17`). Skyrim.esm `DA14Start` has two CTDAs with function indices 562 and 180; the Skyrim.esm and Update.esm `DA14` QUST records each have two function-67 CTDAs. xEdit's function table maps 67 to `GetInCell`. No screened QUST condition has function index 80.
- Skyrim.esm has 61 DIAL topics with DA14 in the editor ID and 65 linked INFO records. The five-master raw scan found no function-80 condition in those 65 INFO records. It found no target DA14 QUST/SMQN record in Dawnguard.esm, HearthFires.esm or Dragonborn.esm, and Update.esm has the matching main DA14 QUST override but no DA14Start or node. This is an official-master file screen, not an active-order winner claim (EV-0212, EV-0213).
- `QF_DA14Start_0003FA17.pex` disassembly shows Fragment_2 calling `SetObjectiveCompleted`, then `SetStage(5)` on the `DA14` Quest property, then `Stop` on self (EV-0215). Follow-up VMAD mapping resolves Fragment_2 to DA14Start stage 70. Stages 30/50 start the two Sam drinking scenes; their scripts advance the owning quest at stages 40/60 (EV-0264). This fills the earlier fragment-stage gap but does not establish a separate start route or level-one transition.
- The narrow parse of `QF_DA14_0001BB9B.pex` has no textual `GetLevel` token. This does not rule out conditions outside that script or dynamic native behavior (EV-0216).

## Tool boundary

The attempted native xEdit query failed before launch with the WSL interop error `UtilBindVsockAnyPort: socket failed 1`. It produced no native record export. The successful observations above come from a read-only TES4 parser plus the xEdit schema source reference and PEX inspection; they are not labeled as native xEdit results.

## Assessment

H1 is supported for the screened Story Manager-to-DA14Start record path: the only explicit `GetLevel` condition found is on the start node. H2's repeated-condition branch is unsupported in the screened QUST/INFO scope, but its distinct-entry-route branch remains open. No level-one quest start, level preservation, negative control, replication, profile-specific winner, or actual alternate route was observed. This is a mechanism lead only, not a bounty candidate reproduction.

## Next discriminant

Q-0002 will inventory ordinary player-accessible DA14/DA14Start start writers and determine whether they necessarily reach `DA14QuestStartNode`. If a distinct route remains plausible, the decisive test needs a clean level-one save, a matched no-trigger control, numeric level preservation and direct observation of DA14/DA14Start running state and stage—not console or injected-stage evidence.
