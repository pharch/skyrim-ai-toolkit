# EXP-0046 — Shared HitData helper indirect-call trace

This dossier tests whether indirect calls inside the shared GOG `FUN_1407ddf50` helper add armor-dependent damage behavior beyond its mapped AV39 and Actor slot `0xE7` inputs.

## Scope

- Analysis target: GOG Skyrim AE 1.6.1179.0, identity and query scope EV-0302.
- Separate runtime target: Steam Skyrim AE 1.6.1170.0, identity EV-0109. No runtime test is part of this static query.
- Primary raw capture: `.local/ghidra/gog-query-20261016T144839Z.stdout.raw` and matching metadata, listed in the TX-20261016-0037 capture manifest.
- Relevant helper RVAs below are GOG addresses only.

## Result

EV-0304 classifies all ten indirect sites in `FUN_1407ddf50`. A weapon-selected target ActorValue can conditionally scale `totalDamage` on weapon-bearing hits, so the model that all remaining calls are auxiliary or cleanup is falsified for general helper use. Weapon attack damage and AV66/AV9 feed `percentBlocked`; AV163 contributes to the `criticalDamageMult` field; and the MagicTarget virtual is a conditional HitData clear. Three calls are release-style cleanup. The ProcessTrapHit builder leaves `HitData.weapon` null, so that route skips both weapon-specific branches. This does not identify the selected ActorValue with AV39 or establish any additional armor factor, positive protection, raw AVSK, Steam equivalence, or a vanilla reproduction.

The exact clean-save protection and raw AVSK comparison remains separate. No game state or installed data is modified.
