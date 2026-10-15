# Skyrim AE Glitch-Research Harness

An offline-first Codex workspace for evidence-backed research into Skyrim
Anniversary Edition engine behavior. It is a research harness, not a mod pack,
installer, or mod-authoring workflow. Priority objectives are level-one quest
and encounter initiation, and effective armor with zero hit-earned armor XP.

No exploit is verified merely because a frontier item is open. See STATE.md,
research/FRONTIER.json, and research/CLAIMS.md.

## Start here

Start with `docs/LOCAL_RUNTIME_CONTRACT.md` and bootstrap the host's persistent
Python 3.12 environment. Windows PowerShell:

    py -3.12 scripts/bootstrap_python.py
    py -3.12 scripts/setup_research.py init
    py -3.12 scripts/python_env.py check --strict
    py -3.12 scripts/python_env.py run scripts/research_state.py validate
    py -3.12 scripts/python_env.py run scripts/harness_doctor.py all

Linux/WSL:

    python3 scripts/bootstrap_python.py
    python3 scripts/setup_research.py init
    python3 scripts/python_env.py check --strict
    python3 scripts/python_env.py run scripts/research_state.py validate
    python3 scripts/python_env.py run scripts/harness_doctor.py all

Bootstrap creates or repairs the Git-ignored host environment under `.local/`
from the single pinned `requirements.txt` specification. Research tools run
only through the strict dispatcher. If a preflight fails, bootstrap repairs
the environment before the failure is treated as an external blocker. The
setup-only initializer creates `config/local.env` from its example only if
absent and preserves existing machine bindings. Native
Windows is preferred for game-connected research; WSL uses a separate
environment. Project guidance is in AGENTS.md and `.agents/skills/`.

Local paths and research corpora belong in ignored config/local.env and
.local/. Do not commit game files, saves, raw exports, local logs, private
Discord data, or personal paths.

## Skyrim AE targeting

The supported runtime is SkyrimSE.exe with ProductVersion 1.6.318 or newer.
Copy `config/local.env.example` to ignored `config/local.env` and bind the
runtime, tools, and selected profile there. Run the dispatched
`scripts/local_paths.py doctor` to check bindings and `tools/ae_preflight.py`
before xEdit or live access. MO2 users must set the selected profile's
explicit `plugins.txt`; a global list is not a substitute. Ghidra uses the
separately configured existing GOG project and analysis binary, regardless
of the runtime store. See [the runtime contract](docs/LOCAL_RUNTIME_CONTRACT.md),
[current readiness](docs/HARNESS_READINESS.md),
[tool bindings](docs/LOCAL_TOOL_BINDINGS.md), and
[getting started](docs/getting-started.md).

## Research durability

- research/FRONTIER.json is the machine-readable queue with evidence links
  and discriminating next actions.
- CLAIMS.md, CONTRADICTIONS.md, and KNOWLEDGE_GRAPH.md hold sourced claims
  and causal links.
- SESSION_LOG.md and STATE.md provide an exact recovery checkpoint.
- docs/WEEK_LONG_OPERATION.md explains interactive checkpoints and recovery.
- Observations, inferences, diagnostic interventions, and vanilla
  reproductions remain distinct.

## Tool limits

The plugin reader supports file-level TES4 inspection with raw subrecords and
has a synthetic explicit-order winner fixture; no real profile winner is
established until the selected full order passes preflight. The Python Ghidra
adapter verifies and queries the existing GOG project with `-process`,
`-noanalysis`, and `-readOnly`; it never imports or auto-analyzes a binary.
`tools/xedit_bridge.py` stages the configured helper and prepares a scoped
view. Its `file-records` command is the read-only bridge record retrieval,
implemented as a direct TES4 file parser rather than native xEdit. A native
record-tree export is not currently reproduced. `skse_probe.py` reports
installed file identity only and never establishes an SKSE connection or
observation. The PEX helper extracts a narrow stream from the base Misc BSA
to ignored `.local/` storage; it is not a general BSA extractor or full
decompiler. Live observation needs a separate disposable profile/save, a
deployed Observer, and verified handshake/snapshot. The build-attested
Address Library adapter reuses the retained legacy decoder and does not
transfer a GOG RVA to another executable build. UESP and Apocrypha use ignored
local databases with separate provenance and privacy limits.

Never treat setstage, setlevel, injected scripts, altered plugins, or patched
executables as a vanilla-valid result. Do not write to original game files,
plugins, archives, saves, or co-saves.
