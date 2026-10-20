# Research capability status — 2026-10-16

**Bounded static research routes are available.** EV-0274 records a current strict Python 3.12 check and `research_state.py validate` pass on WSL, and distinguishes offline file/source tools from native Windows, exact-profile, and live-runtime prerequisites. Do not treat this as a current full-suite or repository-validator pass: EV-0211 is a prior 204-test pass, while later EV-0260 reports one fixture failure and repository-validator findings after intervening ledger changes. No tests were rerun for EV-0274.

| Capability | Status | Evidence and boundary |
|---|---|---|
| Python 3.12 bootstrap, strict dispatch and repair | Current strict check PASS; full suite unresolved | Ubuntu 24.04 / WSL2, CPython 3.12.3; all seven pinned distributions/imports pass the current strict check (EV-0274). EV-0203 records prior bootstrap/reuse/repair. EV-0211's dated 204-test pass is followed by EV-0260's later report of one fixture failure and validator findings; no test suite was run for EV-0274. |
| Existing GOG Ghidra project | PASS | EV-0210 is a fresh query through configured `GHIDRA_PROJECT_REP_PATH`: GOG `SkyrimSE.exe` ProductVersion 1.6.1179.0 and hash `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; RVA `0x14C020` returned `FUN_14014c020`, 24 instructions, incoming xref `140230365 -> 14014c020`, and decompilation output. The configured source fingerprint matched its adapter cache. Invocation used `-process -noanalysis -readOnly`; no source-project write, import or reanalysis. |
| Direct plugin-file parser | PASS; separate route | EV-0205: returned QUST record fields from `Skyrim.esm` using the read-only TES4 parser. Not native xEdit and does not resolve winning overrides. |
| Native xEdit official-master query | PASS by preserved receipt; current WSL retry unavailable | EV-0207 and the ignored native-query receipt verify the successful SSEView 4.1.5f export: five official masters plus executable pseudo-file, 149 fields for QUST `dunDA14MorvunskarQST` (`000427A0`), with stage 100 `Shut Down Stage=1`. The cleanup-turn canonical retry failed before SSEView launch because WSL Windows interop returned `UtilBindVsockAnyPort: socket failed 1`; no new export was produced. The doctor validates the preserved receipt. Fixture `tests/fixtures/xedit/native_quest_smoke.json`; guarded copies and scope refusal are in EV-0208. MO2 is not required for vanilla scope. |
| Profile-specific override resolution | NOT CONFIGURED | No selected MO2 profile/full order is verified. Supply the exact target profile and its complete order only when that profile is under study; no negative or winner claim follows from the five-master scope. |
| UESP and private Apocrypha lookup | PASS | EV-0170 and EV-0171 record local retrieval and source provenance. UESP dump completeness/license remain unknown; Apocrypha is private, untrusted lead data. |
| Research state and evidence references | Current PASS | `research_state.py validate` passes current transaction, frontier, evidence, and recovery structure (EV-0274). This validator does not establish claim truth, complete repository hygiene, or native tool operation. |
| SKSE installed identity | PASS; files only | Installed files identify Steam AE 1.6.1170.0. No live game process or Observer connection is implied. |
| Live SKSE/Observer telemetry | NOT VERIFIED; optional | No verified deployed/loaded Observer, handshake, timestamped event/snapshot or DevBench connection. This is not a static-research blocker. |
| Consolidated doctor | Prior PASS; later findings unresolved | EV-0211's `harness_doctor.py all` returned `READY` with profile/live gates separate. Later EV-0260 reports repository-validator metadata/experiment issues and one fixture failure among 204 tests. Current EV-0274 revalidated only strict Python and research state; it did not rerun the full doctor or tests. No game launch or live Observer result is available. |

## Start research

Open the repository in interactive Codex and use the single natural-language
entrypoint in [`RESEARCH_START_PROMPT.md`](RESEARCH_START_PROMPT.md). Codex
performs bootstrap, validation, recovery and transaction bookkeeping internally.
Static research can begin without live SKSE telemetry or a profile-specific
MO2 order; conclusions requiring either remain gated.
