# Research capability status — 2026-10-15

**Static research is ready.** The current host's persistent Python 3.12 environment, configured GOG Ghidra adapter, official-master xEdit query, UESP/Apocrypha access and research-state validators have passing evidence. This status is a tested baseline; run the local doctor for the current host before relying on a capability.

| Capability | Status | Evidence and boundary |
|---|---|---|
| Python 3.12 bootstrap, strict dispatch and repair | PASS | Ubuntu 24.04 / WSL2, CPython 3.12.3; seven pinned distributions pass. EV-0203 records creation from absent disposable environment, healthy reuse, and missing-dependency repair. Last active suite: 195 passed. |
| Existing GOG Ghidra project | PASS | EV-0204: GOG `SkyrimSE.exe` ProductVersion 1.6.1179.0 and hash `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; Address Library matched `MagicItem::CalculateCost` to GOG RVA `0x14C020`. Existing configured project returned function, incoming xref, disassembly and decompilation with `-process -noanalysis -readOnly`; no import/reanalysis. |
| Direct plugin-file parser | PASS; separate route | EV-0205: returned QUST record fields from `Skyrim.esm` using the read-only TES4 parser. Not native xEdit and does not resolve winning overrides. |
| Native xEdit official-master query | PASS by preserved receipt; current WSL retry unavailable | EV-0207 and the ignored native-query receipt verify the successful SSEView 4.1.5f export: five official masters plus executable pseudo-file, 149 fields for QUST `dunDA14MorvunskarQST` (`000427A0`), with stage 100 `Shut Down Stage=1`. The cleanup-turn canonical retry failed before SSEView launch because WSL Windows interop returned `UtilBindVsockAnyPort: socket failed 1`; no new export was produced. The doctor validates the preserved receipt. Fixture `tests/fixtures/xedit/native_quest_smoke.json`; guarded copies and scope refusal are in EV-0208. MO2 is not required for vanilla scope. |
| Profile-specific override resolution | NOT CONFIGURED | No selected MO2 profile/full order is verified. Supply the exact target profile and its complete order only when that profile is under study; no negative or winner claim follows from the five-master scope. |
| UESP and private Apocrypha lookup | PASS | EV-0170 and EV-0171 record local retrieval and source provenance. UESP dump completeness/license remain unknown; Apocrypha is private, untrusted lead data. |
| Research state and evidence references | PASS | `research_state.py validate` passes transaction, frontier, evidence and recovery structure. Recovery is idle; `TX-0005` / `Q-0001` is next. This validator does not establish claim truth or native tool operation. |
| SKSE installed identity | PASS; files only | Installed files identify Steam AE 1.6.1170.0. No live game process or Observer connection is implied. |
| Live SKSE/Observer telemetry | NOT VERIFIED; optional | No verified deployed/loaded Observer, handshake, timestamped event/snapshot or DevBench connection. This is not a static-research blocker. |
| Consolidated doctor | PASS for currently available gates | Fresh `harness_doctor.py all` run on 2026-10-15 returned `READY`, with Python/configuration, research state, repository, GOG read-only query, TES4 parser, xEdit helper/prepare mode, stored native export receipt, SKSE installed identity, and hygiene checks passing. Profile override resolution remains `NOT_CONFIGURED`; live SKSE observation remains `NOT_VERIFIED`. EV-0209 preserves the prior 22-check baseline. |

## Start research

From the repository root, run the bootstrap, strict check and research-state validator in the local contract. Then follow [`RESEARCH_START_PROMPT.md`](RESEARCH_START_PROMPT.md) with active task input [`bounties/BOUNTY-0001-LEVEL1-P0.md`](../bounties/BOUNTY-0001-LEVEL1-P0.md). Use the relevant static/records doctor mode; do not wait for live SKSE or an unrelated MO2 profile before static investigation.
