# Harness readiness — independent cold-start verification

**Verdict: BLOCKED_EXTERNAL for research dispatch on this host.** The checkout's local validators and system-Python unit tests pass, but the documented research dispatcher requires a Python 3.12 `.venv` that this WSL installation cannot create because `ensurepip` and `pip` are missing. Native Ghidra/xEdit access and live SKSE observation were not reproduced. No bounty investigation was started.

## Readiness gates

| Gate | Status | Evidence-backed result |
|---|---|---|
| Static Python research | BLOCKED_ENVIRONMENT | Python 3.12.3 exists, but clean venv creation fails at missing `ensurepip`; the host diagnostic names `python3.12-venv`. No `pip`, `pip3`, `uv`, Conda, or Windows `py` bootstrap is installed. Strict dispatcher reports `FAIL_VENV_MISSING`; save-reader help fails because `lz4` is unavailable. EV-0197. |
| GOG Ghidra and Address Library | BLOCKED_EXTERNAL | EV-0199 verifies that ignored `config/local.env` binds the exact user-designated existing GOG `.rep` directory and that its adjacent `.gpr` exists; `tools/ghidra_probe.py` reads this file and refuses to create a project. The documented invocation was blocked by `FAIL_VENV_MISSING` before the probe launched. Earlier fresh ProductVersion diagnostics stopped at WSL Windows-process interop (EV-0195); no Ghidra query was performed. |
| xEdit helper binding | PASS, helper only | The documented bridge doctor and scoped preparation ran. `--help` exposes `doctor`, `prepare`, and `file-records`; it explicitly says the latter two do not perform a native xEdit export. EV-0192, EV-0194. |
| Authoritative bridge QUST query | PASS, direct TES4 reader | The documented source `records` command and tracked `file-records` alias each returned `Skyrim.esm` QUST `CreatureDialogueWerewolf`, local form `000E46`. This is a genuine bridge record retrieval through the direct file parser, not native SSEEdit selection/export and not a winning-override query. EV-0193. |
| Native xEdit record query/export | BLOCKED_EXTERNAL | No native record-query/export command is exposed. The existing selection exporter requires a visible record selection and Apply Script; the available UI automation has no safe record-tree selection control. WSL Windows process interop also fails, and no selected MO2 profile/full `plugins.txt` is configured. Smallest safe path: a Windows-hosted visible SSEView session with an explicitly scoped list, a human-visible record selection, then the documented selection-based exporter. No query/export was claimed. |
| Full MO2 winner mode | BLOCKED_EXTERNAL | No selected profile directory and its explicit complete `plugins.txt` are bound. A five-master list is a separate diagnostic scope and cannot stand in for the active profile. |
| SKSE installed identity | BLOCKED_EXTERNAL | The fresh identity probe stopped before runtime comparison at the ProductVersion bridge. EV-0196. |
| SKSE connection/observation | NOT_VERIFIED | Observer is staged only (584,192 bytes; SHA-256 `108a4b9a73c97b0517a5cf23f11c02778b9ec3a8f88ac7aadc4fe129a7f7b084`). No deployed DLL, running game process, plugin load, handshake, event, snapshot, or DevBench connection was observed. EV-0196. |
| Local tests and validators | PASS_LOCAL, not research-ready | The latest report is EV-0200: 19 checks, 12 PASS, 7 BLOCKED_EXTERNAL, zero FAIL; overall exit 2 / BLOCKED. The system-Python suite passed 177 tests with 3 dependency-gated skips. Earlier domain smoke checks returned UESP revision 3629292 and three private summary-only Apocrypha search results (EV-0198). This does not verify the missing `.venv`, Windows CI, native applications, Apocrypha context retrieval, or in-game behavior. Latest raw JSON and command captures are under ignored `.local/alignment/harness-doctor/20261015T084558.620330Z/. |

## Offline source index smoke tests

The consolidated domain doctor runs local, read-only smoke queries. Its UESP probe retrieves `Skyrim:Karstaag` and returns revision `3629292`, then reports three search results; it does not print the page text. This establishes the local page/revision query path, while dump completeness remains unverified. The Apocrypha probe runs a summary-only `level` search and reports three results with private identifiers/text omitted. It does not retrieve message context, so the context-query criterion remains blocked until the strict Python environment is available. These are setup diagnostics and do not start bounty research or bypass the strict dispatcher for research commands. The final captured output is included in EV-0198.

## Observer capability ceiling

The configured source documentation (`observer/docs/README.md`, SHA-256 `7e237e9932e34ccbda4fedced5a734a25ff922a15c8c758d8793f50d4ed56049`, recorded in EV-0196) describes an observational SKSE bridge gated to the exact Steam 1.6.1170 executable/hash. Its documented output is bounded fixed-size events in a session directory plus offline timelines, state diffs, skill budgets, object lineages, and invariant warnings. F10 controls are documented for a marker and requested snapshot/flush/abort; they do not modify game state.

The same README explicitly says the current core does not hook native skill-use, ActiveEffect lifetime, craft transactions, hit routing, inventory ExtraData, perk/spell lists, or Story Manager state. The extension plan (`observer/docs/bridge-extension-plan.md`, SHA-256 `cc29937a2ff85224596ddd5d5e2208f86f60e1ba34f77ca338770961c165ff26`) is a proposed implementation/test plan, not evidence those hooks exist. In this cold-start, the DLL is staged only: no deployment, plugin load, running game, handshake, log session, event, or snapshot occurred.

## Reproduced commands

The three xEdit commands below were run with system Python only as diagnostic reproductions because the strict dispatcher refuses child execution without `.venv`:

- `python3 tools/xedit_bridge.py doctor` — exit 0; helper configuration/staging only. EV-0192.
- `python3 <LEGACY_SKYRIM_REPO>/scripts/skyrim_tool.py records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf` — exit 0, one QUST record; the configured source path stays private. The tracked `tools/xedit_bridge.py file-records ...` alias returned the same result. EV-0193.
- `python3 tools/xedit_bridge.py prepare` — exit 0; scoped five-master session prepared, not launched. EV-0194.
- `python3 tools/xedit_bridge.py --help` — captured output lists no native record-query/export operation.
- Fresh Ghidra, Address Library, SKSE identity, and scoped AE preflight attempts — earlier ProductVersion/Windows-process interop stopped native access (EV-0195–EV-0196). After the explicit project path binding was added, the documented Ghidra dispatcher stopped before probe launch because `.venv` was missing (EV-0199–EV-0200). No Ghidra project was opened.
- Fresh clean-venv, ensurepip, pip, strict dispatcher, and save-reader checks — no packages installed. EV-0197.

The authoritative helper source/help/query hashes and detailed redacted metadata are in ignored `.local/alignment/cold-start-final-20261015/`. The explicit Ghidra binding check is in ignored `.local/ghidra/binding-verification.json`; it records the resolved private path and states that it is verification metadata, not configuration. The consolidated doctor writes its JSON and full stdout/stderr under ignored `.local/alignment/harness-doctor/`.

## Exact next session

On Windows, create the repository environment with Python 3.12, install `requirements-dev.txt`, and run the strict check and doctor exactly as listed in `docs/LOCAL_RUNTIME_CONTRACT.md`. This WSL host cannot complete that bootstrap until its Python distribution includes `venv`/`ensurepip` and pip. Do not run research entrypoints through system Python.

After the Python gate passes, first run `python3 scripts/python_env.py run scripts/research_state.py validate`, then follow `NEXT_SESSION_HANDOFF.md` and `docs/RESEARCH_START_PROMPT.md`. The user-provided task input is `bounties/BOUNTY-0001-LEVEL1-P0.md`; it has not been investigated in this setup session.

Linux/WSL checks do not establish Windows MO2/xEdit behavior or in-game Skyrim AE behavior. A staged Observer or file-parser result is not native observation or a gameplay finding.
