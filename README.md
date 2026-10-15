# Skyrim AE Glitch-Research Harness

An offline-first Codex workspace for evidence-backed research into Skyrim
Anniversary Edition engine behavior. It is a research harness, not a mod pack,
installer, or mod-authoring workflow. Priority objectives are level-one quest
and encounter initiation, and effective armor with zero hit-earned armor XP.

No exploit is verified merely because a frontier item is open. See STATE.md,
research/FRONTIER.json, and research/CLAIMS.md.

## Start here

Use the Python dispatcher, then run checks and the tool doctor:

    python3 scripts/python_env.py check
    python3 scripts/python_env.py run scripts/setup_research.py init
    python3 scripts/python_env.py run scripts/setup_research.py check
    python3 scripts/python_env.py run tools/domain_doctor.py
    python3 scripts/python_env.py run -m unittest discover -s tests -v

The dispatcher selects the named Conda environment when available and
otherwise reports a system-Python fallback. Agent-facing tools use Python;
a Python adapter may call a verified native research application such as
Ghidra. `environment.yml` describes the optional named environment; do not
install local native applications as part of cloning or binding. Project
guidance is in AGENTS.md and .agents/skills/.

Local paths and research corpora belong in ignored config/local.env and
.local/. Do not commit game files, saves, raw exports, local logs, private
Discord data, or personal paths.

## Skyrim AE targeting

The supported runtime is SkyrimSE.exe with ProductVersion 1.6.318 or newer.
Copy `config/local.env.example` to ignored `config/local.env` and bind the
runtime, tools, and selected profile there. Run
`python3 scripts/python_env.py run scripts/local_paths.py doctor` to check
bindings. Run `tools/ae_preflight.py` before xEdit or live access. MO2 users
must set the selected profile's explicit virtualized `plugins.txt`; a global
list is not a substitute. Ghidra uses the separately configured existing GOG
project and analysis binary, regardless of the runtime store. See
[docs/LOCAL_TOOL_BINDINGS.md](docs/LOCAL_TOOL_BINDINGS.md) and
[docs/getting-started.md](docs/getting-started.md).

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
The PEX helper
extracts a narrow stream from the base Misc BSA to ignored `.local/` storage;
it is not a general BSA extractor or full decompiler. `skse_probe.py` verifies
local SKSE/Address Library file metadata only. xEdit is gated on the selected
profile and a live SKSE handshake on an already running game. The
build-attested Address Library adapter reuses the retained legacy decoder and
does not transfer a GOG RVA to another executable build. UESP and Apocrypha use ignored local databases with
separate provenance and privacy limits.

Never treat setstage, setlevel, injected scripts, altered plugins, or patched
executables as a vanilla-valid result. Do not write to original game files,
plugins, archives, saves, or co-saves.
