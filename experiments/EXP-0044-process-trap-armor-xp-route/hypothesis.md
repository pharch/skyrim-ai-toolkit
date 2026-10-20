# Competing models

## H1 — mitigation shared, armor credit omitted

The physical-trap `ProcessTrapHit` receiver consumes common HitData with worn-armor mitigation, then follows a bounded route that omits all player AV11/AV12 awards.

**Prediction:** Build-attested dataflow carries armor-dependent mitigation into final trap damage. The complete relevant receiver and indirect-dispatch targets contain no Light/Heavy Armor skill-credit call. On a clean level-one control, armor reduces positive trap damage while raw Light/Heavy Armor AVSK remains unchanged.

## H2 — incomplete award trace or no effective armor protection

The apparent AV11/AV12 omission is due to unresolved receiver dispatch, or the trap route's final damage does not depend on worn armor.

**Prediction:** A resolved indirect target reaches AV11/AV12 credit, or the mitigation dataflow bypasses/removes worn-armor protection. A matched clean level-one armor/control comparison separates these outcomes.

## Interpretation boundary

EV-0292–EV-0295 support common HitData construction and bounded branches without a mapped armor award; they do not settle every indirect edge. Positive configured PEX damage is not positive live damage. Static GOG findings do not establish the installed Steam behavior. H1 requires both protection and raw AVSK discriminators before this is a functional-armor candidate.

## EV-0302 update

The static mitigation submodel of H1 is supported: `ProcessTrapHit` and normal hits both call `FUN_1407ddf50`, which reads AV39/GetArmorBaseFactorSum inputs and reduces HitData `totalDamage`. The trap wrapper also bypasses the known normal resolver `FUN_1406bcaa0` AV11/AV12 branch. The no-award submodel remains proposed because 28 indirect callsites in `FUN_1406b9df0` remain unresolved, and positive protection/zero raw AVSK have not been measured.

H2's no-mitigation branch is narrowed for the mapped GOG source path; its incomplete-trace branch remains live until the unresolved receiver targets are classified.
