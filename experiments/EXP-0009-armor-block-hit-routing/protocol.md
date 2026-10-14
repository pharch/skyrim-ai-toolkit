# Protocol

## Target and version

- Current AE executable ProductVersion/hash: **unknown**; required command is `python3 scripts/python_env.py run tools/ae_preflight.py` on Windows.
- Complete active plugin order/profile: **unknown**; MO2 requires the selected profile's explicit `plugins.txt`.
- Historical report build: GOG native-analysis claim; exact matched binary identity is not revalidated here.
- Lane now: `mechanism_inference`; no hit test is scheduled.

## Baseline and rollback

Make a disposable copy of a verified vanilla save. Record Heavy/Light Armor and Block levels, raw progress, next thresholds, armor form and positive DNAM, and damage/protection controls. Restore the same baseline before each variant. Do not use invulnerability, console, altered plugins, or state-mutating probes.

## Matched control and candidate

1. Confirm observer read-only handshake/liveness and exact executable identity before any live call.
2. Control: take a reproducible unblocked physical hit from the same attacker/weapon; capture hit validity, total/physical damage, flags, armor mitigation, calls to AV9/11/12, and raw AVSK before/after.
3. Candidate: reload baseline, wear the same armor, block the matched hit, and capture the same fields plus the exact Block amount and budget delta.
4. Reject a run if damage source/attack differs materially or the observer loses liveness.

## Interpretation

Evidence for the candidate requires a real incoming hit, measured armor contribution, no Heavy/Light award, and Block progress below the remaining budget. Skipped AV11/12 with positive AV9 is armor-XP redirection only. Preserve raw trace, save identity, tool versions, control/candidate ordering, and negative outcomes. Do not infer zero from an unchanged displayed skill level.
