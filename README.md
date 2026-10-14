# Skyrim AE Glitch-Research Harness

An offline-first Codex workspace for evidence-backed research into Skyrim
Anniversary Edition engine behavior. It is a research harness, not a mod pack,
game installer, or mod-authoring workflow. Priority objectives are level-one
quest/encounter initiation and effective armor with zero hit-earned armor XP.

No exploit is verified merely because a frontier item is open. See
[STATE.md](./STATE.md), [research/FRONTIER.json](./research/FRONTIER.json), and
the [claims ledger](./research/CLAIMS.md).

## Start here

Create the Python Conda environment, then run the repository checks and tool
doctor:

```text
conda env create -f environment.yml
python3 scripts/python_env.py check
python3 scripts/python_env.py run --require-conda scripts/setup_research.py init
python3 scripts/python_env.py run --require-conda scripts/setup_research.py check
python3 scripts/python_env.py run --require-conda tools/domain_doctor.py
python3 scripts/python_env.py run --require-conda -m pytest tests/ -q
```

Agent commands can use `python3 scripts/python_env.py run ...`; the dispatcher
selects the named Conda environment when available and otherwise reports a
system-Python fallback. The environment manifest is the source of truth for
Python and test dependencies. Agent tools do not use Node or shell launchers.
Project guidance is in [AGENTS.md](./AGENTS.md), with procedures in
[.agents/skills/](./.agents/skills/).

Local paths and research corpora belong in ignored `config/local.env` and
`.local/`. Do not commit game files, saves, co-saves, raw exports, local logs,
private Discord data, or personal paths. `migration/PRE_PUSH_SETUP_SUMMARY.md`
reports the current ignore, tool, and platform status for reviewers.

## Skyrim AE targeting

The supported executable is `SkyrimSE.exe` with ProductVersion 1.6.318 or
newer. Configure `SKYRIM_EDITION=AE`, `GAME_ROOT`, and the selected profile's
explicit `PLUGINS_TXT` in ignored `config/local.env`. Run
`python3 scripts/python_env.py run tools/ae_preflight.py` before SSEEdit or live
game access. The gate reads executable metadata and validates the complete
active order; a typed version is not evidence. MO2 users must choose the
selected profile's virtualized `plugins.txt`.

## Research durability

- `research/FRONTIER.json` is the machine-readable queue with explicit evidence
  links and discriminating next actions.
- `research/CLAIMS.md`, `research/CONTRADICTIONS.md`, and
  `research/KNOWLEDGE_GRAPH.md` hold sourced claims and causal links.
- `research/SESSION_LOG.md` and `STATE.md` provide append-only notes and an
  exact recovery checkpoint.
- `docs/WEEK_LONG_OPERATION.md` explains interactive checkpoints and recovery.
- Source observations, inferences, diagnostic interventions, and vanilla
  reproductions remain distinct.

## Tool limits

All active agent-facing commands are Python. The Python plugin reader supports
narrow file-level TES4 inspection; it does not establish winning records.
Ghidra, CommonLibSSE builds, Windows SSEEdit, and live SKSE behavior still need
their installed native tools and a verified AE target/profile. The domain
doctor reports which prerequisites are available without claiming those tools
ran. UESP and Apocrypha queries use ignored local SQLite databases and have
separate provenance/privacy limits.

Never treat `setstage`, `setlevel`, injected scripts, altered plugins, or
patched executables as a vanilla-valid result. Do not write to original game
files, plugins, archives, saves, or co-saves.
