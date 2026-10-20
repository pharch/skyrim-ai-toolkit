# EXP-0017 protocol

## Competing hypotheses and predictions

- **H1 — armor protection precedes the blocked award route:** with qualifying worn armor, the blocked hit remains valid, armor measurably reduces damage, and the player receiver selects AV9 while skipping AV11/12. The Block AV9 delta is recorded separately and may remain positive.
- **H2 — the blocked case fails the practical objective:** the armor factor is absent or ineffective on the blocked hit, the hit is not valid, AV11/12 still receive skill credit, or the Block cost crosses the level-one budget relevant to the run.

EV-0261/0263 support only the GOG static source-order component of H1. They do not select the runtime hypothesis for installed Steam AE.

## Target and preconditions

Before any live run, verify `SkyrimSE.exe` ProductVersion (installed Steam 1.6.1170.0 identity is EV-0109), the complete active order for the exact disposable profile, relevant winning ARMO/record values, a clean disposable save, and a loaded read-only Observer handshake. EV-0260 currently shows the profile, order, save, Observer deployment/load and bindings are unavailable. Do not launch or manipulate the live game as part of this static protocol; await user-controlled setup and launch.

## Controls and observables

Use one fixed attacker, weapon/attack, difficulty, player position, timing window, and ordinary blocking input. Record attacker and player form identities, hit direction, hit validity, incoming attack/weapon, game settings, base armor DNAM, equipped armor, AV39, HitData fields, health loss, selected `UseSkill` AV/points arguments, and raw AVSK before/after each hit.

1. **Unarmored, unblocked control:** one standardized valid hit; record baseline damage and raw AVSK deltas.
2. **Unarmored, blocked control:** repeat with ordinary block input; record Block AV9 points/delta and hit validity.
3. **Qualifying armor, unblocked control:** wear positive-DNAM armor; repeat the same attack without blocking; measure protection relative to the unarmored control and record AV11/12 points/deltas.
4. **Qualifying armor, blocked candidate:** repeat with the same armor and ordinary block input. Measure protection against the unarmored blocked control and the armored unblocked control; record whether AV9 is selected, whether AV11/12 are absent, and every raw AVSK delta.

The armor objective requires a valid hit, effective protection measured against its matched no-armor control, and no raw AV11/12 progress from the blocked hit. Any AV9 change is reported separately; it must not be described as zero total skill XP. If maintaining level one is part of the run, record the starting level and the exact remaining skill/character-level budget and reject any trial that crosses it.

## Save and rollback

Use only a clean duplicate disposable save after all preconditions pass. Preserve a byte-identified baseline copy and raw capture bundle; roll back by discarding the trial save and restoring the baseline copy. Do not use the user's primary save. No test save exists or is authorized by this protocol at present.

## Decision and classification

Support the OBJ-2 result only when armor reduces damage in the blocked case relative to the matched unarmored blocked case, the hit is valid, no AV11/12 skill call or raw progress occurs, and the ordinary controls behave as expected. Capture AV9 separately. Missing target identity, incomplete controls, observer drops, or missing raw AVSK makes the trial inconclusive. An injected stage/effect or console-forced state is `diagnostic_intervention`, not a `vanilla_reproduction`.
