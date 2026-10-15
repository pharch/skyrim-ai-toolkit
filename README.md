# Skyrim AE glitch research

This repository supports ongoing, evidence-backed research into Skyrim Anniversary Edition engine behavior and reproducible vanilla-compatible glitches. It is not a mod-authoring toolkit. The active bounty and evidence bar are in [`bounties/BOUNTY-0001-LEVEL1-P0.md`](bounties/BOUNTY-0001-LEVEL1-P0.md); permanent research instructions are in [`AGENTS.md`](AGENTS.md).

## Start here

Open the checkout in an interactive Codex session and paste the single
[`research-start prompt`](docs/RESEARCH_START_PROMPT.md). Codex reads the
checkpoint and active bounty, bootstraps or repairs the persistent Python 3.12
environment when needed, validates the relevant source route, resumes work and
continues the frontier. Users do not need to run Python research commands,
select frontier IDs or manage transaction IDs. The canonical runtime contract
documents internal tool invocations and host limits:
[`docs/LOCAL_RUNTIME_CONTRACT.md`](docs/LOCAL_RUNTIME_CONTRACT.md).

## Research memory

- `research/FRONTIER.json` and `research/RECOVERY.json` select and resume work.
- `research/EVIDENCE.json`, `CLAIMS.md`, `MECHANISMS.md`, `CONTRADICTIONS.md`, and `KNOWLEDGE_GRAPH.md` preserve sourced conclusions and uncertainty.
- `experiments/` stores hypotheses, protocols, results and implications. `research/SESSION_LOG.md` and `STATE.md` checkpoint the exact next action.
- `research/LEGACY_IMPORT.md` and its hash map retain provenance for imported historical research.

Never infer a negative result from an empty, partial or unverified input. Do not write to protected game files or baseline saves.
