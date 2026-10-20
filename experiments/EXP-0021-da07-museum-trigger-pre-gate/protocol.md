# EXP-0021 protocol

## Competing models and predicted outcomes

- **H1 — alternate start after clip entry:** A player stays level 1, clips into Silus's house through a reproducible vanilla movement glitch, enters one artifact trigger, and observes DA07MuseumScenes start plus its intro scene's completion transition to DA07intro stage 200 and main DA07 stage 5.
- **H2 — Silus scene-readiness gate:** The trigger can set/start DA07MuseumScenes, but the intro scene cannot complete while Silus is initially disabled or the Silus alias has no loaded 3D; the HasLoaded3D condition or alias fill blocks stage 200/5.
- **H3 — stage-only or failed startup:** SetStage does not start the stopped quest on the target runtime, or the stage/scene flags change without useful DA07 introduction, dialogue, or progression.

## Required target and baseline

1. Verify the actual SkyrimSE.exe ProductVersion and exact complete active order for the selected target. If MO2 manages the target, use its selected profile's full plugins.txt. Keep Steam 1.6.1170 evidence separate from GOG Ghidra evidence.
2. Use a fresh disposable save that has never started DA07/DA07MuseumScenes and records numeric character level 1. Preserve a baseline copy; do not edit it.
3. Use a read-only observer that can report numeric level, quest running/stage state, alias reference IDs, scene start/completion, and relevant player location. If any required field is unavailable, record the exact gap and do not infer it from the journal alone.
4. Run a time-matched control in which the player stays outside the house and does not cross any Museum trigger.

## Candidate sequence

1. Reproduce and document the player-only clipping sequence needed to enter Silus's house. Do not use console, injected scripts, moved actors, altered plugins, or save edits.
2. Record video/screenshots showing character level and the player's route through the entrance. Preserve the exact timing and any variability.
3. Enter one artifact trigger naturally. Record which trigger was crossed and whether the museum quest/scene changes without touching Silus or other actors.
4. Capture read-only state before and after: DA07MuseumScenes running/stage; Silus alias fill and HasLoaded3D result if available; DA07MuseumIntroScene and DA07MuseumTapestriesScene state; DA07intro running/stage; main DA07 running/stage; actual dialogue/objective progression; numeric player level.
5. Repeat from a fresh disposable save at least once if the first candidate shows a useful transition. Keep the no-entry control under the same active order and timing.

## Interpretation

- A journal entry or stage field alone is not enough. H1 requires the scene transition and a useful gated quest/event progression while level remains 1.
- If the museum quest starts but its scene does not complete, distinguish alias-unfilled, actor-not-loaded, scene-condition failure, and missing observation capability.
- A failed physical clip attempt does not falsify all house-entry glitches; preserve the exact method and scope.
- Console `setstage`, `startquest`, `setlevel`, script injection, actor movement, modified plugins, or altered saves are diagnostic interventions only and cannot validate H1.

## Evidence handling

Keep raw video, snapshots, save copies, and private paths under ignored `.local/`. Record hashes, exact target identity, full active order, tool versions, and timestamps in the evidence note. Analyze disposable save copies read-only with the documented save-state route. No original game, plugin, archive, save, or co-save may be modified.
