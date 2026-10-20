# EXP-0038 hypotheses

## H1 — The placed unique actor is enabled through the gated quest alias

Dragonborn.esm places one reference for NPC base `020285C3`, but the reference starts disabled and the CLOC quest alias is its unique-actor owner. Stage 10 enables and moves that alias reference after Story Manager selection.

**Prediction:** the one matching ACHR has the Initially Disabled record flag; the target QUST has a Unique Actor alias for the same NPC base; other official record references do not configure an independent actor or quest start.

## H2 — Another official record provides an independent pre-gate actor or start path

A second placed actor, another quest alias, or a script/condition-bearing record independently exposes the actor or directly references the Ebony Warrior quest before the CLOC gate.

**Prediction:** another ACHR/REFR or an unrelated QUST/VMAD/package/scene record contains the actor base, placed reference, or quest FormID in a start-capable context.

## Assessment

H1 is supported for the serialized official-master record path. H2's independent-placement component is contradicted in those files: the full record scan found one matching ACHR and no matching REFR placement. Other matching fields belong to the target quest, its dialogue and packages, its stage-granted pickpocket perk, the CLOC child link, or Last Vigil location data. Dynamic script lookups, arbitrary PEX code, profile overrides, and runtime enable state remain open ([EV-0290]).
