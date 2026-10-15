# Local tool bindings

The active configuration and exact invocation source of truth is
docs/LOCAL_RUNTIME_CONTRACT.md. This file summarizes the machine bindings and
evidence boundary. Keep all absolute paths in ignored config/local.env; do not
copy them, game files, saves, Ghidra databases, private exports, or binaries
into tracked Git. The retired .local/research-paths.toml file is not read or
synchronized by active tools.

## Separate the runtime and static targets

The game runtime is resolved from SKYRIM_EDITION=AE, GAME_ROOT,
SKYRIM_EXE_PATH, SKYRIM_DATA, and a selected MO2 profile's explicit
MO2_PROFILE_DIR plus PLUGINS_TXT. ProductVersion comes from the configured
SkyrimSE.exe. A full-order preflight requires a readable complete plugins.txt
inside the explicitly selected profile.

The Ghidra lane is separately bound by GHIDRA_ANALYSIS_EXE_GOG,
GHIDRA_PROJECT_REP_PATH, GHIDRA_PROJECT_PROGRAM, and GHIDRA_HEADLESS_EXE.
The project path names the existing `.rep` data directory; the probe reads it
from ignored `config/local.env`, derives the Ghidra directory/name, and checks
for the matching `.gpr` before invocation. `.local/ghidra/` stores private
query and binding-verification artifacts, not project configuration. The
Ghidra lane points to the existing GOG AE 1.6.1179.0 analysis; the runtime may
be Steam AE 1.6.1170. Do not transfer an RVA across those builds without
independent mapping evidence.

The xEdit helper source is identified by LEGACY_SKYRIM_REPO. Toolkit bindings
SSEEDIT_EXE, SKYRIM_DATA, XEDIT_SCRIPTS, SKYRIM_EXE_PATH, and
INCLUDE_CREATION_CLUB are translated into the helper's derived ignored
configuration by tools/xedit_bridge.py. The source checkout is read-only.
Scoped five-master preparation and the selected MO2 full order are distinct.

The live-test lane has separate SKYRIM_TEST_PROFILE_DIR,
SKYRIM_TEST_PLUGINS_TXT, RESEARCH_TEST_SAVE, SKYRIM_OBSERVER_DEPLOYED_DLL,
and SKYRIM_OBSERVER_LOG_DIR bindings. Keep these empty until a disposable lane
is designated. SKYRIM_OBSERVER_STAGED_DLL only identifies a local build
artifact. DEVBENCH_PORT is reserved and no active toolkit command connects to
it.

## Commands

Bootstrap and verify the repository-local Python 3.12 environment as
documented in docs/LOCAL_RUNTIME_CONTRACT.md. The strict dispatcher does not
fall back to Conda or system Python.

    python3 scripts/python_env.py check --strict
    python3 scripts/python_env.py run scripts/local_paths.py doctor
    python3 scripts/python_env.py run tools/ae_preflight.py
    python3 scripts/python_env.py run tools/xedit_bridge.py doctor
    python3 scripts/python_env.py run tools/xedit_bridge.py prepare
    python3 scripts/python_env.py run tools/address_library_probe.py --symbol MagicItem::CalculateCost
    python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x14C020 --timeout 600
    python3 scripts/python_env.py run tools/skse_probe.py
    python3 scripts/harness_doctor.py all

Use docs/HARNESS_READINESS.md to distinguish this cold-start's successful
file-level xEdit helper checks from its blocked native record export, Ghidra
query, and live Observer connection. Historical EV-0165–EV-0191 remain
historical evidence and do not prove current-session access.

## Read-only handling

Path and domain doctors report statuses; they do not launch native tools.
Ghidra probes are confined to the existing GOG project and request
-process/-noanalysis/-readOnly. xEdit helper doctor stages the fixed source
files into ignored .local and retains private raw outputs. xEdit prepare writes
an isolated five-master view session but does not launch SSEView. The
file-records subcommand is the bridge’s read-only record retrieval, implemented
by parsing plugin bytes; it is not native SSEEdit record-tree export or a
winning override.

The SKSE identity probe checks installed files only. The Observer is not
deployed or loaded in the current cold-start. A build artifact, staged DLL,
or configured path is not a live handshake or game-state observation. Never
launch Skyrim from an unattended doctor and never write to original game,
plugin, archive, save, or co-save files.

Linux/WSL validation does not establish Windows MO2/SSEEdit behavior or
in-game AE behavior.
