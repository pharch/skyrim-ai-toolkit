# Skyrim AE Glitch-Research Harness

An offline-first Codex workspace for evidence-backed research into Skyrim
Anniversary Edition engine behavior. It is a research harness, not a mod pack,
installer, or mod-authoring workflow. Priority objectives are level-one quest
and encounter initiation, and effective armor with zero hit-earned armor XP.

No exploit is verified merely because a frontier item is open. See STATE.md,
research/FRONTIER.json, and research/CLAIMS.md.

## Start here

Create the Python environment, then run checks and the tool doctor:

    conda env create -f environment.yml
    python3 scripts/python_env.py check
    python3 scripts/python_env.py run --require-conda scripts/setup_research.py init
    python3 scripts/python_env.py run --require-conda scripts/setup_research.py check
    python3 scripts/python_env.py run --require-conda tools/domain_doctor.py
    python3 scripts/python_env.py run -m pytest -q

The dispatcher selects the named Conda environment when available and
otherwise reports a system-Python fallback. Agent-facing tools use Python;
a Python adapter may call a verified native research application such as
Ghidra. Project guidance is in AGENTS.md and .agents/skills/.

Local paths and research corpora belong in ignored config/local.env and
.local/. Do not commit game files, saves, raw exports, local logs, private
Discord data, or personal paths.

## Skyrim AE targeting

The supported executable is SkyrimSE.exe with ProductVersion 1.6.318 or newer.
Configure SKYRIM_EDITION=AE, GAME_ROOT, SKYRIM_DATA, and the selected profile's
explicit PLUGINS_TXT in ignored config/local.env. `scripts/local_paths.py sync`
fills empty local paths from the ignored registry. Run the Python ae_preflight.py
before SSEEdit or live access. MO2 users must select the profile's virtualized
plugins.txt; a global list is not a substitute. See docs/getting-started.md for
the maintained branch and Windows checkout steps.

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
established. The Python Ghidra adapter invokes the
installed headless tool after verifying the AE executable. The PEX helper
extracts a narrow stream from the base Misc BSA to ignored `.local/` storage;
it is not a general BSA extractor or full decompiler. `skse_probe.py` verifies
local SKSE/Address Library file metadata only. xEdit is gated on the selected
profile, CommonLib on a working build toolchain, and a live SKSE handshake on
an already running game. UESP and Apocrypha use ignored local databases with
separate provenance and privacy limits.

Never treat setstage, setlevel, injected scripts, altered plugins, or patched
executables as a vanilla-valid result. Do not write to original game files,
plugins, archives, saves, or co-saves.
