# Research capability status — 2026-10-15

**Static research is ready.** The current host's persistent Python 3.12 environment, configured GOG Ghidra adapter, official-master xEdit query, UESP/Apocrypha access and research-state validators have passing evidence. This status is a tested baseline; run the local doctor for the current host before relying on a capability.

| Capability | Status | Evidence and boundary |
|---|---|---|
| Python 3.12 bootstrap, strict dispatch and repair | PASS | Ubuntu 24.04 / WSL2, CPython 3.12.3; all seven pinned distributions pass strict dispatch. EV-0203 records creation from an absent disposable environment, healthy reuse, and missing-dependency repair. Final suite: 204 passed (EV-0211). |
| Existing GOG Ghidra project | PASS | EV-0210 is a fresh query through configured `GHIDRA_PROJECT_REP_PATH`: GOG `SkyrimSE.exe` ProductVersion 1.6.1179.0 and hash `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; RVA `0x14C020` returned `FUN_14014c020`, 24 instructions, incoming xref `140230365 -> 14014c020`, and decompilation output. The configured source fingerprint matched its adapter cache. Invocation used `-process -noanalysis -readOnly`; no source-project write, import or reanalysis. |
| Direct plugin-file parser | PASS; separate route | EV-0205: returned QUST record fields from `Skyrim.esm` using the read-only TES4 parser. Not native xEdit and does not resolve winning overrides. |
| Native xEdit official-master query | PASS by preserved receipt; current WSL retry unavailable | EV-0207 and the ignored native-query receipt verify the successful SSEView 4.1.5f export: five official masters plus executable pseudo-file, 149 fields for QUST `dunDA14MorvunskarQST` (`000427A0`), with stage 100 `Shut Down Stage=1`. The cleanup-turn canonical retry failed before SSEView launch because WSL Windows interop returned `UtilBindVsockAnyPort: socket failed 1`; no new export was produced. The doctor validates the preserved receipt. Fixture `tests/fixtures/xedit/native_quest_smoke.json`; guarded copies and scope refusal are in EV-0208. MO2 is not required for vanilla scope. |
| Profile-specific override resolution | NOT CONFIGURED | No selected MO2 profile/full order is verified. Supply the exact target profile and its complete order only when that profile is under study; no negative or winner claim follows from the five-master scope. |
| UESP and private Apocrypha lookup | PASS | EV-0170 and EV-0171 record local retrieval and source provenance. UESP dump completeness/license remain unknown; Apocrypha is private, untrusted lead data. |
| Research state and evidence references | PASS | `research_state.py validate` passes transaction, frontier, evidence and recovery structure. Recovery is idle after historical `TX-0004`; `Q-0001` is the next ready frontier item and the next transaction ID is generated internally when an agent begins it. This validator does not establish claim truth or native tool operation. |
| SKSE installed identity | PASS; files only | Installed files identify Steam AE 1.6.1170.0. No live game process or Observer connection is implied. |
| Live SKSE/Observer telemetry | NOT VERIFIED; optional | No verified deployed/loaded Observer, handshake, timestamped event/snapshot or DevBench connection. This is not a static-research blocker. |
| Consolidated doctor | PASS for static research | EV-0211: final `harness_doctor.py all` returned `READY`; 21 checks include 19 `PASS`, one `NOT_CONFIGURED` selected-profile override gate, and one `NOT_VERIFIED` live SKSE/Observer gate. GOG read-only query, research state, local configuration, Python, direct TES4 parsing, xEdit helper/prepare and the preserved native export receipt pass. No game or native application was launched by the doctor. |

## Start research

Open the repository in interactive Codex and use the single natural-language
entrypoint in [`RESEARCH_START_PROMPT.md`](RESEARCH_START_PROMPT.md). Codex
performs bootstrap, validation, recovery and transaction bookkeeping internally.
Static research can begin without live SKSE telemetry or a profile-specific
MO2 order; conclusions requiring either remain gated.
