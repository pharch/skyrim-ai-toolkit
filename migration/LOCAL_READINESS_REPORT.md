# Local Research Readiness Report

> Historical report for the 74-criterion mission, superseded by
> `migration/FINAL_ALIGNMENT_REPORT.md`. Its older native/project and gate
> assertions are not current unless independently cited there.

## Audit identity

- Mission: `migration/LOCAL_RESEARCH_READINESS_MISSION.md`, read in full; all 74 criteria A01–F12 are classified.
- Branch: `glitch-hunting-setup`.
- Starting HEAD: `e13ae4b253a6f5fd66f0f8abc3e49e6f9b29a6cc`.
- The starting tree contained a deletion of `migration/RESEARCH_READINESS_MISSION.md` and the user-supplied untracked mission file. Both are preserved and excluded from the audit's changes.
- Runtime identity: Steam Skyrim AE `SkyrimSE.exe`, ProductVersion 1.6.1170.0 (normalized 1.6.1170), SHA256 `c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9` (EV-0109).

## Readiness gates

### `STATIC_RESEARCH_READY` — READY, scoped

The active instruction/skill audit, historical source map, UESP and private community retrieval, read-only file-level record queries, research-state validators, and four-transaction pilot provide a working static research loop. This gate does not authorize profile-dependent quest-gate conclusions: the selected MO2 profile and real winning-record query are blocked by the empty/unidentified load order. UESP dump acquisition/license provenance is also still unknown.

### `NATIVE_RESEARCH_READY` — NOT READY

The native Ghidra query now passes against the hash-attested Steam AE project (EV-0152), and CommonLibSSE plus the Observer AE Release DLL build passed (EV-0130, EV-0154, EV-0155). C07/C08 are PASS. The gate remains not ready because the selected full profile is unknown, so no load-order-aware winner query ran, and no permitted real save/ReSaver inspection was available. Ghidra's saved project remains incomplete after its analysis timeout; the queried sample function near image entry has no gameplay identification.

### `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY` — NOT READY

The read-only Observer now builds as a PE32+ x64 Windows DLL and exports SKSEPlugin_Load, SKSEPlugin_Query and SKSEPlugin_Version (EV-0154/EV-0155), but no live game load, handshake, or event capture was tested. No selected disposable profile/save workflow is available. Four transactions demonstrate investigation, synthesis and reselection; separate local subprocess recovery passes, and an independent ephemeral Codex context resumed correctly from sanitized state (EV-0153). Gate 3 remains not ready because Gate 2 and the safe runtime probe workflow are incomplete.

## Acceptance tally

Current reconciliation: **67 PASS / 0 FAIL_FIXABLE / 7 BLOCKED_EXTERNAL / 0 NOT_APPLICABLE / 0 PENDING, out of 74**. All rows are classified. C07/C08 passed on the real Ghidra query (EV-0152), F08 passed on independent fresh-context recovery (EV-0153), and the Observer AE DLL build/export checks passed (EV-0154/EV-0155). Final post-closeout full test and validator rerun is EV-0164; the final Markdown inventory, staged privacy audit, and 74-row/checkpoint audit are EV-0161–EV-0163. Remaining blocked criteria are A04, C01, C03, C12, C13, D09 and F10.

Criterion-by-criterion commands, outputs, evidence IDs, changes, and limitations are in [`LOCAL_READINESS_CHECKLIST.md`](LOCAL_READINESS_CHECKLIST.md). External blockers and exact follow-up commands are in [`LOCAL_READINESS_BLOCKERS.md`](LOCAL_READINESS_BLOCKERS.md).

## Capabilities exercised

| Area | Real operation and result | Limit |
|---|---|---|
| AE target and profile | ProductVersion and binary SHA were read from the actual Steam AE executable (EV-0109). | `ae_preflight.py` finds zero active plugins and five missing masters in the resolved global list; selected MO2 profile is unknown (EV-0110). |
| Plugin records and xEdit | Actual Skyrim.esm and Update.esm DA14 QUST `0001BB9B` records were queried with 288 raw subrecords each, including CTDA/ALST/ALID/VMAD. Synthetic two-record winner fixture returns the final candidate in a complete explicit order (EV-0111/0112/0119). xEdit 4.1.5.0 and Node/npm metadata were checked (EV-0120). | No xEdit launch or real winner query: preflight failed. Raw record presence is not condition semantics or an active override. |
| Ghidra and Java | Java 21.0.10 and Ghidra 12.0.4 imported/opened the verified AE project. Query EV-0152 reported 93,587 functions, lookup FUN_1400010d0, call edge 140001164 → 14000110c, 24 disassembly instructions, and decompilation of FUN_140001160. | Query capability is real, but the project is still incomplete after auto-analysis timeout (EV-0139); the generic sample function near image entry is not identified as gameplay code. No binary-wide negative or gameplay offset is claimed. |
| CommonLib/SKSE | CommonLibSSE-NG built for AE (EV-0130); Observer Release DLL built with local-copy API/PCH fixes (EV-0154), 584,192 bytes, SHA256 `8ef8a660c8fe2878ee12b445740b70c99b995280bcc58776dba9820f7183e50b`; PE32+ x64 and SKSEPlugin_Load/Query/Version exports verified (EV-0155). SKSE runtime ProductVersion `0,2,2,6` and Address Library identity match AE 1.6.1170 (EV-0128). | DLL has not been deployed or loaded. CMakeLists says 3.6.0 while the vcpkg manifest says 3.7.0. No live process handshake. |
| BSA/Papyrus | DA14Script was extracted from the verified base `Skyrim - Misc.bsa`; the 507-byte PEX 3.2 parser consumed all bytes and identified the Quest parent plus GetState/GotoState bytecode (EV-0121/0122). A bounded literal scan ran (EV-0123). | This is bytecode inspection, not a full source decompiler or proof of quest reachability. One archive's zero literal matches do not prove absence; the optional Creation Club scan was stopped. |
| Saves/ReSaver | The current co-save parser passed synthetic fixture tests; one retained legacy report was inventoried (EV-0125–0127). | Legacy input hash/path unavailable; no disposable real save or ReSaver operation. `lz4` is absent for `scripts/read-save.py`. |
| UESP | Local index doctor reports 475,228 pages and 17,520 pages in namespace 134. Exact revision-cited Enchanting, A Night to Remember, and Ebony Warrior retrievals ran (EV-0124/0129/0134). | Local database hash is known; original source URL, acquisition date, license, and completeness are not. Page text is a secondary-source lead, not current binary behavior. |
| Apocrypha | Local index/context retrieval ran against 60,873 messages with private-field protections (EV-0133). | Private messages remain ignored, untrusted leads. No private content is copied into public research artifacts. |

## Pilot and continuity result

The transaction ledger validates four transactions and 17 events. The imported Ebony Warrior >=80 report was cross-checked against UESP revision 3580051 and a private Apocrypha context capture; CL-L064 records source agreement and the community source’s uncertainty without exposing its message body or identifier. TX-0001 performed actual AE identity/preflight work; the incomplete profile blocked Q-0001 and selected independent Q-0003 (TE-000004/5). TX-0002 wrote rival armor-hit/XP models and imported the current executable into Ghidra. TX-0003 queried real Skyrim.esm MGEF candidates for Q-0015, but did not infer AV39 sign, target, reachability, or winner. TX-0004 retrieved a revision-cited Enchanting page as a breadth investigation and set a matched raw-XP successor. These are bounded source/tool investigations, not reproduced exploits.

Synthesis claim CL-SYN-001 records that the available evidence supports no shared engine primitive between the armor and Enchanting branches. The next prediction is a paired raw Enchanting XP measurement with item value, soul level, effect count, and XP modifiers controlled. This is a falsifiable experiment proposal, not a measured result.

`tests/test_research_transactions.py` exercises a running transaction recovery through separate local subprocesses and verifies resume from persisted state. A separate ephemeral read-only Codex context read only a sanitized recovery JSON and returned the exact profile-dependent next action (EV-0153); no repository documents or private source were sent. This verifies fresh-context recovery from the provided state subset.

## Validation and privacy

Final post-closeout validation passed after the evidence ledger and readiness records were complete: all 139 unittest tests plus research/evidence, transaction ledger, overlay, and compileall validators returned exit 0 (EV-0164). The final Markdown inventory write/check covers 155 Markdown files (EV-0161). The staged pre-push/privacy audit is EV-0162; the final 74-row checklist/evidence/gate and exact-checkpoint audit is EV-0163. The Ghidra adapter suite passed 9/9 tests after adding exact EV-0139 project attestation (EV-0140). Conda was unavailable, so the named `skyrim-ae-research` environment is not verified. Linux tests do not establish Windows MO2, xEdit, native-process bridge, live SKSE, ReSaver, or in-game AE behavior. EV-0162 records the staged diff, pre-push, and path scan after the final report, checklist, state, and inventory updates were staged.

## User-only actions, in priority order

1. Set ignored `config/local.env` `PLUGINS_TXT` to the selected MO2 profile's explicit active `plugins.txt`; run `python3 scripts/python_env.py run tools/ae_preflight.py`. Only after it passes should xEdit/winner resolution run.
2. Provide a copied disposable `.ess`/co-save pair and provenance; do not use the active save. Run read-only ReSaver/parser analysis only.
3. After a selected disposable profile/save is available, stage only the built read-only Observer in that profile, manually launch verified AE+SKSE, and capture the handshake under this checkout's ignored `.local/readiness/`. Do not use the original checkout's launcher unchanged because it writes into that original repository.
4. Provide the UESP snapshot acquisition URL/date/license manifest if available.
5. Run the checked-in Windows CI suite when Windows Python/pytest or a connected CI runner is available.

First deep-session prompt: [`docs/RESEARCH_START_PROMPT.md`](../docs/RESEARCH_START_PROMPT.md).
