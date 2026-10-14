# Local Research Readiness Report

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

CommonLibSSE-NG compiled for AE (EV-0130), and Ghidra imported the correctly hashed AE executable (EV-0113). The separate 7,200-second analysis session 40253 terminated after 7,260.809 seconds, reported an analysis timeout, and saved an incomplete project (EV-0139). The first two repaired query launches failed at WSL; a third passed the EV-0139 project and executable hash checks, then failed before Ghidra (EV-0131/0138/0141); no current-build xref or decompilation/disassembly export exists. C07/C08 remain BLOCKED_EXTERNAL. Real load-order-aware winner resolution is blocked, and no permitted real save or ReSaver inspection was available.

### `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY` — NOT READY

The CommonLib library build does not establish an Observer DLL build. The Observer target failed on standard-library declarations and the local-only source repair could not be rebuilt because Windows interop failed before MSBuild. SKSE and Address Library file identities match the AE runtime, but no live process handshake or event capture was tested. No disposable save workflow was supplied. The four transactions demonstrate repeated investigation, synthesis and reselection, and the local recovery test uses fresh subprocesses; independent Codex-context recovery remains blocked by auto-review.

## Acceptance tally

Final reconciliation: **64 PASS / 0 FAIL_FIXABLE / 10 BLOCKED_EXTERNAL / 0 NOT_APPLICABLE / 0 PENDING, out of 74**. All rows are classified. C07/C08 are externally blocked after the saved-project query could not launch through WSL interop; session 40253 terminated at its analysis limit (EV-0139), and the third query attempt is EV-0141. The final Markdown inventory write/checks are EV-0147, EV-0149, EV-0150, and EV-0151; EV-0151 follows the completed mission-state handoff synchronization.

Criterion-by-criterion commands, outputs, evidence IDs, changes, and limitations are in [`LOCAL_READINESS_CHECKLIST.md`](LOCAL_READINESS_CHECKLIST.md). External blockers and exact follow-up commands are in [`LOCAL_READINESS_BLOCKERS.md`](LOCAL_READINESS_BLOCKERS.md).

## Capabilities exercised

| Area | Real operation and result | Limit |
|---|---|---|
| AE target and profile | ProductVersion and binary SHA were read from the actual Steam AE executable (EV-0109). | `ae_preflight.py` finds zero active plugins and five missing masters in the resolved global list; selected MO2 profile is unknown (EV-0110). |
| Plugin records and xEdit | Actual Skyrim.esm and Update.esm DA14 QUST `0001BB9B` records were queried with 288 raw subrecords each, including CTDA/ALST/ALID/VMAD. Synthetic two-record winner fixture returns the final candidate in a complete explicit order (EV-0111/0112/0119). xEdit 4.1.5.0 and Node/npm metadata were checked (EV-0120). | No xEdit launch or real winner query: preflight failed. Raw record presence is not condition semantics or an active override. |
| Ghidra and Java | Java 21.0.10 and Ghidra 12.0.4 native headless help/import ran. Attempt2 saved a partial project with 92,219 functions after 1,200 seconds. A separate 7,200-second run timed out and saved an incomplete project (EV-0139). Nine adapter tests and metadata hash checks pass (EV-0140). | No binary-wide negative finding or current xref/disassembly/decompilation export. Three query launches failed before Ghidra through WSL `UtilBindVsockAnyPort` (EV-0131/0138/0141), including one after EV-0139 metadata and executable hashes passed. After WSL recovery, use the exact longanalysis command in the resume note. |
| CommonLib/SKSE | CommonLibSSE-NG commit `b93280e832f263dbef44e44cbe2936622a02f91a` built an AE library, 200,524,092 bytes, SHA256 `230929f4ac49b5dbd8c3c143c43e3983ad788891a3c83baa9201060f32addda2` (EV-0130). SKSE loader/runtime ProductVersion `0,2,2,6` and Address Library runtime filename/hash match local AE 1.6.1170 (EV-0128). | Observer DLL failed; CMakeLists says 3.6.0 while the vcpkg manifest says 3.7.0. Metadata is not a live DLL load or handshake. |
| BSA/Papyrus | DA14Script was extracted from the verified base `Skyrim - Misc.bsa`; the 507-byte PEX 3.2 parser consumed all bytes and identified the Quest parent plus GetState/GotoState bytecode (EV-0121/0122). A bounded literal scan ran (EV-0123). | This is bytecode inspection, not a full source decompiler or proof of quest reachability. One archive's zero literal matches do not prove absence; the optional Creation Club scan was stopped. |
| Saves/ReSaver | The current co-save parser passed synthetic fixture tests; one retained legacy report was inventoried (EV-0125–0127). | Legacy input hash/path unavailable; no disposable real save or ReSaver operation. `lz4` is absent for `scripts/read-save.py`. |
| UESP | Local index doctor reports 475,228 pages and 17,520 pages in namespace 134. Exact revision-cited Enchanting, A Night to Remember, and Ebony Warrior retrievals ran (EV-0124/0129/0134). | Local database hash is known; original source URL, acquisition date, license, and completeness are not. Page text is a secondary-source lead, not current binary behavior. |
| Apocrypha | Local index/context retrieval ran against 60,873 messages with private-field protections (EV-0133). | Private messages remain ignored, untrusted leads. No private content is copied into public research artifacts. |

## Pilot and continuity result

The transaction ledger validates four transactions and 17 events. The imported Ebony Warrior >=80 report was cross-checked against UESP revision 3580051 and a private Apocrypha context capture; CL-L064 records source agreement and the community source’s uncertainty without exposing its message body or identifier. TX-0001 performed actual AE identity/preflight work; the incomplete profile blocked Q-0001 and selected independent Q-0003 (TE-000004/5). TX-0002 wrote rival armor-hit/XP models and imported the current executable into Ghidra. TX-0003 queried real Skyrim.esm MGEF candidates for Q-0015, but did not infer AV39 sign, target, reachability, or winner. TX-0004 retrieved a revision-cited Enchanting page as a breadth investigation and set a matched raw-XP successor. These are bounded source/tool investigations, not reproduced exploits.

Synthesis claim CL-SYN-001 records that the available evidence supports no shared engine primitive between the armor and Enchanting branches. The next prediction is a paired raw Enchanting XP measurement with item value, soul level, effect count, and XP modifiers controlled. This is a falsifiable experiment proposal, not a measured result.

`tests/test_research_transactions.py` exercises a running transaction recovery through separate local subprocesses and verifies resume from persisted state. The stronger independent Codex-context attempt was rejected by automatic review because a proposed external payload could contain repository documents; no repository content was sent. This does not certify cross-context recovery.

## Validation and privacy

Final local validations: 139 unittest tests passed (EV-0145); research/evidence, transaction ledger, overlay, and compileall validators all returned exit 0 (EV-0146). The Ghidra adapter suite passed 9/9 tests after adding exact EV-0139 project attestation (EV-0140). The final Markdown inventory write/check passed after mission closeout state synchronization (EV-0151; earlier passes EV-0147/EV-0149/EV-0150); the staged pre-push/privacy audit passed (EV-0148), followed by a final rerun against the evidence-registered staged tree. Linux tests do not establish Windows MO2, xEdit, native-process bridge, live SKSE, ReSaver, or in-game AE behavior.

## User-only actions, in priority order

1. Set ignored `config/local.env` `PLUGINS_TXT` to the selected MO2 profile's explicit active `plugins.txt`; run `python3 scripts/python_env.py run tools/ae_preflight.py`. Only after it passes should xEdit/winner resolution run.
2. Restore WSL Windows process interop, then run `python3 scripts/python_env.py run tools/ghidra_probe.py --project-dir .local/readiness/ghidra/project_AE_SkyrimSE_1_6_1170_longanalysis --project-name AE_SkyrimSE_1_6_1170_longanalysis --timeout 300` and preserve its raw query result. Session 40253 is finished and its saved analysis is incomplete.
3. Provide a copied disposable `.ess`/co-save pair and provenance; do not use the active save. Run read-only analysis only.
4. After the Observer target rebuilds successfully, select a disposable profile/save and manually launch verified AE+SKSE for the read-only handshake. The original checkout's launch wrapper writes into that original repository; use a `.local`-routed procedure.
5. Provide the UESP snapshot acquisition URL/date/license manifest if available. Run the checked-in Windows CI suite when Windows Python/pytest or a CI runner is available.

First deep-session prompt: [`docs/RESEARCH_START_PROMPT.md`](../docs/RESEARCH_START_PROMPT.md).
