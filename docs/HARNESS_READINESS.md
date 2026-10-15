# Harness readiness — 2026-10-15

**Static Skyrim AE research is ready.** The current strict Python environment,
GOG Ghidra adapter, direct TES4 reader, and recovered native xEdit workflow have
all passed their documented checks. Research state is idle with `Q-0001` next.
This setup session did not start bounty research or launch Skyrim.

## Readiness gates

| Gate | Status | Evidence |
|---|---|---|
| Persistent Python 3.12 and strict dispatcher | PASS | Ubuntu 24.04 / WSL2, CPython 3.12.3 at ignored `.local/python-envs/wsl`; seven pinned distributions and imports pass `python3 scripts/python_env.py check --strict`. EV-0203 records absent-environment creation, healthy reuse, and missing-dependency repair. Current active suite: 195 passed. |
| GOG identity and Ghidra | PASS | EV-0204: configured GOG `SkyrimSE.exe` ProductVersion 1.6.1179.0, hash `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; Address Library maps `MagicItem::CalculateCost` to RVA `0x14C020`. Read-only query of the existing configured GOG project returned the function, incoming xref, disassembly, and decompilation using `-process -noanalysis -readOnly`; no import or reanalysis. |
| Direct plugin-file parsing | PASS, separate route | EV-0205: `file-records` returned a named QUST and raw fields from `Skyrim.esm` through the read-only TES4 parser. This route does not run xEdit or calculate a winning override. |
| Native xEdit record export | PASS, five official masters | EV-0207: a fresh `native-query` launched configured SSEView 4.1.5f and ran the recovered original Pascal field walker through the original Apply Script hotkey route. It loaded `Skyrim.esm`, `Update.esm`, `Dawnguard.esm`, `HearthFires.esm`, and `Dragonborn.esm` plus the `SkyrimSE.exe` pseudo-file; exported 149 rows for `Skyrim.esm` QUST `dunDA14MorvunskarQST` (form `000427A0`). Stage 100 has `Shut Down Stage=1`; VMAD fragments reference stages 20, 30, and 100. TSV SHA-256: `e061837ec22bd737355f2cad1c6cedb5052fd4530d4b740f19b680fb6bcb4213`. Fixture: `tests/fixtures/xedit/native_quest_smoke.json`. |
| xEdit source and native scope | PASS, guarded | The bridge stages hash-verified helper files from ignored `config/local.env`'s `LEGACY_SKYRIM_REPO`. It copies only the five official masters and matching vanilla strings to a read-only ignored `.local` Data view. EV-0208 records why: a direct configured-Data launch auto-loaded Creation Club/user plugins despite the generated list; the exporter refused to write output. The official view prevents that scope leak. |
| Profile-specific override resolution | NOT_CONFIGURED | MO2 is optional. No selected profile/full order is configured, so the five-master result does not support profile-specific winner or negative claims. Configure the target's actual complete order only when that profile is the research target. |
| UESP and Apocrypha local access | PASS | EV-0170 and EV-0171 verified local retrieval and provenance. Apocrypha remains private and untrusted; UESP dump completeness is not established. |
| Research evidence/frontier/recovery state | PASS | `python3 scripts/python_env.py run scripts/research_state.py validate` reports `PASS research frontier, evidence links, and recovery state`. Recovery is idle and selects `Q-0001`. |
| SKSE installed identity | PASS, file identity only | The installed identity probe passes for Steam AE 1.6.1170.0. A staged Observer DLL is only file metadata evidence. |
| Live SKSE/Observer capabilities | NOT_VERIFIED, optional | No game process, deployed/loaded Observer plugin, handshake, event, snapshot, or DevBench connection was observed. Live operation is not required for static research. |
| Consolidated harness doctor | PASS | EV-0209 records the final `all` report, exact check counts, artifact path, and report hash. The optional profile and live SKSE gates are labeled separately and do not block static readiness. |

## Research start

From the repository root, bootstrap or reuse the persistent host environment,
validate the strict dispatcher, and validate research state:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
```

On Windows PowerShell, use `py -3.12` in place of `python3`. Then read
`docs/RESEARCH_START_PROMPT.md` and begin `TX-0005` / `Q-0001` in that research
session. If a preflight fails, repair the environment or local setup and
recheck it before calling it an external blocker. Once these static gates pass,
proceed with the selected frontier rather than continuing setup work.

Native official-master xEdit command:

```sh
python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm --editor-id dunDA14MorvunskarQST
```

The native command uses Windows PowerShell interop from WSL or native Windows.
`MO2_PROFILE_DIR` is not needed for official masters. Use the configured
target's complete actual load order for profile-specific override findings.

## Historical setup records

EV-0197–EV-0206 and earlier entries in `docs/LOCAL_TOOL_HANDOFF.md` retain
failed or partial setup attempts. They are historical; current routes are
defined in `docs/LOCAL_RUNTIME_CONTRACT.md` and the relevant `.agents/skills/`.

## Cleanup candidates for later review

Keep setup and migration history until the independent review authorizes
cleanup. Possible later candidates include `migration/FINAL_HARNESS_CLOSEOUT_MISSION.md`,
`migration/FINAL_ALIGNMENT_*`, `migration/FINAL_SETUP_BRIEF.md`, historical
sections of `docs/LOCAL_TOOL_HANDOFF.md`, and ignored raw acceptance captures.
Nothing in this list was removed during this task.
