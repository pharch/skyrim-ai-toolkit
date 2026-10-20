# Protocol

## Target and prerequisites

- Verify the exact Steam `SkyrimSE.exe` ProductVersion and complete active order. If the target is MO2-managed, use that profile's full explicit `plugins.txt`.
- Require a disposable level-one baseline save and an approved, loaded measurement tool that captures actual hits, effective protection, AV11/12 and AV9 calls, and raw skill progress. Do not launch Skyrim from an unattended readiness run.
- If these prerequisites are absent, do not schedule a live action. Keep the result static/community-lead only and update the exact external discriminator.

## Matched comparison

1. Record armor FormID, armor class, body slots, base DNAM, displayed/effective rating, relevant effects, Heavy/Light/Block level and raw progress, and current character level.
2. Use one positive-DNAM Heavy or Light item in a normal-rating control, then in a candidate state that changes its current effective/displayed rating to zero. Include a negative-rating state only if it is naturally reproducible at level one. Keep incoming attacker, hit type, difficulty, location, blocking state, and other equipment/effects fixed.
3. Compare a bare/unarmored control and, if available, a true zero-base-DNAM item whose separate protective effect can be measured. Do not conflate “zero displayed rating” with “zero base DNAM.”
4. For each verified hit, capture hit identity, damage before/after mitigation, armor contribution, selected skill AV, `UseSkill` points, raw Heavy/Light/Block progress before and after, and level. Repeat enough hits to detect delayed or batched progress; restore the baseline between conditions.
5. Keep any console, injected-script, edited-plugin, or debug setup in a separate `diagnostic_intervention` lane. A qualifying result still requires a player-accessible vanilla sequence.

## Current offline evidence

The GOG 1.6.1179.0 hit-resolution trace selects AV11/12 after scanning worn ARMO entries for positive base rating; the receiver points argument and protection outcome remain incompletely measured ([EV-0222], [EV-0223]). It is not an RVA or runtime result for Steam 1.6.1170.0. The bounded private community screen is only an untrusted lead ([EV-0283]).
