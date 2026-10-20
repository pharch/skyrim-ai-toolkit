# Protocol

## Goal

Determine which documented retained research interfaces have current or durable evidence of use, and which conclusions require optional software, Windows UI, a verified target profile, or live game/Observer state.

## Criteria and limits

- Read `tools/README.md`, `docs/LOCAL_RUNTIME_CONTRACT.md`, and `docs/HARNESS_READINESS.md` as the declared interface contracts.
- Inventory tracked `scripts/` and `tools/` entrypoints without changing them.
- Capture strict Python and research-state checks through the strict dispatcher; use only existing read-only research operations and prior receipts for route claims.
- Treat `file-records` as direct parsing, Ghidra as the matching GOG build/project, native xEdit as five-official-master scope unless an exact full profile is verified, and SKSE file identity as distinct from live connection.
- Do not launch Skyrim, xEdit, or mutate game/profile/save data. Do not add or run unit/integration tests in this audit.
- Record dated prior test/doctor disagreements as unresolved rather than claiming a current pass.

## Reproduction commands

```sh
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
git ls-files scripts tools
```

The first two outputs and tracked inventory hash are preserved privately for EV-0274. Other route capabilities link to existing evidence IDs; their scopes are retained in `results.md` and EV-0274.
