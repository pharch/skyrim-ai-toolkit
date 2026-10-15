# Harness readiness — setup closeout

**Static Skyrim AE research is ready to begin.** The persistent Python 3.12
environment, strict dispatcher, configured GOG Address Library lookup and
read-only Ghidra function/xref/decompilation query pass on the current WSL
host. Research-state validation passes. This setup session did not begin
bounty investigation or launch Skyrim.

## Readiness gates

| Gate | Status | Evidence-backed result |
|---|---|---|
| Persistent Python 3.12 environment | PASS | Ubuntu 24.04 / WSL2, CPython 3.12.3 at `.local/python-envs/wsl`; all seven exact pins and required imports pass `python3 scripts/python_env.py check --strict`. A fresh disposable environment was created, reused on the next run, and repaired after removing `pytest==8.0.0`; the active environment was not recreated. |
| Strict Python dispatcher | PASS | Research tools ran through `python3 scripts/python_env.py run ...`; the cold test environment also passed strict check and `scripts/research_state.py validate`. See EV-0203 and ignored bootstrap captures. |
| GOG identity and Address Library | PASS | The configured GOG `SkyrimSE.exe` PE ProductVersion is 1.6.1179.0; SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. `MagicItem::CalculateCost` maps to GOG RVA `0x14C020` using the matching Address Library. |
| Existing GOG Ghidra project query | PASS | `GHIDRA_PROJECT_REP_PATH` points to the existing GOG `.rep`, with adjacent `.gpr`. The query found the requested function and RVA, an incoming call xref, disassembly, and decompilation. It used `-process -noanalysis -readOnly`; import, project creation, and reanalysis were not attempted. On this WSL host the source project is mounted read-only, so the adapter queries a metadata-tracked copy under ignored `.local/ghidra/project-cache/`. EV-0204 and `.local/ghidra/gog-query-20261015T111658Z.meta.json` preserve the run. |
| xEdit bridge record retrieval | PASS, file parser only | The documented read-only query returned one `CreatureDialogueWerewolf` QUST record from `Skyrim.esm` via the direct TES4 byte parser (EV-0205). It is not a native SSEEdit query and does not resolve winning overrides. |
| UESP and Apocrypha local access | PASS | The readiness smoke check queried the local UESP index (475,228 pages; 17,520 Skyrim namespace pages; sample revision 3629292) and the private Apocrypha index (60,873 messages). Apocrypha text remains untrusted and private; UESP dump completeness remains unverified. |
| Research evidence/frontier/recovery state | PASS | `python3 scripts/python_env.py run scripts/research_state.py validate` reports `PASS research frontier, evidence links, and recovery state`. Recovery is idle and selects Q-0001. |
| Selected MO2 profile and complete active order | NOT_VERIFIED | `MO2_PROFILE_DIR` and `PLUGINS_TXT` are unset in ignored `config/local.env`. Do not make profile-specific winner claims or negative findings until the selected profile's explicit complete order is validated. This is a separate research limitation, not a blocker for static source work. |
| Native SSEEdit record export | NOT_VERIFIED; not required for static research | The configured executable and helper bindings exist, but no native record-tree selection/export was performed. The tested Python bridge result is file-local. |
| SKSE installed identity | PASS, file metadata only | The installed loader, runtime DLL, Address Library, and executable identify the Steam AE 1.6.1170.0 file set. `tools/skse_probe.py` did not launch Skyrim. |
| Live SKSE/Observer capabilities | NOT_VERIFIED | No live game process, deployed Observer DLL, loaded plugin, handshake, event, snapshot, or DevBench connection was tested. A staged DLL/build is not live observation. Live SKSE is not required for static research. |
| Consolidated harness doctor | 19 PASS, 2 BLOCKED_EXTERNAL, 0 FAIL | EV-0206: `.local/alignment/harness-doctor/20261015T114903.144317Z/harness_doctor.json`, SHA-256 `ea294ef262870deb7a0fd6c821c9af335aa57548f7a29f76cf11d81bd1c85a28`. Overall verdict is BLOCKED/exit 2 only because the selected MO2 profile/full order and native export are unverified, and live SKSE observation was not attempted; static research checks pass. Rerun with `python3 scripts/python_env.py run scripts/harness_doctor.py all`. |

## Start sequence for the next research session

From the repository root on Linux/WSL:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/setup_research.py init
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
```

The config initializer copies the blank template only when the ignored local
file is absent; existing bindings are preserved. Then read this readiness
report and paste the **Initial Codex prompt** from
`docs/RESEARCH_START_PROMPT.md`. The first research transaction is
`TX-0005` / `Q-0001`; the exact `research_state.py begin` command is recorded
there. Bootstrap is a setup repair step. Once the strict environment, state
validator, and local static gates pass, continue the selected frontier instead
of repeating setup.

On Windows PowerShell, use `py -3.12` for each command above. Native Windows
is preferred for game-connected research; WSL results do not establish
Windows MO2/xEdit or in-game behavior.

## Historical setup records

EV-0197–EV-0202 and the older rows in `docs/LOCAL_TOOL_HANDOFF.md` retain
earlier failed or partial setup attempts. They are history, not current
readiness. Current tool invocations are defined only in
`docs/LOCAL_RUNTIME_CONTRACT.md` and the relevant `.agents/skills/` files.

## Cleanup candidates for later review

Keep these until the independent review authorizes cleanup. Setup-only tracked
history includes `migration/FINAL_HARNESS_CLOSEOUT_MISSION.md`,
`migration/FINAL_ALIGNMENT_*`, `migration/FINAL_SETUP_BRIEF.md`, and the older
historical sections of `docs/LOCAL_TOOL_HANDOFF.md`. Current runtime contract,
readiness gates, and next-session prompt are active and should remain. After
their hashes and findings are reviewed, ignored raw acceptance captures under
`.local/alignment/python-bootstrap-final/`,
`.local/alignment/harness-doctor/`, and `.local/ghidra/gog-query-*` can be
pruned. The derived `.local/ghidra/project-cache/` can be regenerated from the
configured GOG project path if it is ever removed. Nothing in this list was
deleted during setup closeout.
