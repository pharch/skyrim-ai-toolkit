# Harness readiness — cold-start setup closeout

**Current verdict: BLOCKED for starting the first research session from this
WSL shell.** The repository’s strict Python 3.12 environment is unavailable,
so the documented GOG and xEdit dispatchers refused to launch. Research-state
structure passed inside the consolidated doctor. No bounty investigation,
Ghidra query, xEdit record retrieval, or game launch occurred in this pass.
See EV-0202 and its ignored raw artifacts.

## Readiness gates

| Gate | Status | Evidence-backed result |
|---|---|---|
| Python 3.12 repository `.venv` | BLOCKED_ENVIRONMENT | Actual host: Ubuntu 24.04 under WSL2, CPython 3.12.3. `ensurepip` and pip are absent; `python3 -m venv .venv` fails. The needed `python3.12-venv` apt package is not installed, and sudo requires a password. Windows `py.exe`/PowerShell interop fails with `UtilBindVsockAnyPort:307`. The incomplete Linux `.venv` was removed. Strict check: `FAIL_VENV_MISSING`. No Conda or system-Python research fallback was used. |
| Research-state structure | PASS via doctor | The consolidated doctor’s `research_state_validation` check exited 0 and validated frontier/evidence/recovery structure. The separately documented dispatcher command was attempted but failed closed before the validator because the repository `.venv` is missing. |
| GOG project binding | PASS | Ignored `config/local.env` contains the specified `GHIDRA_PROJECT_REP_PATH`. Its mapped WSL `.rep` directory and adjacent `.gpr` exist. This verifies the binding only. |
| GOG function/xref/decompilation query | BLOCKED_ENVIRONMENT | The Address Library and Ghidra commands were attempted through `scripts/python_env.py run`; both returned 127 before their child started. No function, xref, or decompilation query was reproduced. The adapter source uses the configured existing project with `-process -noanalysis -readOnly` and contains no project import/create/reanalysis route. |
| xEdit bridge read-only file-record retrieval | BLOCKED_ENVIRONMENT_CURRENT / HISTORICAL_PASS | The documented `file-records` command was attempted through the strict dispatcher and returned 127 before the parser ran. EV-0193 records the earlier QUST result from the direct TES4 parser, but that is not a current cold-start reproduction, native SSEEdit record export, or winning-override result. |
| Selected MO2 profile and full order | NOT_VERIFIED | `MO2_PROFILE_DIR` and `PLUGINS_TXT` are unset in the canonical local config. The selected profile could not be identified from this host, so no profile or complete order was fabricated. This remains a separate blocker for profile-specific winners and negative claims. |
| Native SSEEdit record export | NOT_REQUIRED_FOR_STATIC_RESEARCH / NOT_REPRODUCED | Native SSEEdit selection/export is not a prerequisite for static research. Its record-tree selection/export route remains unverified. The Python file parser and static Ghidra query are the applicable static routes. |
| SKSE installed identity | NOT_VERIFIED | The strict dispatcher did not start the identity probe. |
| Live SKSE connection/observation | NOT_VERIFIED | No live game process, loaded Observer, handshake, snapshot, or DevBench connection was tested. The staged DLL and prior successful build are not proof of a live connection. Live SKSE is not a prerequisite for static research. |
| Consolidated harness doctor | BLOCKED overall | Post-edit report is indexed in EV-0202 and its ignored capture manifest. It recorded 12 PASS, 7 BLOCKED_EXTERNAL, zero FAIL, verdict BLOCKED, exit 2. Structural validators, path/config/domain diagnostics, Markdown audit, compile check, and unit tests passed; external routes remained blocked. The final post-edit doctor is run during this closeout and its raw report remains under ignored `.local/alignment/harness-doctor/`. |

The detailed session capture is ignored under
`.local/alignment/research-start-cold-start-20261015/`. It includes the
actual host, failed bootstrap and strict commands, Windows interop failures,
and a private GOG path-existence check. The private project path remains only
in `config/local.env` and ignored capture metadata.

## Research selection and next step

`research/RECOVERY.json` is idle, has no active transaction, and points
`next_frontier_id` to the initial P0 item Q-0001 (OBJ-1). This matches
`research/FRONTIER.json` and `docs/RESEARCH_START_PROMPT.md`; no bounty
research has started. The selected MO2 profile remains a separate blocker.

On WSL, the authorized setup route from
`docs/LOCAL_RUNTIME_CONTRACT.md` requires installing
`python3.12-venv` through the host package manager, then creating the
repository environment and installing the pinned development requirements:

```sh
sudo apt-get install -y python3.12-venv
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-dev.txt
python3 scripts/python_env.py check --strict
```

On Windows PowerShell, follow the contract’s `py -3.12 -m venv .venv` and
`requirements-dev.txt` commands. After strict Python passes, reproduce the
GOG Address Library and existing-project query exactly as listed in
`docs/LOCAL_RUNTIME_CONTRACT.md`. Run the research-state validator and
consolidated doctor again. Start the first deep research session only after
the strict environment, GOG query, and research-state gates pass.

## SKSE capability ceiling

The Observer source documentation (`observer/docs/README.md`, SHA-256
`7e237e9932e34ccbda4fedced5a734a25ff922a15c8c758d8793f50d4ed56049`,
recorded in EV-0196) describes a bounded observational event sink and offline
timeline/state-diff analysis. It documents marker and snapshot/flush/abort
controls, not game-state mutation.

The same README says the current core does not hook native skill-use,
ActiveEffect lifetime, craft transactions, hit routing, inventory ExtraData,
perk/spell lists, or Story Manager state. The extension plan is proposed work,
not an implemented capability. A staged DLL or successful build does not
establish deployment, plugin load, handshake, event, or snapshot.

## Historical tool handoffs

Earlier records EV-0184–EV-0201 remain historical evidence of their captured
calls. Their outcomes do not supersede this cold-start status. Follow only the
current commands in `docs/LOCAL_RUNTIME_CONTRACT.md`; do not treat old
system-Python/Conda invocations as active fallback routes.

Linux/WSL validation does not establish Windows MO2/xEdit behavior or
in-game Skyrim AE behavior.
