# EXP-0018 protocol

## Competing hypotheses and discriminants

- **H1 — downstream DA14Start scene chain:** scene `Start()` calls occur only in DA14Start quest-stage fragments downstream from `DA14QuestStartNode`. The discriminant is VMAD fragment-to-stage mapping plus PEX call sites and scene script ownership.
- **H2 — separate ordinary initiation:** a player-accessible script, quest, or scene reaches DA14/DA14Start without the Story Manager node. The discriminant is a distinct Start/SetStage writer or a clean level-one transition that starts the event before the gate.

## Read-only procedure

1. Verify installed executable identity separately from GOG static evidence and hash the five official masters.
2. Retrieve DA14, DA14Start, the start node, and both Sam drinking SCEN records through the direct TES4 parser; label this separately from native xEdit.
3. Decode QUST VMAD fragment-to-stage mapping using the pinned TES5Edit schema, then disassemble only the PEX scripts linked to the candidate scene/quest records when the tested archive route can validate them.
4. Screen all five official masters for DA14, DA14Start, and scene VMAD object references. Preserve decoder errors and run raw FormID byte-pattern discovery only as candidate search; validate each candidate against its record and schema before interpreting it.
5. Inspect direct candidate script calls, stage checks, scene starts, and triggers. Keep unresolved script bodies and unsupported archive paths explicit.
6. Do not claim a level-one bypass, profile winner, or negative from static absence. The runtime discriminator requires a clean level-one save, matched ordinary no-trigger control, verified complete active order, and direct running-state/stage capture.

## Controls and exclusions

No console stage/level forcing, injected script, altered plugin, game launch, live mutation, or save write is part of this protocol. A debug-forced transition can only be diagnostic. A raw FormID byte hit is not a decoded reference until its record field is schema-validated.
