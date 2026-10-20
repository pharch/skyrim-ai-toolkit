# EXP-0038 predicted outcomes

| Hypothesis | Predicted observation | Discriminant |
|---|---|---|
| H1: the actor is enabled through the gated quest alias | One ACHR uses NPC base `020285C3`, sets Initially Disabled, and lacks XESP; QUST `0202C49E` has a Unique Actor alias for that base and stage 10 enables/moves it. | Inspect all ACHR/REFR records, target alias fields, and full official-master raw FormID hits. |
| H2: another official record exposes a pre-gate route | A second placement or unrelated quest/script/package/scene record contains the actor base, placed reference, or quest FormID in a start-capable context. | Search every record subrecord in the five official master files, then inspect each hit by record/subrecord type. |

Raw byte matches are candidate references only. TES5Edit schema interpretation is used for the ACHR record flags, XESP structure, QUST alias fill type, and CTDA fields. Static plugin data cannot establish the active-profile winner, a dynamic lookup, or runtime placement.
