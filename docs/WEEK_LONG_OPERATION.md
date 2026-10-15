# Continuing research across sessions

Research proceeds in interactive Codex sessions and durable repository records. Do not schedule unattended fresh threads or imply uninterrupted execution. The frontier is a continuing program: complete, block or narrow one question, reselect the next independent tractable question, and periodically synthesize the causal model.

## Session start

1. Follow the required-context list and active bounty in `AGENTS.md`.
2. Bootstrap/reuse Python 3.12, run `python_env.py check --strict`, then `research_state.py validate`. If Python preflight fails, run bootstrap repair and repeat the check.
3. Run the doctor mode relevant to the selected source. Static research may proceed without a profile-specific MO2 list or live SKSE connection.
4. Resume the transaction named in `research/RECOVERY.json`, or select the highest-information-gain ready frontier item. State rival models, predicted discriminants, source/tool and exact next action before data collection.

## Checkpoint and recovery

Before a context or CLI boundary, update `STATE.md`, `research/FRONTIER.json`, and `research/SESSION_LOG.md` with completed work, evidence/artifact hashes, scope and the exact next action. Keep raw data below ignored `.local/`; put concise evidence IDs and negative results in the research ledgers.

Validate before resuming. If `research/RECOVERY.json` has status `running`, use:

```sh
python3 scripts/python_env.py run scripts/research_state.py recover --root .
python3 scripts/python_env.py run scripts/research_state.py validate
```

Inspect partial outputs and the durable-state diff; resume only from the recovered `next_action`. Interruption is not evidence of completion. On Windows, start the dispatcher with `py -3.12`.

## Synthesis and reselection

After several substantive investigations, a surprising result or a major contradiction, compare recent findings across quests, combat XP, ActiveEffects, crafting and serialization. Add graph links only for a supported relationship. Generate successor questions with distinct predicted outcomes and an actionable source route. Preserve negative results, scope and unresolved alternatives. When a lane is blocked, queue the precise external test and continue independent static work.
