# Implications

EV-0304 adds a conditional weapon-selected ActorValue to the `totalDamage` calculation for weapon-bearing helper calls. The weapon's attack damage and AV66/AV9 feed `percentBlocked`; AV163 contributes to `criticalDamageMult`; and a later `MagicTarget::IsInvulnerable` gate can clear selected HitData fields. This is another damage input, but the evidence does not identify it as armor rating or establish a factor beyond AV39 and `GetArmorBaseFactorSum`.

The captured ProcessTrapHit construction route has a null weapon pointer, so it skips the two optional weapon branches while retaining the common AV39/slot-`0xE7` calculation. Neither route proves positive protection or zero Light/Heavy Armor AVSK in Steam. The DA04, Dawnguard, and Ebony Warrior gate traces remain independent OBJ-1 evidence; no causal relation is supported.
