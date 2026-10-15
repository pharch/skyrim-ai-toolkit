# Local runtime contract

This file is the active setup and invocation contract for this checkout. The
only machine-specific binding file is ignored config/local.env; raw captures
and derived helper files stay below ignored .local/. Never copy absolute
machine paths, game/plugin bytes, saves, private exports, binaries, or Ghidra
project data into tracked files.

## Python 3.12 environment

`requirements.txt` is the one complete, pinned dependency specification.
`requirements-dev.txt` only includes it for compatibility. Persistent
host-specific environments live below ignored `.local/python-envs/`:

- native Windows: `.local/python-envs/windows`
- WSL: `.local/python-envs/wsl`
- other Linux: `.local/python-envs/linux`

Use native Windows for game-connected research. A WSL session has its own
Python environment for offline analysis; it never shares or rewrites the
Windows environment. Bootstrap reuses a healthy environment, repairs missing
or changed pinned packages in place, and preserves an unusable environment in
an ignored quarantine directory before rebuilding it.

Bootstrap from the host's installed Python 3.12 launcher. In Windows
PowerShell:

    py -3.12 scripts/bootstrap_python.py

In Linux or WSL:

    python3 scripts/bootstrap_python.py

The command detects the execution host, locates Python 3.12, creates the
persistent environment, installs every pin from `requirements.txt`, verifies
pip/imports/versions, and prints JSON containing the working environment path.
It can run without a venv. If the host lacks `venv` or `ensurepip`, it attempts
the host package-manager repair and a user-local verified pip-wheel bootstrap
before reporting a blocker. A failed strict preflight therefore starts
bootstrap repair; do not immediately hand off or switch to Conda/system
packages.

On a fresh checkout, initialize the ignored local configuration before strict
validation if `config/local.env` is absent. The setup-only command copies the
blank schema and preserves any existing machine values:

    python3 scripts/setup_research.py init
    # Windows PowerShell: py -3.12 scripts/setup_research.py init

Bind the paths needed on this host in `config/local.env`. Python bootstrap and
this config initializer may use the host launcher; research tools always use
the strict dispatcher.

After bootstrap, use the strict dispatcher for research. The Windows launcher
is `py -3.12`; Linux/WSL uses `python3`:

    python3 scripts/python_env.py check --strict
    python3 scripts/python_env.py run scripts/research_state.py validate
    python3 scripts/python_env.py run scripts/harness_doctor.py all

PowerShell forms:

    py -3.12 scripts/python_env.py check --strict
    py -3.12 scripts/python_env.py run scripts/research_state.py validate
    py -3.12 scripts/python_env.py run scripts/harness_doctor.py all

The dispatcher starts children only from the validated environment for the
active host. Its system launcher runs the dispatcher itself and is not a
research fallback. Do not call research scripts directly or activate another
environment. `check --strict` verifies Python 3.12, pip, every pinned
requirement and required import, and the syntax of `config/local.env`. `run`
returns 127 without starting a child when a strict prerequisite fails.

To add a dependency that an active research or validation script genuinely
needs, add an exact `name==version` pin to `requirements.txt`, then rerun
bootstrap and `check --strict`. Do not install packages by hand into a host
Python. `requirements.txt` currently declares `lz4==4.3.3` for
`scripts/read-save.py`, `PyYAML==6.0.1` for `scripts/validate_overlay.py`,
`pip==24.0` for environment repair, and `pytest==8.0.0` for test tooling with
its `iniconfig`, `packaging`, and `pluggy` dependencies pinned too.

For an isolated bootstrap acceptance test, `bootstrap_python.py --env-dir`
accepts only a directory below `.local/`. The dispatcher test override
`SKYRIM_PYTHON_ENV_DIR` is also restricted below `.local/`; ordinary research
uses the automatic host path above. Tests must never remove or recreate the
active environment. To reproduce cold creation, select a fresh nonexistent
path below `.local/`, run bootstrap twice, and confirm `action=created` then
`action=reused`. To exercise repair, remove one pinned package only from that
disposable environment, rerun bootstrap, and confirm `action=repaired` plus a
passing strict check through `SKYRIM_PYTHON_ENV_DIR`. Never uninstall from
`.local/python-envs/<host>`.

After bootstrap, strict Python, research-state validation, and locally
available static checks pass, stop setup work and continue the selected
frontier item. Missing profile/game/live-tool bindings remain separate
capability gates; they do not keep the agent in a setup loop. A Linux/WSL
Python-only pass does not establish Windows xEdit/MO2 or live-game behavior;
an actual WSL-to-Windows SSEView run with native output and loaded-file
inventory establishes xEdit capability only for the tested scope.

`scripts/research_state.py validate` checks durable transaction, frontier,
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
| SKYRIM_DATA | Absolute Data directory | <GAME_ROOT>\Data | Source for direct parsing and the official masters; native xEdit makes an ignored `.local` view that omits CC and user plugins. |
| MO2_PROFILE_DIR | Optional absolute selected MO2 profile | <MO2 profiles>\<selected profile> | Needed only when the researched target order is managed by this MO2 profile. |
| PLUGINS_TXT | Optional absolute selected plugins.txt | <selected profile>\plugins.txt | For MO2 targets, must belong to MO2_PROFILE_DIR and contain the full active list. Not needed for official-master xEdit inspection. |
| SKYRIM_TEST_PROFILE_DIR | Optional absolute disposable profile | <MO2 profiles>\<test profile> | Used only by ae_preflight.py --test-profile. |
| SKYRIM_TEST_PLUGINS_TXT | Optional absolute test plugins.txt | <test profile>\plugins.txt | Used only with SKYRIM_TEST_PROFILE_DIR and must contain the full order. |
| RESEARCH_TEST_SAVE | Absolute disposable save | <test profile save> | Never point at a user's baseline. |
| SKSE_LOADER | Absolute SKSE loader executable | <GAME_ROOT>\skse64_loader.exe | skse_probe.py checks installed file identity; does not launch it. |
| SKYRIM_OBSERVER_STAGED_DLL | Local staged DLL | .local/readiness/<build>/stage/SKSE/Plugins/SkyrimStateObserver.dll | Hash/PE inspection only; staged is not deployed or loaded. |
| SKYRIM_OBSERVER_DEPLOYED_DLL | Optional deployed DLL | <test profile virtual Data>\SKSE\Plugins\SkyrimStateObserver.dll | Keep blank until a disposable lane is separately authorized; no current command deploys it. |
| SKYRIM_OBSERVER_LOG_DIR | Optional session output directory | .local/observer/<session> | Must be outside live Data and SKSE/Plugins; output remains ignored. |
| DEVBENCH_PORT | Optional integer | <local port> | Reserved only; no active toolkit connector consumes it. |
| LEGACY_SKYRIM_REPO | Absolute read-only source checkout | <existing skyrim checkout> | xedit_bridge.py stages fixed source files under ignored .local and never edits source. |
| SSEEDIT_EXE | Absolute SSEEdit executable | <SSEEdit install>\SSEEdit.exe | Required for helper doctor/prepare; native launch also needs AE preflight. |
| XEDIT_SCRIPTS | Optional absolute global script directory | <SSEEdit scripts> | Legacy compatibility path only; the native bridge installs the query script in its per-session `-S:` directory. |
| INCLUDE_CREATION_CLUB | 0 or 1 | 0 | Official-master `prepare` and `native-query` require 0; CC records are outside the validated route. |
| GHIDRA_HEADLESS_EXE | Absolute headless executable | <Ghidra>\support\analyzeHeadless.bat | Required by existing-project adapter. |
| GHIDRA_PROJECT_REP_PATH | Absolute path to the existing GOG `.rep` data directory | <GOG project name>.rep | Adapter derives the project directory/name and requires this directory plus its adjacent `.gpr`; it never creates a project. |
| GHIDRA_PROJECT_PROGRAM | Existing program name | SkyrimSE.exe | GOG program only. |
| GHIDRA_ANALYSIS_EXE_GOG | Absolute GOG executable | <GOG install>\SkyrimSE.exe | ProductVersion/hash must match the project and Address Library. Never use Steam here. |
| JAVA_HOME | Absolute JDK directory | <installed JDK> | Local Ghidra prerequisite. |
| GHIDRA_JAVA_HOME_WSL | Optional WSL Java home | .local/ghidra-runtime/root/usr/lib/jvm/java-21-openjdk-amd64 | Used only with the paired Linux `analyzeHeadless` launcher; Ghidra requires Java 21+. Native Windows continues to use its installed Java runtime. |
| GHIDRA_USER_HOME_WSL | WSL Ghidra preference/JDK state | .local/ghidra-runtime/home | Must resolve below ignored `.local/`; keeps LaunchSupport preferences and selected JDK local to this checkout. |
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

Use the strict dispatcher after bootstrap. On Windows invoke it with
`py -3.12 scripts/python_env.py run ...`; on Linux/WSL use
`python3 scripts/python_env.py run ...`.

### xEdit

    python3 scripts/python_env.py run tools/xedit_bridge.py doctor
    python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf
    python3 scripts/python_env.py run tools/xedit_bridge.py prepare
    python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm --editor-id dunDA14MorvunskarQST
    python3 scripts/python_env.py run tools/ae_preflight.py --scoped-five-master <prepared-session>/plugins.txt
    python3 scripts/python_env.py run tools/ae_preflight.py --test-profile

On Windows PowerShell, invoke the same native query with the strict Windows
launcher:

    py -3.12 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm --editor-id dunDA14MorvunskarQST

`doctor` stages the fixed helper files from the configured, read-only
`LEGACY_SKYRIM_REPO` into ignored `.local/xedit-authoritative-copy/`, verifies
their SHA-256 hashes, checks local bindings, and validates the latest native
receipt without launching xEdit. `prepare` creates but does not launch a
view-only session. Both use the official-master-only Data view under
`.local/xedit-data/official-ae-v1`; it contains hash-verified read-only copies
of only the five official masters and their matching vanilla string files from
`SKYRIM_DATA`. This is needed
because a direct launch against the configured game Data folder auto-loaded
Creation Club and user plugins even though the original helper generated a
five-entry `plugins.txt`. The overlay omits `Skyrim.ccc` and all non-master
plugins. The source game Data files remain the inputs and are not written.

`native-query` is the canonical Codex route for native xEdit. It verifies the
executable ProductVersion against its generated five-master list without
requiring `MO2_PROFILE_DIR`, stages a per-session Pascal script through the
original helper's `-S:` option, launches the configured executable using its
original `-SSE -view -DontCache -D: -P: -I: -R: -O: -S:` arguments, and uses
the original UIAutomation status and Ctrl+Alt+F9 helpers to dispatch the
read-only Apply Script. The field walker and TSV columns come from the source
`scripts/xedit/export-records.pas`; its global `Initialize` execution pattern
is corroborated by `investigation-export.pas`. The query writes the actual
loaded-file inventory, an explicit result status, decoded field values,
`LinksTo` values, and the winning plugin within this five-master scope. Raw
TSV/UI captures and structured JSON remain in ignored `.local/` paths. The
wrapper requests a graceful close only for the SSEView process it launched;
the closing window may outlive the initial two-second status sample. The
acceptance run's specific process was absent in a later PID check.

The native route was cold-start reproduced for `Skyrim.esm` QUST
`dunDA14MorvunskarQST` (form `000427A0`): SSEView 4.1.5f reported
`Background Loader: finished`, loaded exactly the five official masters plus
the executable pseudo-file, and exported 149 field rows. The output includes
stage indices 20 and 100 and the `Shut Down Stage=1` field under stage 100.
See EV-0207 and `tests/fixtures/xedit/native_quest_smoke.json`. This validates
native record fields and a stage-field relationship. It does not establish a
profile-specific override: `WinningOverride` is reported only within the five
official masters.

Keep the three routes distinct:

1. `file-records` reads raw plugin bytes through the original Python `read_plugin`
   TES4 parser. It is not native xEdit and does not resolve a winning override.
2. `native-query` loads the exact official-master view in SSEView and exports
   native xEdit field values. No MO2 profile is needed for this vanilla scope.
3. Profile-specific winner or negative claims require the complete order from
   the actual target. If that target is MO2-managed, configure its selected
   profile's explicit `plugins.txt` and run the regular `ae_preflight.py`.
   Do not infer an effective winner from the five-master view.

The wrapper uses Windows PowerShell/UIAutomation and a visible SSEView window;
it requires a native Windows session or WSL2 Windows interop. A WSL Python
check alone does not prove that the Windows GUI bridge is available.

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
configuration registry. On WSL, when the Windows Ghidra installation also
contains its paired Linux `support/analyzeHeadless`, the adapter invokes that
launcher and uses `GHIDRA_JAVA_HOME_WSL` (or Java 21+ on PATH). If the
configured project is on a read-only WSL mount, it copies the existing project
files into ignored `.local/ghidra/project-cache/`; a source manifest pins that
working copy to `GHIDRA_PROJECT_REP_PATH` and its file metadata. Ghidra's
preference/JDK state stays under `GHIDRA_USER_HOME_WSL`. The source project is
not modified, imported, or reanalyzed. Both platform routes retain
`-process -noanalysis -readOnly`.

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

Run `python3 scripts/python_env.py run scripts/harness_doctor.py all` for the
consolidated verdict (Windows PowerShell: `py -3.12
scripts/python_env.py run scripts/harness_doctor.py all`). Its read-only checks
cover Python/config, research-state validators, local path and tool status,
and safe file-level smoke probes. It never launches xEdit, Ghidra, Skyrim, or an
SKSE mutator. Native records, Ghidra access, and live observation remain
separate gates in docs/HARNESS_READINESS.md. Linux/WSL Python-only validation
does not establish Windows xEdit/MO2 or in-game AE behavior. A
WSL-to-Windows native export with loaded-file inventory is evidence for its
exact xEdit scope; it does not verify the active profile or in-game behavior.

