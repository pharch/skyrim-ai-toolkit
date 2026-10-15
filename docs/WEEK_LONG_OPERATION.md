# Continuing research across sessions

Research proceeds in interactive Codex sessions and durable repository records. Do not schedule unattended fresh threads or imply uninterrupted execution. The frontier is a continuing program: complete, block or narrow one question, reselect the next independent tractable question, and periodically synthesize the causal model. The user starts or resumes work with the single prompt in [`RESEARCH_START_PROMPT.md`](RESEARCH_START_PROMPT.md); all validation and recovery calls below are internal Codex operations, not a user-run start procedure.

## Session start

1. Follow the required-context list and active bounty in `AGENTS.md`.
2. Bootstrap/reuse Python 3.12, run the strict check, then validate research state. If Python preflight fails, repair it autonomously and repeat validation.
3. Run the doctor mode relevant to the selected source. Static research may proceed without a profile-specific MO2 list or live SKSE connection.
4. Inspect `research/RECOVERY.json`: recover and resume the matching running/interrupted investigation, or select the highest-information-gain ready item and generate a unique transaction ID internally. State rival models, predicted discriminants, source/tool and exact next action before data collection.

## Checkpoint and recovery

Before a context or CLI boundary, update `STATE.md`, `research/FRONTIER.json`, and `research/SESSION_LOG.md` with completed work, evidence/artifact hashes, scope and the exact next action. Keep raw data below ignored `.local/`; put concise evidence IDs and negative results in the research ledgers. The user does not need to issue a follow-up command; Codex performs recovery and continuation.

Validate before resuming. If `research/RECOVERY.json` has status `running`, use:

```sh
python3 scripts/python_env.py run scripts/research_state.py recover --root .
python3 scripts/python_env.py run scripts/research_state.py validate
```

Inspect partial outputs and the durable-state diff; resume only from the recovered `next_action`. Interruption is not evidence of completion. On Windows, start the dispatcher with `py -3.12`.

## Synthesis and reselection

After several substantive investigations, a surprising result or a major contradiction, compare recent findings across quests, combat XP, ActiveEffects, crafting and serialization. Add graph links only for a supported relationship. Generate successor questions with distinct predicted outcomes and an actionable source route. Preserve negative results, scope and unresolved alternatives. When a lane is blocked, queue the precise external test and continue independent static work.
