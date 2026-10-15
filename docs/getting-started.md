# Getting started: Skyrim AE research checkout

## 0. Check out the research branch safely

Keep this repository outside the Skyrim installation. On an existing clone,
switch to and verify the maintained branch before setting up tools:

    git switch glitch-hunting-setup
    git branch --show-current

The second command should print `glitch-hunting-setup`. Run repository scripts
from this checkout, never from the game `Data` directory.

## 1. Prepare the Python environment

Clone this research repository outside the Skyrim installation and open it
in Codex. Check the Python dispatcher and initialize repository-local state:

    python3 scripts/python_env.py check
    python3 scripts/python_env.py run scripts/setup_research.py init
    python3 scripts/python_env.py run scripts/setup_research.py check
    python3 scripts/python_env.py run tools/domain_doctor.py
    python3 scripts/python_env.py run -m unittest discover -s tests -v

The dispatcher chooses `skyrim-ae-research` when Conda and that environment
are available. Otherwise it reports the system-Python fallback. Do not install
Ghidra, xEdit, CommonLib, or game tooling to satisfy a clone or doctor check.
Python adapters call existing native tools only when their target and safety
gates pass. Keep machine paths in `config/local.env` and corpora under ignored
`.local/`.

## 2. Verify the AE installation

Copy `config/local.env.example` to ignored `config/local.env` and bind paths
directly there. `scripts/local_paths.py doctor` reads only that file; it never
syncs a second registry or prints configured values. Bind `SKYRIM_EDITION=AE`,
`GAME_ROOT`, `SKYRIM_EXE_PATH`, `SKYRIM_DATA`, `MO2_PROFILE_DIR`, and the
selected profile's `PLUGINS_TXT`. For MO2,
`PLUGINS_TXT` must name the selected profile's explicit `plugins.txt`; the
global profile is not a safe substitute. Do not guess which profile is active.
Set the GOG analysis executable and existing project separately; see
`docs/LOCAL_TOOL_BINDINGS.md`.

    python3 scripts/python_env.py run tools/ae_preflight.py

Preflight reads SkyrimSE.exe ProductVersion, requires runtime 1.6.318 or
newer, hashes the executable and active list, and validates the five required
official masters. It does not prove MO2 launched that same profile; compare
the reported path/hash with the selected profile. A typed version is not
evidence. --probe-executable does not pass the full xEdit/live gate.

## 3. Validate repository and tools

    python3 scripts/python_env.py run -m pytest -q
    python3 scripts/python_env.py run scripts/validate_research.py
    python3 scripts/python_env.py run scripts/research_state.py validate
    python3 scripts/python_env.py run scripts/validate_overlay.py
    python3 scripts/python_env.py run tools/domain_doctor.py

Offline fixtures do not establish Windows or in-game behavior.

## 4. Use local knowledge sources

Authorized UESP and private Apocrypha corpora live only under ignored .local/.
Use the Python tools. UESP source acquisition URL, license, and completeness
remain unverified. Apocrypha results are private untrusted leads; do not copy
message content or identifiers into tracked research.

## 5. Route other evidence

- Plugin records: plugin_reader.py reads one explicit plugin and can emit raw
  subrecords. It does not resolve a winning override.
- SKSE co-save: cosave-info.py is a read-only structural survey.
- Installed SKSE/Address Library identity: `python3 scripts/python_env.py run
  tools/skse_probe.py` reads local file versions and hashes only; it does not
  launch Skyrim or prove a live SKSE/DevBench handshake.
- Papyrus and crash logs: use the Python triage tools and preserve coverage.
- Ghidra: `python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]`
  queries the existing GOG project using `-process -noanalysis -readOnly`.
  This route cannot import or create a project. `GHIDRA_ANALYSIS_EXE_GOG` and
  `GHIDRA_PROJECT_REP_PATH/PROGRAM` are separate from the runtime target. The
  probe reads the full existing `.rep` path from ignored `config/local.env` and
  checks its adjacent `.gpr` before invocation.
- CommonLib/Address Library: `python3 scripts/python_env.py run
  tools/address_library_probe.py --symbol Namespace::Name` reads the matching
  GOG ProductVersion and Address Library, then obtains the AE ID from the
  configured CommonLib `Offsets.h`; it reports build-specific RVAs.
- CommonLib, xEdit, and live SKSE require their native prerequisites and
  applicable AE/profile gates. No xEdit call is allowed while the selected
  MO2 profile remains unidentified.
- Use retained read-only archive/save procedures and report exact coverage.

See protocols/TOOL_ROUTING.md and .agents/skills/retained-tool-operations/SKILL.md.

## 6. Resume a session

Read AGENTS.md, NORTH_STAR.md, STATE.md, ROADMAP.md,
research/FRONTIER.json, protocols/TOOL_ROUTING.md, and the recovery record.
Inspect partial outputs before continuing; do not infer success from a process
launch or incomplete output.
