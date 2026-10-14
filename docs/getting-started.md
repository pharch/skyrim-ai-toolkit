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
in Codex. Create the named Conda environment:

    conda env create -f environment.yml
    python3 scripts/python_env.py check
    python3 scripts/python_env.py run --require-conda scripts/setup_research.py init
    python3 scripts/python_env.py run --require-conda scripts/setup_research.py check
    python3 scripts/python_env.py run --require-conda tools/domain_doctor.py
    python3 scripts/python_env.py run -m pytest -q

The dispatcher chooses this environment when available. If Conda is absent,
it reports and uses current Python. Python adapters can call native tools
when their target and safety gates pass. Keep local paths in config/local.env
and corpora under ignored .local/.

## 2. Verify the AE installation

Set paths in ignored `.local/research-paths.toml`, then run
`python3 scripts/python_env.py run scripts/local_paths.py sync` to fill empty
values in ignored `config/local.env`, including `SKYRIM_DATA`. Set
`SKYRIM_EDITION=AE`, `GAME_ROOT`, and `PLUGINS_TXT` there. For MO2,
`PLUGINS_TXT` must name the selected profile's explicit `plugins.txt`; the
global profile is not a safe substitute. Path sync does not guess the selected
profile.

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
- Ghidra: tools/ghidra_probe.py --analyze imports into a fresh ignored project;
  without --analyze it runs a read-only query against an existing project.
  Native analysis can take a long time; inspect saved logs before retrying.
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
