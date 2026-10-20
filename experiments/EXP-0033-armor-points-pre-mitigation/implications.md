# Implications

The receiver armor award normally consumes a pre-resistance `physicalDamage` snapshot, while AV39 and armor-base-factor mitigation update the separate `totalDamage` field. This strengthens the source path from incoming hit construction to AV11/AV12 points and separates it from effective damage reduction.

The conditional `FUN_1407dda40` path resets both fields, so it qualifies the claim that later mitigation cannot alter armor points. It supplies a new static zero-points lead, but its attacker/process condition is unresolved, and its complete damage clear does not show that armor caused or retained protection. It should be explored as a separate state-machine question rather than treated as a functional-armor candidate.

No edge to OBJ-1 quest initiation is supported. The shared PlayerCharacter `UseSkill` sink remains a cross-domain link to Enchanting, but EXP-0033 adds no XP-suppression edge there. Required runtime work remains a matched hit with exact Steam build/profile, HitData, protection, and raw AVSK observations.
