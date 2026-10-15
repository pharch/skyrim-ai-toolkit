# Harness readiness — independent cold-start verification

**Verdict: BLOCKED for research dispatch from this session.** This WSL host has Python 3.12.3 but lacks `ensurepip` and pip. A venv bootstrap attempt left an incomplete Linux `.venv`; strict validation found both pinned imports missing, and that incomplete venv was removed so it cannot conflict with the intended Windows environment. Windows `py.exe` is present but execution from WSL fails with `UtilBindVsockAnyPort`; passwordless package installation is unavailable. The strict dispatcher therefore refuses research commands. No bounty investigation was started.

## Readiness gates

| Gate | Status | Evidence-backed result |
|---|---|---|
| Static Python research | BLOCKED_ENVIRONMENT | WSL Python 3.12.3 cannot create a usable venv because `ensurepip` is absent; system and venv pip are unavailable. The strict check reports `FAIL_VENV_MISSING` after cleanup. Windows `py.exe` exists, but WSL execution fails with `UtilBindVsockAnyPort`. No Conda/system fallback was used. See current raw captures under `.local/alignment/final-consistency-20261015/`; earlier bootstrap evidence is EV-0197. |
| GOG Ghidra and Address Library | BLOCKED_EXTERNAL | The ignored `config/local.env` binding exactly matches the user-designated GOG `.rep` path, and the `.rep` directory plus adjacent `.gpr` exist. The adapter reads `GHIDRA_PROJECT_REP_PATH` and its source enforces `-process -noanalysis -readOnly`, with no import or reanalysis path. The fresh documented invocation returned 127 at the strict dispatcher before the probe started; no function, xref, or decompilation was reproduced in this session. EV-0167 is historical integration evidence only; EV-0199 records the binding verification. |
| xEdit helper binding | HISTORICAL_PASS / BLOCKED_CURRENT | EV-0192 and EV-0194 preserve prior helper/prepare results. This fresh session could not dispatch the helper because the strict `.venv` is unavailable; the current doctor reports it blocked. |
| Authoritative bridge QUST query | HISTORICAL_PASS / NOT_REPRODUCED_CURRENT | EV-0193 preserves the prior result: the documented source `records` command and tracked `file-records` alias returned `Skyrim.esm` QUST `CreatureDialogueWerewolf`, local form `000E46`, through the direct TES4 reader. This fresh session could not dispatch it because the strict `.venv` is unavailable. It is not native SSEEdit selection/export or a winning-override query. |
| Native xEdit record query/export | BLOCKED_EXTERNAL | No native record-query/export command is exposed. The existing selection exporter requires a visible record selection and Apply Script; the available UI automation has no safe record-tree selection control. WSL Windows process interop also fails, and no selected MO2 profile/full `plugins.txt` is configured. Smallest safe path: a Windows-hosted visible SSEView session with an explicitly scoped list, a human-visible record selection, then the documented selection-based exporter. No query/export was claimed. |
| Selected MO2 profile and full winner mode | NOT_VERIFIED | No selected profile directory or its explicit complete `plugins.txt` is bound. A five-master list is a separate diagnostic scope and cannot stand in for the active profile. |
| SKSE installed identity | NOT_VERIFIED | The strict dispatcher could not launch the identity probe in this session. Earlier fresh diagnostics stopped before runtime comparison at the WSL ProductVersion bridge (EV-0196). |
| SKSE connection/observation | NOT_VERIFIED | Observer is staged only (584,192 bytes; SHA-256 `108a4b9a73c97b0517a5cf23f11c02778b9ec3a8f88ac7aadc4fe129a7f7b084`). No deployed DLL, running game process, plugin load, handshake, event, snapshot, or DevBench connection was observed. EV-0196. |
| Local tests and validators | PASS_LOCAL, not research-ready | EV-0201 is the fresh consolidated report: 19 checks, 12 PASS, 7 BLOCKED_EXTERNAL, zero FAIL; overall exit 2 / BLOCKED. Unit tests passed 177 with 3 skips. Research-state and Markdown validators pass. Raw report: `.local/alignment/harness-doctor/20261015T092050.055549Z/harness_doctor.json`. These results do not verify the missing `.venv`, Windows CI, native applications, Apocrypha context retrieval, or in-game behavior. |

## Offline source index smoke tests

The consolidated domain doctor runs local, read-only smoke queries. Its UESP probe retrieves `Skyrim:Karstaag` and returns revision `3629292`, then reports three search results; it does not print the page text. This establishes the local page/revision query path, while dump completeness remains unverified. The Apocrypha probe runs a summary-only `level` search and reports three results with private identifiers/text omitted. It does not retrieve message context, so the context-query criterion remains blocked until the strict Python environment is available. These are setup diagnostics and do not start bounty research or bypass the strict dispatcher for research commands. The final captured output is included in EV-0198.

## Observer capability ceiling

The configured source documentation (`observer/docs/README.md`, SHA-256 `7e237e9932e34ccbda4fedced5a734a25ff922a15c8c758d8793f50d4ed56049`, recorded in EV-0196) describes an observational SKSE bridge gated to the exact Steam 1.6.1170 executable/hash. Its documented output is bounded fixed-size events in a session directory plus offline timelines, state diffs, skill budgets, object lineages, and invariant warnings. F10 controls are documented for a marker and requested snapshot/flush/abort; they do not modify game state.

The same README explicitly says the current core does not hook native skill-use, ActiveEffect lifetime, craft transactions, hit routing, inventory ExtraData, perk/spell lists, or Story Manager state. The extension plan (`observer/docs/bridge-extension-plan.md`, SHA-256 `cc29937a2ff85224596ddd5d5e2208f86f60e1ba34f77ca338770961c165ff26`) is a proposed implementation/test plan, not evidence those hooks exist. In this cold-start, the DLL is staged only: no deployment, plugin load, running game, handshake, log session, event, or snapshot occurred.

## Reproduced commands

The following are historical setup diagnostics from the previous setup pass.
Their direct system-Python invocations are not active routes and do not
authorize bypassing the strict dispatcher. New runs must use the implemented
commands in `docs/LOCAL_RUNTIME_CONTRACT.md`:

- `python3 scripts/python_env.py run tools/xedit_bridge.py doctor` — helper configuration/staging only. Historical evidence EV-0192 records the direct diagnostic invocation and output.
- `python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf` — direct TES4 reader returned one QUST record; EV-0193 preserves the historical bridge result. It is not a native xEdit query.
- `python3 scripts/python_env.py run tools/xedit_bridge.py prepare` — scoped five-master session preparation only; EV-0194 preserves the historical result.
- `python3 scripts/python_env.py run tools/xedit_bridge.py --help` — the wrapper exposes no native record-query/export operation.
- Fresh Ghidra, Address Library, SKSE identity, and scoped AE preflight attempts — earlier ProductVersion/Windows-process interop stopped native access (EV-0195–EV-0196). After the explicit project path binding was added, the documented Ghidra dispatcher stopped before probe launch because `.venv` was missing (EV-0199–EV-0200). No Ghidra project was opened.
- Fresh clean-venv, ensurepip, pip, strict dispatcher, and save-reader checks — no packages installed. EV-0197.

The authoritative helper source/help/query hashes and detailed redacted metadata are in ignored `.local/alignment/cold-start-final-20261015/`. The explicit Ghidra binding check is in ignored `.local/ghidra/binding-verification.json`; it records the resolved private path and states that it is verification metadata, not configuration. The consolidated doctor writes its JSON and full stdout/stderr under ignored `.local/alignment/harness-doctor/`.

## Exact next session

On the intended Windows host, create the repository environment with Python 3.12, install `requirements-dev.txt`, and run the strict check and doctor exactly as listed in `docs/LOCAL_RUNTIME_CONTRACT.md`. This WSL session cannot execute Windows processes or install the missing `python3.12-venv` package without administrator credentials. Do not run research entrypoints through system Python.

After the Python gate passes, first run `python3 scripts/python_env.py run scripts/research_state.py validate`, then follow `NEXT_SESSION_HANDOFF.md` and `docs/RESEARCH_START_PROMPT.md`. The user-provided task input is `bounties/BOUNTY-0001-LEVEL1-P0.md`; it has not been investigated in this setup session.

Linux/WSL checks do not establish Windows MO2/xEdit behavior or in-game Skyrim AE behavior. A staged Observer or file-parser result is not native observation or a gameplay finding.
