# Local tool capability matrix

Agent-facing operations use Python entrypoints through
python3 scripts/python_env.py run. Those Python tools may dispatch a verified
native application when its platform and safety gates allow it.

| Domain | Verified operation | Current status and limit |
|---|---|---|
| AE executable | Windows FileVersionInfo ProductVersion and SHA256 read-only query. | PASS: Steam AE 1.6.1170.0 (normalized 1.6.1170), SHA256 c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9. The WSL bridge requires Windows interop. |
| Active AE profile | Full ae_preflight.py attempted against configured PLUGINS_TXT. | BLOCKED_EXTERNAL: selected MO2 profile is not identified. Resolver reached global plugins.txt, with zero active entries and all five required masters missing. No xEdit or game call followed. |
| Plugin records | plugin_reader.py queried real Skyrim.esm and Update.esm DA14 QUST records and emitted raw subrecord bytes; a two-record synthetic winner fixture passed. | PASS (bounded): same real FormID 0001BB9B, each with 2 CTDA, 26 ALST, 26 ALID, and 1 VMAD. The resolver fixture selects the last explicit-order candidate. No real active-profile winner or Papyrus semantics inferred. |
| Ghidra | Python-dispatched Ghidra 12.0.4/Java 21 native import of the verified AE image; bounded read-only function/xref/disassembly/decompilation query. | PASS for native query (EV-0152): the EV-0139-attested Steam AE project reported 93,587 functions, resolved FUN_1400010d0, exported call edge 140001164 → 14000110c, 24 disassembly instructions, and decompilation of FUN_140001160. The prior auto-analysis timeout leaves the project incomplete; the sample is not identified as a gameplay routine and supports no binary-wide negative or gameplay-offset claim. |
| CommonLibSSE-NG | Actual CMake/MSBuild built `CommonLibSSE.lib` for AE (EV-0130) and a read-only Observer Release DLL from an ignored local source copy (EV-0154); PE32+ x64 and SKSE entrypoint exports were verified (EV-0155). | PASS for the AE library and Observer build. The local copy required an AE subobject API correction and CommonLib PCH setup; the original source was not changed. CMakeLists version 3.6.0 and vcpkg manifest 3.7.0 differ. The DLL has not been loaded in Skyrim; no SKSE runtime handshake occurred. |
| SKSE / Address Library / co-save | Read-only `skse_probe.py` verifies local AE/SKSE/Address Library file metadata; `cosave-info.py` inventories co-save chunk structure. | PASS (bounded): loader/runtime DLL ProductVersion `0, 2, 2, 6`, runtime filename and Address Library filename match AE 1.6.1170 (EV-0128). Retained co-save output EV-0125 reports 19 chunks/15 opcodes/100% flat coverage, but source input bytes/path/hash are unavailable; current parser synthetic checks pass EV-0126/0127. No internal save-state decode or live game/DevBench handshake (C12 blocked). |
| xEdit / SSEEdit | Executable candidate configured; file-level metadata available. | BLOCKED_EXTERNAL: no selected complete active profile, so preflight failed closed and xEdit was not launched. No real winner query claimed; the synthetic Python fixture is not an xEdit operation. |
| UESP | Local indexed snapshot supports exact title, full text, search, related pages, and revision-cited retrieval. | PASS (retrieval only): database works. Snapshot source URL, license, and completeness remain unknown. |
| Apocrypha | Local SQLite lookup/context operations executed with private-field safeguards. | PASS (private untrusted leads): 60,873 messages indexed; content and identifiers remain ignored. Community statements are not runtime evidence. |
| Papyrus / BSA / logs | Python entrypoint extracted actual DA14Script.psc from verified Steam AE `Skyrim - Misc.bsa`, decoded the 507-byte PEX 3.2 stream, and ran a bounded literal scan. | PASS (current local operation): extraction/bytecode evidence EV-0121/0122; base archive scan EV-0123. A historical scan EV-0083 reported 14,025 streams over its archived scope. The 74 installed Creation Club archives total 6.26 GB; the optional scan was stopped without result. Neither scan proves absence of dynamic strings/native writers. |
| xEdit metadata / Node / CMake | Read-only Windows metadata and host-tool lookup; xEdit application deliberately not launched. | xEdit 4.1.5.0, Node v22.19.0, npm present, Windows CMake absent (EV-0120). xEdit integration remains blocked by the unidentified selected profile and failed full-order preflight. |
| Python environment | python3 scripts/python_env.py check and stdlib test suite. | PARTIAL: system Python 3.12.3 is in use; Conda is unavailable, so the named environment is unverified. |

Raw binaries, private corpora, logs, saves, and heavyweight Ghidra projects stay
in ignored .local/. Linux fixture results do not establish Windows MO2, xEdit,
live handshake, or gameplay behavior. See LOCAL_READINESS_REPORT.md and
LOCAL_READINESS_BLOCKERS.md.
