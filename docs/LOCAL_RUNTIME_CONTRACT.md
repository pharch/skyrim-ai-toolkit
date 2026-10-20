# Local runtime contract

This is the single source of truth for Python, private local bindings and exact tool invocations. `config/local.env` is ignored and is the only machine-specific registry; `config/local.env.example` is its portable schema. Keep absolute paths, private indexes, raw captures, game files, saves, binaries and Ghidra project data out of tracked files.

These commands describe internal Codex operations. The user-facing research
interface is the single natural-language prompt in
[`RESEARCH_START_PROMPT.md`](RESEARCH_START_PROMPT.md); do not ask the user to
run `research_state.py` or `research_transactions.py`, choose a transaction ID,
or manually resume the frontier. If a check fails, repair or recover it here
and continue once the required source route is ready.

## Python 3.12

`requirements.txt` is the one complete, pinned dependency specification. Persistent host-specific environments live under ignored `.local/python-envs/`: `windows`, `wsl`, or `linux`. Native Windows is preferred for game-connected work; WSL/Linux uses its own environment.

Bootstrap works without an existing venv and reuses a healthy environment. It creates an absent environment, repairs missing venv/pip prerequisites where permitted, installs or repairs every pin, verifies versions/imports and prints the environment path. A failed strict check triggers bootstrap repair before any external blocker is declared.

```powershell
py -3.12 scripts/bootstrap_python.py
py -3.12 scripts/python_env.py check --strict
py -3.12 scripts/python_env.py run scripts/research_state.py validate
py -3.12 scripts/python_env.py run scripts/harness_doctor.py static
```

```sh
python3 scripts/bootstrap_python.py
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
python3 scripts/python_env.py run scripts/harness_doctor.py static
```

Research tools run only through `scripts/python_env.py run`; children launch from the validated host venv. The host launcher starts bootstrap/dispatcher only and is never a research dependency fallback. Do not use Conda, system packages or ambient site-packages for normal research. To add a genuinely needed package, add one exact `name==version` pin to `requirements.txt`, then bootstrap and run `check --strict`. Tests use the same pins. `setup_research.py init` is only for a fresh checkout whose ignored `config/local.env` does not exist; it never overwrites an existing file.

The bootstrap's `--env-dir` and dispatcher override `SKYRIM_PYTHON_ENV_DIR` are limited to `.local/`. For a cold bootstrap/reuse/repair regression, use a new disposable path under `.local/`; never remove or uninstall from `.local/python-envs/<host>`.

`scripts/research_state.py validate` checks transaction, frontier, evidence, claim and recovery structure. It does not validate local binaries, Ghidra/xEdit execution, the selected plugin order, privacy, SKSE deployment or the truth of a research claim.

## Local configuration

`config/local.env` uses one `KEY=VALUE` assignment per line. Duplicate keys, malformed quotes and conflicting aliases are rejected; values are not shell-expanded and ambient environment variables are not fallbacks. Blank example values mean unbound. Path examples are placeholders.

| Key | Use / status | Expected value and validation |
|---|---|---|
| `SKYRIM_EDITION` | Required for AE target checks | Literal `AE`; executable ProductVersion is still read from file. |
| `GAME_ROOT`, `SKYRIM_EXE_PATH`, `SKYRIM_DATA` | Required for target/xEdit | Game root, `SkyrimSE.exe`, and Data directory. `SKYRIM_EXE_PATH` may derive from root. |
| `SSEEDIT_EXE` | Required for native xEdit | Existing SSEEdit/SSEView executable; identity and launch are checked by the bridge. |
| `LEGACY_SKYRIM_REPO` | Required for recovered xEdit helpers and source provenance | Read-only original checkout. Helpers are copied by the wrapper into ignored `.local/` and hash-checked. |
| `XEDIT_SCRIPTS` | Optional compatibility path | Existing Edit Scripts directory; canonical query installs its script in a per-session `-S:` directory. |
| `INCLUDE_CREATION_CLUB` | Required xEdit scope flag | Set `0` for the tested official-five-master route. |
| `MO2_PROFILE_DIR`, `PLUGINS_TXT` | Optional; required only for a profile-managed target order | Exact selected MO2 profile and its full `plugins.txt`; never infer either. |
| `SKYRIM_TEST_PROFILE_DIR`, `SKYRIM_TEST_PLUGINS_TXT`, `RESEARCH_TEST_SAVE` | Optional live-test prerequisites | Explicit disposable profile, complete list and disposable save; never use a baseline. |
| `GHIDRA_PROJECT_REP_PATH` | Required for GOG Ghidra | Existing GOG project `.rep` directory with adjacent `.gpr`; the adapter queries it read-only. |
| `GHIDRA_PROJECT_CACHE_WSL` | Required only when WSL cannot write/lock the configured project mount | Absolute WSL-native cache path outside `/mnt` and the checkout. It holds a metadata-verified copy of the configured existing project; it never replaces or reanalyzes the source project. |
| `GHIDRA_PROJECT_PROGRAM` | Required for Ghidra | Existing program name, currently `SkyrimSE.exe`. |
| `GHIDRA_HEADLESS_EXE`, `GHIDRA_ANALYSIS_EXE_GOG` | Required for Ghidra verification | Ghidra headless launcher and the exact GOG AE analysis executable. |
| `JAVA_HOME` | Required native Ghidra prerequisite | Existing JDK. WSL may use the paired `GHIDRA_JAVA_HOME_WSL`. |
| `GHIDRA_USER_HOME_WSL` | Optional WSL Ghidra state | Private preference directory below ignored `.local/`. |
| `COMMONLIBSSE_ROOT`, `ADDRESS_LIBRARY_DIR` | Optional native symbol route | CommonLib source and Address Library matching the GOG analysis binary; validated by `address_library_probe.py`. |
| `VCPKG_ROOT` | Optional build metadata | Existing tool directory; current research probes do not build or install native tools. |
| `SKSE_LOADER` | Optional identity probe | Existing SKSE loader; `skse_probe.py` checks files only. |
| `SKYRIM_OBSERVER_STAGED_DLL`, `SKYRIM_OBSERVER_DEPLOYED_DLL` | Optional; deployed path only for approved live work | Staged/deployed DLL identities are distinct from a loaded DLL or connection. |
| `SKYRIM_OBSERVER_LOG_DIR`, `DEVBENCH_PORT` | Optional live integration | Session output directory outside game Data; port is reserved and no current toolkit connector consumes it. |
| `SKYRIM_CONFIG_DIR`, `PAPYRUS_LOG_DIR`, `SKSE_CRASH_DIR` | Optional read-only triage | Existing configuration/log folders; no writes. |
| `UESP_DUMP_PATH`, `UESP_INDEX_PATH` | Optional local UESP source/index | Local input and SQLite path; dump completeness/license are not presumed. |
| `APOCRYPHA_EXPORT_PATH`, `APOCRYPHA_INDEX_PATH` | Optional private untrusted leads | Private export and SQLite path; message text stays outside Git. |

Use `python3 scripts/python_env.py run scripts/local_paths.py doctor` (Windows: `py -3.12 ...`) to report bound-path presence without values. `tools/ae_preflight.py` reads executable identity and, when requested, the exact complete target order. A configured path or a doctor status alone is not a successful tool query.

## xEdit / SSEView

Canonical commands (Windows uses the same arguments after `py -3.12 scripts/python_env.py run`):

```sh
python3 scripts/python_env.py run tools/xedit_bridge.py doctor
python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf
python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm --editor-id dunDA14MorvunskarQST
python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature INFO --plugin Skyrim.esm --form-id 00095585
```

`file-records` parses a single TES4 plugin file and returns raw record fields; it does not run xEdit or resolve a winner. `native-query` launches configured SSEView using the original helper and Pascal field exporter. Select exactly one record with `--editor-id` or an eight-digit source-plugin-local `--form-id`; the FormID route supports nested records such as INFO records that have no EditorID. It makes a hash-verified read-only copy of the five official masters and matching vanilla strings under ignored `.local/`, loads the exact official-master scope, exports native fields and loaded-file inventory, and needs no MO2 profile. It uses a visible SSEView window and Windows PowerShell/UI Automation (native Windows or tested WSL-to-Windows interop). EV-0207 records the fresh native QUST export; the regression fixture is `tests/fixtures/xedit/native_quest_smoke.json`.

The native route is a real five-official-master session, not a profile winner. Profile-specific winner and negative claims require the complete order from the exact target; if MO2-managed, bind the selected profile's own `plugins.txt` and run `tools/ae_preflight.py`. Never substitute the five-master list or global AppData order.

## Existing GOG Ghidra project

```sh
python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'MagicItem::CalculateCost'
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x14C020 --timeout 600
```

The first command verifies GOG AE `SkyrimSE.exe` identity and matching Address Library. The second uses `GHIDRA_PROJECT_REP_PATH` and the existing project with `-process -noanalysis -readOnly`; it never creates, imports or reanalyzes a project. The verified GOG 1.6.1179.0 RVA is not a Steam 1.6.1170.0 address. When the source is on a read-only Windows mount, WSL uses the configured paired Linux launcher and copies the existing project into `GHIDRA_PROJECT_CACHE_WSL`, which must be on the WSL-native filesystem so Ghidra can acquire its project lock. Raw query output remains below ignored `.local/`.

For a bounded call-graph census without decompiling each callee, use `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xRVA --list-call-edges --timeout 600`. It reports every direct call edge and unresolved indirect call site in the selected function. The existing `--follow-direct-calls` option still decompiles at most eight direct callees.

For a bounded initialized function-pointer table, use `python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0xRVA --pointer-count N --timeout 600`. The query lists references to each table entry and reports each raw pointer value and any containing analyzed function; it remains attached to the identity-checked existing GOG project and runs read-only with auto-analysis disabled. Use the exact table address and bounds observed in a captured function; a resolved pointer alone does not establish its runtime type or behavior. For a target address with no analyzed function boundary, `--address-rva 0xRVA` reports references plus a bounded instruction context without creating or changing a function.

For a whole-program analyzed-memory-operand scan by displacement, use `python3 scripts/python_env.py run tools/ghidra_probe.py --search-displacement 0x274 --timeout 600`. This reports matching operands, stack-relative references, containing functions, and bounded candidate writer/callee analysis from the existing GOG program. Check the metadata completion markers and output caps; a displacement match alone does not identify a field or establish semantics. The scan uses `-process -noanalysis -readOnly` and does not create, import, or reanalyze a program.

## SKSE, sources, and readiness

```sh
python3 scripts/python_env.py run tools/skse_probe.py
python3 scripts/python_env.py run -m tools.uesp search --db .local/uesp.sqlite3 --limit 10 'quest terms'
python3 scripts/python_env.py run -m tools.apocrypha search --db .local/apocrypha.sqlite3 --summary-only 'mechanic terms'
```

`skse_probe.py` reports installed file identity only. A staged DLL/build does not prove deployment, game process, plugin load, handshake, event capture or snapshot; live capability remains unverified until timestamped read-only telemetry from the exact runtime is preserved. Live SKSE is not required for static work. UESP is secondary grounding; Apocrypha content is private and untrusted. Preserve page revision/URL or private message provenance without copying private text.

Run `python3 scripts/python_env.py run scripts/harness_doctor.py static` for static Python, Ghidra, source and research-state gates; `records` reports xEdit separately; `live` reports live-only gates; `all` reports every mode independently and cannot turn an unverified optional gate into a pass. The doctor never launches a native GUI, game or mutator. Current scope and evidence are in [`HARNESS_READINESS.md`](HARNESS_READINESS.md). A Linux/WSL pass does not establish Windows UI or in-game behavior.
