# Protocol

Use a disposable level-1 save with one low-rating positive-DNAM armor piece and no shield for the first sample. Before travel, record Heavy/Light/Block raw progress and thresholds, AV39, equipment DNAM/BOD2, load order, and observer profile. During ordinary travel/exploration only, observe Story Manager starts, alias fills, spell FormIDs, AV39/effect additions, and every `UseSkill` call. Do not force a quest or cast.

Prioritize a clean save that reaches Sovngarde through ordinary main-quest
progression without console or diagnostic mutation. The parent Story Manager
node has a raw `GetInCurrentLoc` condition for `SovngardeLocation`; verify
whether the node fires inside or outside that location before expanding to
other cells.

If an unforced Marked-for-Death cast reaches the player, take one weak unblocked hit and one held-block hit during the 60-second effect. Record total/physical damage, blocked bit, AV39, selected skill, points bit pattern, wrapper return, and raw progress. If only words 1/2 appear, test overlap by reading active-effect identities and AV39, never HUD icons alone.

For every candidate cell, also record `WIComplexInteractionToggle` keyword data
before entry, after each observed world-interaction quest stage, after leaving
the cell, and after save/load. Correlate each change with active quest stages
and the official Disallow/Allow callsites. A repeated decrement without a
matching increment is the specific H-0009 imbalance signature.
