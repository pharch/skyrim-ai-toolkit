# Hypotheses

## H1 — Attacker-side one-shot no-damage cancellation

The resolver clears HitData when the attacker has a `doNoDamage` process flag and is not in combat or is ignoring combat. The full clear suppresses the receiver's armor points independent of worn armor or AV39.

**Prediction:** The process bytes map to `middleHigh->doNoDamage` and `AIProcess::ignoringCombat`, and the virtual actor call maps to `IsInCombat`; the clear helper overwrites both damage floats before receiver routing.

## H2 — Armor-linked post-mitigation protection state

The flag represents an armor or protection state that reduces HitData after useful armor mitigation and provides a functional zero-XP route.

**Prediction:** The flag/condition depends on worn armor, AV39, or receiver protection, or an independent effective-protection outcome is established before the clear.
