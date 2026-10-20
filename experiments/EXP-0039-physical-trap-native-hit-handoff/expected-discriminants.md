# Expected discriminants

| Observation | H1: descendant armor award | H2: damage route without armor award | H3: direct post-resolver convergence |
|---|---|---|
| Receiver call graph | A descendant or indirect target reaches Actor::UseSkill with AV11/AV12 or an equivalent armor-credit routine | Bounded relevant descendants identify a damage/protection path but no AV11/AV12 award site; state uncovered indirect edges | Trap path reaches FUN_1406b9df0 directly; FUN_1406bcaa0 calls it after the AV11/AV12 receiver branch |
| Existing bounded result | Shared HitData builder is established; AV11/AV12 descendant remains untested | FUN_1406b49d0 conditionally calls HandleHealthDamage for negative Health delta; helper AV15 calls do not establish armor credit | Supported as a call-path shape; no positive damage/protection measurement |
| Runtime-initialized AV callback | A mapped AV11/AV12 callback reaches `UseSkill` AV11/12 or returns to `FUN_1406bcaa0` | AV11/12 entries map to `FUN_1406b65c0` -> Actor slot `0xCA`; selected PlayerCharacter callback updates fields/container state and shows no skill award | Supported within the selected callback chain; unrelated receiver indirect calls remain open |
| Valid player trap impact | Independently measure positive damage, effective armor mitigation, selected AV/points and raw AVSK | Same measurements are required before accepting a functional zero-armor-XP result | Same measurements are required before accepting a bypass candidate |
| Contact controls | Miss, sub-threshold impact, block, zero damage and unequipped armor are excluded | Same exclusions; none counts as a zero-XP route | Same exclusions; none counts as a zero-XP route |
