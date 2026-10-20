# Competing models

## H1 — a remaining call adds a totalDamage input

At least one indirect call supplies a conditional input that changes `HitData.totalDamage` (`+0x50`) beyond the already mapped AV39 and Actor slot `0xE7` inputs.

**Prediction:** A resolved target or bounded descendant reads a weapon-selected ActorValue or other value and its result enters the `+0x50` multiplier. This would be an additional damage input, though not necessarily an armor-rating factor.

## H2 — remaining calls do not change totalDamage

The remaining indirect calls affect only secondary HitData fields, evaluate independent gates, or release references; AV39 and slot `0xE7` are the only inputs to the helper's `totalDamage` calculation.

**Prediction:** Resolved targets show value reads feeding fields such as `percentBlocked` or `criticalDamageMult`, a conditional clear path, and cleanup, with no additional value entering the `+0x50` multiplier.

## Discriminating evidence

Resolve the two behavior-bearing slot-`0x4` calls at GOG RVAs `0x1407de2fc` and `0x1407de518`; check the three visible ActorValueOwner getter indices `0x42`, `0x09`, and `0xA3`; map the conditional `GetActorValue` index loaded from the associated object's `+0x194`; classify the three refcount cleanup calls; and establish whether the ProcessTrapHit builder supplies a weapon pointer. Preserve any unresolved target explicitly.
