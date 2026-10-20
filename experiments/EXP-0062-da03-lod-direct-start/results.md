# Results

The hash-verified five-official-master join contains 15 logical DA03Start DIAL/INFO topic-child pairs. Lod's stage-10 handoff topics 000D7930 -> 000D7933 and 000E0D3F -> 000E0D47 require GetLevel >= 10 and helper stage below 10. Their PEX callbacks set helper stage 10; its QF fragment then calls DA03.SetStage(5) [EV-0322], [EV-0323].

The unlevelled Lod goodbye path 0010F58E -> 0010F590 sets only helper stage 20. The captured stage-20 fragment gives 25 gold and moves to stage 200, whose fragment stops the helper. No direct DA03 start/stage call appears in that callback [EV-0322], [EV-0323].

Q61-H1 is falsified and Q61-H2 supported within the fixed official source layer and tested base-Misc-BSA PEX scope. This closes the Lod direct-start candidate only. It establishes neither a profile winner nor runtime dialogue accessibility, level-one main quest state/progression, useful access, or vanilla reproduction. No cross-objective edge to OBJ-2 is justified.
