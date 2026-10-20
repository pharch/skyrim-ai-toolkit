# EXP-0039 hypotheses

## H1 — shared HitData and armor-XP route

The native function bound to Papyrus `ObjectReference.ProcessTrapHit` constructs or forwards HitData and can reach the player receiver AV11/AV12 branch as well as common mitigation calculations.

**Prediction:** The exact native binding and PlayerCharacter callee route reach a HitData builder and a player AV11/AV12 branch. A valid unblocked trap impact with positive damage and qualifying worn armor selects AV11/AV12.

## H2 — trap damage skips HitData construction

`ProcessTrapHit` handles trap impacts through a separate damage path that bypasses the common HitData builder and armor calculations.

**Prediction:** The exact native target and PlayerCharacter receiver route do not reach `FUN_1407dd110`/`FUN_1407ddf50` or the armor-related HitData fields.

## H3 — shared builder, separate receiver handler

`ProcessTrapHit` uses the common HitData construction/mitigation pass, then dispatches to a distinct Actor receiver handler. Whether descendants or indirect calls award AV11/AV12 remains unresolved.

**Prediction:** The PlayerCharacter slot route reaches the common builder and a different receiver function from `FUN_1406bcaa0`; direct/indirect callee analysis identifies whether an AV11/AV12 award occurs below that handler.

## Exclusion rule

A miss, impact below the trap script's velocity threshold, block, zero damage, unequipped armor, nonpositive skill points, or an unmeasured hit does not distinguish these models and cannot count as a zero-armor-XP result.
