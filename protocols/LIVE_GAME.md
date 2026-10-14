# Skyrim AE live-test protocol

## Lanes

- `offline`: records, Ghidra, decompilation, save copies, parsers, and test
  fixtures. Default for autonomous work.
- `diagnostic_intervention`: isolated disposable save and explicitly tagged
  interventions used only to locate a mechanism. Such evidence is not a vanilla
  exploit.
- `vanilla-validation`: a clean baseline with observational instrumentation
  only, reproducing the player-available sequence without altering conditions.

## AE identity gate

Before any live tool call, run `python3 scripts/python_env.py run tools/ae_preflight.py` on Windows. Confirm
the detected `SkyrimSE.exe` ProductVersion is 1.6.318+, the executable hash
matches the intended install, and the load-order path/hash identifies the
selected AE profile. `GAME_ROOT` and a named plugin are not sufficient identity
evidence. Stop on a runtime/profile mismatch.

DevBench is optional and is not bundled. The operator installs it through the
mod manager. Use `alive` before other requests and confirm process identity
matches the AE target. The API may answer while the game's main thread is
blocked; `ping` alone is not evidence that gameplay is advancing.

## Before and after each experiment

Record game build, SKSE version, load-order hash, save identifier/hash, lane,
instrumentation version, test objective, competing hypotheses, preconditions,
expected outcomes, observables, exact commands, rollback, and data destination.
Use a duplicated disposable save for any diagnostic intervention. Preserve the
original save and co-save. Capture before/after state and raw output; never
overwrite a unique baseline.

- Quest target: retain player level 1 and track skill/character XP, real quest
  start, journal visibility, stage transitions, aliases, world changes, event
  initiation, and every trigger/precondition. `setstage` or `startquest` is
  diagnostic only.
- Armor target: verify the incoming hit/damage event, worn armor, coverage,
  rating, armor skill XP before/after, race/perks, combat state, and damage
  absorption. A miss or prevented hit is a false positive.
- Enchanting: track cumulative skill XP and underlying threshold, not only a
  crafting UI level.
- Alchemy: distinguish displayed duration, remaining ActiveEffect instance,
  reapplied/ability/enchantment effects, and save/load persistence.

Stop that experiment if the executable/profile changes, baseline becomes
uncertain, data is corrupted, the game enters a crash loop, or the tool returns
an unsupported schema. Continue with offline work and record the blocker.
Unattended Codex cycles may not call DevBench mutators, save/load, console
commands, or arbitrary MCP tools.
