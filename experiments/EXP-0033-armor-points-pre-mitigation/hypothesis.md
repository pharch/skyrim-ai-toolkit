# Hypotheses

## H1 — Post-mitigation total damage feeds armor points

The AV11/AV12 receiver call reads the damage remaining after AV39 and armor-base-factor mitigation. Changing those reductions can therefore change the armor `UseSkill` points argument.

**Prediction:** A def-use trace ends at the mutated `totalDamage` field or another post-mitigation value.

## H2 — Pre-resistance physical-damage snapshot feeds armor points

The AV11/AV12 receiver call reads `physicalDamage`, copied from the then-current `totalDamage` before the AV39/armor-factor reduction. The final mitigated `totalDamage` remains a distinct field used by other branches.

**Prediction:** Both default and alternate HitData builders reach the receiver with `+0x54` as the copied snapshot; the `+0x50` mitigation writes do not rewrite `+0x54`.

## H3 — A separate downstream clear may zero both damage fields

A state-dependent caller path may clear the contiguous `totalDamage`/`physicalDamage` pair after mitigation, independently of which field normally supplies points.

**Prediction:** A helper called after the builder writes zero across `+0x50..+0x57` before receiver skill routing. Its condition must be treated separately from AV39 and armor mitigation unless a direct causal edge is found.
