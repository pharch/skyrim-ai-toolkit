# EXP-0013 protocol

## Competing models and predictions

- **H1 — the candidate suppresses only skill credit:** a natural negative AV39 state makes the blocked hit's AV9 points non-positive. The PlayerCharacter guard rejects AV9, the blocked branch still skips AV11/12, and worn armor still measurably reduces damage.
- **H2 — no qualifying vanilla state:** damage construction keeps the AV9 amount positive, the candidate cannot target the player through ordinary play, cleanup removes the state before the hit, or the armor-protection control fails.

The static GOG path is a mechanism lead, not an installed-Steam result. Do not infer the effect from the displayed level or a visual armor rating.

## Preconditions and source identity

Before a live test, verify the exact Steam `SkyrimSE.exe` ProductVersion (installed 1.6.1170.0 identity is EV-0109), complete active order for the disposable profile, clean disposable save, exact winning records, and a loaded read-only Observer handshake. No level, quest, effect, ActiveEffect, hit or save state may be forced. If the natural WICast event does not occur, record an inconclusive observation rather than casting the shout or adding the effect.

## Matched observations

1. Capture baseline player level, AV39, ActiveEffects, raw AVSK progress for AV9/11/12, worn armor records and their base ratings, block state, and attacker/weapon identity.
2. **Unarmored control:** take one standardized valid hit with no armor; capture HitData totals, health loss, and AVSK deltas.
3. **Armor control:** repeat the same hit with qualifying worn armor and no candidate effect; capture the same fields and confirm the hit is valid and armor protection is measurable.
4. **Candidate:** only after an ordinary event naturally applies the effect to the player, capture effect source, magnitude, duration, AV39 and ActiveEffect identity. Repeat the matched blocked hit with the same armor and block input.
5. Record each selected `UseSkill` ActorValue and points argument, HitData `totalDamage`/`physicalDamage`, raw AVSK before/after, and subsequent cleanup. Preserve the save and all raw logs before reset.

## Decision rule

Support H1 only if a valid blocked hit selects AV9 with points `<=0`, raw AV9/11/12 progress is unchanged, the ordinary armor control gives its expected progress, and the candidate still measurably reduces damage relative to the unarmored control. A displayed level without raw progress is insufficient. Any forced state is `diagnostic_intervention`, not a vanilla reproduction.
