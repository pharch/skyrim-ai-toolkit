# Protocol

## Target and version

- Current AE executable ProductVersion/hash: **unknown**; must come from `python3 scripts/python_env.py run tools/ae_preflight.py` on Windows.
- Active plugin order: **unknown**; verify the complete selected profile, including the explicit MO2 `plugins.txt` if used.
- Historical report build: source reports identify a five-master GOG static corpus, but the exact current input hashes are not attached to this import.
- Lane now: `mechanism_inference`. No runtime action is scheduled until target and order are verified.

## Baseline and rollback

Use a clean level-one save from the verified vanilla profile, copied before the candidate. Record level, quest running state, stage, objective state, and relevant alias/reference state. Restore the copy between each candidate and control. Do not use console stage/level commands, forced aliases, injected items, or edited plugins.

## Minimal controls and observations

1. Select one candidate only (DA07 pamphlet, Haknir, or DA14 trigger) and resolve its complete winning-record/script/placed-reference chain first.
2. Record the gated helper's level predicate, quest start/stop state, alias fill event, placed-reference enabled state, and exact player action.
3. Candidate observation: run only the ordinary action at level 1 and capture quest stage/running state before and after.
4. Control: use the ordinary gated route on a disposable above-threshold copy, confirming the relevant event and instrumentation can observe the expected transition.

## Instrumentation and result rule

Required gate: `python3 scripts/python_env.py run tools/ae_preflight.py` before xEdit/live access. The current WSL shell cannot retrieve ProductVersion and no complete active order is configured, so no xEdit/game command is available. Keep any raw record/export output in ignored `.local/`; summarize source identity, executable ProductVersion/hash, profile `plugins.txt` hash, save hash, and exact stage/alias deltas in this experiment's Markdown. A stage change is not a vanilla bypass unless the level remains 1 and no diagnostic intervention occurred.
