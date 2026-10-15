# Local runtime contract

This file is the active setup and invocation contract for this checkout. The
only machine-specific binding file is ignored config/local.env; raw captures
and derived helper files stay below ignored .local/. Never copy absolute
machine paths, game/plugin bytes, saves, private exports, binaries, or Ghidra
project data into tracked files.

## Python 3.12 environment

Create one repository-local environment. On Windows PowerShell:

    py -3.12 -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install --requirement requirements-dev.txt
    Copy-Item config/local.env.example config/local.env
    # Fill the private bindings described below, then:
    & .\.venv\Scripts\python.exe scripts/python_env.py check --strict
    & .\.venv\Scripts\python.exe scripts/python_env.py run scripts/research_state.py validate
    & .\.venv\Scripts\python.exe scripts/harness_doctor.py all

On Linux/WSL:

    python3 -m venv .venv
    .venv/bin/python -m pip install --requirement requirements-dev.txt
    cp config/local.env.example config/local.env
    # Fill config/local.env, then:
    python3 scripts/python_env.py check --strict
    python3 scripts/python_env.py run scripts/research_state.py validate
    python3 scripts/harness_doctor.py all

If venv creation reports that ensurepip or venv is unavailable, the host's
Python 3.12 venv package is missing. Install that Python prerequisite through
the host's normal package channel, recreate .venv, and repeat the bootstrap.
Do not substitute system Python, Conda, or an ambient environment for research
commands.

requirements.txt pins active runtime third-party imports to lz4==4.3.3 and
PyYAML==6.0.1; other active tools use the standard library. lz4 is required by
scripts/read-save.py, including its --help import path. requirements-dev.txt
includes those runtime pins and pytest==8.0.0 for the CI test runner. The dev
split is deliberate; install requirements-dev.txt for a complete clean setup.
environment.yml is optional Conda alignment metadata, not the active route.
scripts/python_env.py always targets this checkout's .venv, requires Python
3.12 and both pinned imports, and fails closed. check --strict reports setup
status; run returns 127 without starting a child when the venv is missing or
invalid. It never falls back.

scripts/harness_doctor.py all is the bootstrap diagnostic entrypoint. It may
be started with system Python because it must report a missing .venv; this does
not make the system interpreter ready for research. Run research tools only
through scripts/python_env.py run after the repository venv passes.

scripts/research_state.py validate checks durable transaction, frontier,
evidence, claim, and recovery structure. It does not verify executable
ProductVersion, load-order completeness against MO2, xEdit/Ghidra access, save
parsing, or live-game behavior.

## Private configuration schema

Create config/local.env from config/local.env.example. The parser accepts
one KEY=VALUE per line, rejects duplicate keys and malformed quotes, and
does not expand shell variables or consult process-environment fallbacks.
Blank values mean unbound. Path examples below are placeholders, not paths from
this workstation.

| Key | Type and mode | Example | Validation and use |
|---|---|---|---|
| SKYRIM_EDITION | Literal AE; runtime gate | AE | ae_preflight.py requires AE. |
| GAME_ROOT | Absolute game directory | <Skyrim AE install> | Contains SkyrimSE.exe. |
| SKYRIM_EXE_PATH | Optional absolute executable | <GAME_ROOT>\SkyrimSE.exe | Defaults to GAME_ROOT/SkyrimSE.exe; ProductVersion comes from the executable. |
| SKYRIM_DATA | Absolute Data directory | <GAME_ROOT>\Data | xEdit helper binding; path doctor checks accessibility. |
| MO2_PROFILE_DIR | Absolute selected MO2 profile | <MO2 profiles>\<selected profile> | Full-order preflight requires the explicit selected directory. |
| PLUGINS_TXT | Absolute selected plugins.txt | <selected profile>\plugins.txt | Must belong to MO2_PROFILE_DIR and contain the full active list. |
| SKYRIM_TEST_PROFILE_DIR | Absolute disposable profile | <MO2 profiles>\<test profile> | Required by ae_preflight.py --test-profile. |
| SKYRIM_TEST_PLUGINS_TXT | Absolute test plugins.txt | <test profile>\plugins.txt | Must belong to SKYRIM_TEST_PROFILE_DIR and contain the full order. |
| RESEARCH_TEST_SAVE | Absolute disposable save | <test profile save> | Never point at a user's baseline. |
| SKSE_LOADER | Absolute SKSE loader executable | <GAME_ROOT>\skse64_loader.exe | skse_probe.py checks installed file identity; does not launch it. |
| SKYRIM_OBSERVER_STAGED_DLL | Local staged DLL | .local/readiness/<build>/stage/SKSE/Plugins/SkyrimStateObserver.dll | Hash/PE inspection only; staged is not deployed or loaded. |
| SKYRIM_OBSERVER_DEPLOYED_DLL | Optional deployed DLL | <test profile virtual Data>\SKSE\Plugins\SkyrimStateObserver.dll | Keep blank until a disposable lane is separately authorized; no current command deploys it. |
| SKYRIM_OBSERVER_LOG_DIR | Optional session output directory | .local/observer/<session> | Must be outside live Data and SKSE/Plugins; output remains ignored. |
| DEVBENCH_PORT | Optional integer | <local port> | Reserved only; no active toolkit connector consumes it. |
| LEGACY_SKYRIM_REPO | Absolute read-only source checkout | <existing skyrim checkout> | xedit_bridge.py stages fixed source files under ignored .local and never edits source. |
| SSEEDIT_EXE | Absolute SSEEdit executable | <SSEEdit install>\SSEEdit.exe | Required for helper doctor/prepare; native launch also needs AE preflight. |
| XEDIT_SCRIPTS | Absolute custom script directory | <SSEEdit scripts> | Required xEdit binding; checked by helper doctor. |
| INCLUDE_CREATION_CLUB | 0 or 1 | 0 | Validated by xedit_bridge.py; helper setting only. |
| GHIDRA_HEADLESS_EXE | Absolute headless executable | <Ghidra>\support\analyzeHeadless.bat | Required by existing-project adapter. |
| GHIDRA_PROJECT_REP_PATH | Absolute path to the existing GOG `.rep` data directory | <GOG project name>.rep | Adapter derives the project directory/name and requires this directory plus its adjacent `.gpr`; it never creates a project. |
| GHIDRA_PROJECT_PROGRAM | Existing program name | SkyrimSE.exe | GOG program only. |
| GHIDRA_ANALYSIS_EXE_GOG | Absolute GOG executable | <GOG install>\SkyrimSE.exe | ProductVersion/hash must match the project and Address Library. Never use Steam here. |
| JAVA_HOME | Absolute JDK directory | <installed JDK> | Local Ghidra prerequisite. |
| COMMONLIBSSE_ROOT | Absolute source directory | <CommonLibSSE-NG checkout> | address_library_probe.py reads include/RE/Offsets.h. |
| ADDRESS_LIBRARY_DIR | Absolute GOG Address Library directory | <GOG Data>\SKSE\Plugins | Must match the GOG executable build. |
| VCPKG_ROOT | Absolute source/tool directory | <vcpkg root> | Build metadata; current research probes do not build/install native tools. |
| SKYRIM_CONFIG_DIR | Optional absolute config directory | <local Skyrim config> | Path doctor only. |
| PAPYRUS_LOG_DIR | Optional absolute log directory | <Papyrus logs> | Read-only triage input. |
| SKSE_CRASH_DIR | Optional absolute crash-log directory | <SKSE crash logs> | Read-only triage input. |
| UESP_DUMP_PATH | Optional absolute dump path | <local UESP dump> | Local UESP input only. |
| UESP_INDEX_PATH | Local relative or absolute SQLite path | .local/uesp.sqlite3 | Relative paths resolve from repository root. |
| APOCRYPHA_EXPORT_PATH | Optional absolute private export | <private export> | Untrusted lead input; text stays private. |
| APOCRYPHA_INDEX_PATH | Local relative or absolute SQLite path | .local/apocrypha.sqlite3 | Relative paths resolve from repository root; results stay private. |

config/local.env is ignored by Git. scripts/local_paths.py doctor reports
presence booleans without path values. scripts/local_config.py parses the
registry; tools/ae_target.py validates executable/profile boundaries;
tools/xedit_bridge.py doctor validates xEdit bindings; Ghidra and SKSE probes
validate their own bindings. A configured path does not prove that a native
tool ran.

## Exact tool routes and limits

Use the strict dispatcher after the venv passes. On Windows invoke it with
& .\.venv\Scripts\python.exe scripts/python_env.py run ...; on Linux use
python3 scripts/python_env.py run ....

### xEdit

    python3 scripts/python_env.py run tools/xedit_bridge.py doctor
    python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf
    python3 scripts/python_env.py run tools/xedit_bridge.py prepare
    python3 scripts/python_env.py run tools/ae_preflight.py --scoped-five-master <prepared-session>/plugins.txt
    python3 scripts/python_env.py run tools/ae_preflight.py
    python3 scripts/python_env.py run tools/ae_preflight.py --test-profile

On Windows PowerShell, prepare returns JSON containing a session path. After
the matching AE preflight passes, invoke its generated view-only launch file:

    $prepared = & .\.venv\Scripts\python.exe scripts/python_env.py run tools/xedit_bridge.py prepare | ConvertFrom-Json
    $session = Join-Path $PWD $prepared.session
    & .\.venv\Scripts\python.exe scripts/python_env.py run tools/ae_preflight.py --scoped-five-master (Join-Path $session 'plugins.txt')
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $session 'launch.ps1')

doctor stages the configured authoritative helper/template files into
ignored .local/xedit-authoritative-copy/, checks hashes and bindings, and
captures helper stdout/stderr under ignored .local. The configured source
`LEGACY_SKYRIM_REPO/scripts/skyrim_tool.py` documents `doctor`, `prepare-xedit`,
`records`, and `inventory`. Its `records --signature QUST --plugin Skyrim.esm
--editor-id CreatureDialogueWerewolf` command was reproduced from the source
and returned one record (`CreatureDialogueWerewolf`, local form `000E46`). The
source dispatches `records` to its direct `read_plugin` TES4 reader; the tracked
wrapper exposes the same route as `file-records`. This is a real read-only
bridge record retrieval, but it does not invoke SSEEdit, select a record in the
native record tree, or resolve winning overrides.
prepare writes a scoped five-official-master SSEView session but does not
launch it. --scoped-five-master validates only that generated list. Normal
preflight validates the selected MO2 profile's explicit complete list;
--test-profile uses a separately designated disposable profile. Helper
subprocess timeout is 120 seconds. The wrapper does not supervise or terminate
native SSEView. Close the visible process normally and verify it exited.

A native record export still requires a visible SSEView record selection and
the selection-based export-records.pas Apply Script operation. The exporter
and a real native record export have not been validated in this cold-start
session; the available UI automation has no safe record-tree selection
control. Never label a file-parser result as an xEdit query or winner result.

### Existing GOG Ghidra project

    python3 scripts/python_env.py run tools/address_library_probe.py --symbol MagicItem::CalculateCost
    python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x14C020 --timeout 600

The first command verifies GOG SkyrimSE.exe ProductVersion and a matching
Address Library before returning a GOG-specific RVA. The second queries only
the existing project with -process -noanalysis -readOnly. Neither imports,
creates, overwrites, or reanalyzes a project. The example RVA belongs to GOG
AE 1.6.1179.0; it is not a Steam runtime address. If ProductVersion validation
fails, do not open Ghidra or use a remembered RVA.

`tools/ghidra_probe.py` reads the ignored `config/local.env` through
`scripts/local_config.py`. `GHIDRA_PROJECT_REP_PATH` must name the existing
GOG `.rep` directory; the adapter derives its parent and project name for the
headless invocation and checks the matching `.gpr` first. `.local/ghidra/`
stores private query and binding-verification artifacts, not a second
configuration registry.

### SKSE / Observer

    python3 scripts/python_env.py run tools/skse_probe.py

This is a local file-identity probe. It does not launch Skyrim, load a DLL,
connect to DevBench, wait for a handshake, or retrieve game state. The existing
Observer source documentation describes bounded fixed-size event capture and
requested snapshots into a session directory, with offline timeline/diff
analysis. It says native skill-use, active-effect lifetime, craft transactions,
hit routing, inventory ExtraData, perk/spell lists, and Story Manager state are
not instrumented. A successful build or staged DLL is only a build artifact.
Live observation requires a matching runtime process, a separately designated
disposable profile/save, an authorized deployed DLL, and preserved plugin
handshake plus timestamped snapshot evidence. None of those observations is
established by skse_probe.py.

## Readiness boundary

Run python3 scripts/harness_doctor.py all for the consolidated verdict. Its
read-only checks cover Python/config, research-state validators, local path and
tool status, and safe file-level smoke probes. It never launches xEdit,
Ghidra, Skyrim, or an SKSE mutator. Native records, Ghidra access, and live
observation remain separate gates in docs/HARNESS_READINESS.md. Linux/WSL
validation does not establish Windows xEdit/MO2 or in-game AE behavior.

