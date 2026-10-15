# Skyrim AE glitch research

This repository supports ongoing, evidence-backed research into Skyrim Anniversary Edition engine behavior and reproducible vanilla-compatible glitches. It is not a mod-authoring toolkit. The active bounty and evidence bar are in [`bounties/BOUNTY-0001-LEVEL1-P0.md`](bounties/BOUNTY-0001-LEVEL1-P0.md); permanent research instructions are in [`AGENTS.md`](AGENTS.md).

## Start here

Read `AGENTS.md`, the current checkpoint in `STATE.md`, and the selected frontier item. The canonical runtime contract documents the host-specific bootstrap, ignored local configuration, tested tool commands and their limits: [`docs/LOCAL_RUNTIME_CONTRACT.md`](docs/LOCAL_RUNTIME_CONTRACT.md). Bootstrap or reuse Python 3.12, validate the relevant tools, then continue the frontier. A missing environment is repaired by bootstrap; once validation passes, research remains the active task.

Typical Linux/WSL start:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
python3 scripts/python_env.py run scripts/harness_doctor.py static
```

In Windows PowerShell, start each command with `py -3.12` instead of `python3`. Native Windows is preferred for game-connected operations; WSL has an independent persistent environment.

## Research memory

- `research/FRONTIER.json` and `research/RECOVERY.json` select and resume work.
- `research/EVIDENCE.json`, `CLAIMS.md`, `MECHANISMS.md`, `CONTRADICTIONS.md`, and `KNOWLEDGE_GRAPH.md` preserve sourced conclusions and uncertainty.
- `experiments/` stores hypotheses, protocols, results and implications. `research/SESSION_LOG.md` and `STATE.md` checkpoint the exact next action.
- `research/LEGACY_IMPORT.md` and its hash map retain provenance for imported historical research.

Never infer a negative result from an empty, partial or unverified input. Do not write to protected game files or baseline saves.
