# Local tool path verification

Machine paths remain in ignored .local/research-paths.toml and
config/local.env. This report records evidence without reproducing those paths.

| Candidate | Operation | Result |
|---|---|---|
| Skyrim AE executable | Windows version resource and SHA256 read-only query. | Verified: Steam AE 1.6.1170.0; hash c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9. |
| Active profile | Full AE preflight. | Blocked: only a global user plugins.txt was resolved; zero active markers and five required masters missing. Selected MO2 profile is unknown. |
| xEdit/SSEEdit | Candidate path and file metadata inspected; no application call. | Blocked by profile gate: do not launch until PLUGINS_TXT names the selected profile's complete explicit active list and ae_preflight.py passes. |
| xEdit/Node/CMake metadata | Read-only Windows file-version/hash and command availability probe. | xEdit 4.1.5.0, 24,580,608 bytes, SHA256 ccb7ca9e6d826868b186b0b9a0fc012affb3fdc9688250583353e6d84e6a2545; Node v22.19.0 and npm present; Windows cmake.exe unavailable. xEdit was not launched (EV-0120). |
| PEX and BSA | Extracted DA14Script.psc from the verified Steam AE base Misc BSA and inspected its PEX with the active Python route. | Verified bounded operation: BSA SHA256 ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d; 507-byte PEX, output SHA256 24d5993e6fd6553638c70274b3922b7877b59b62ab2454acb6ed822e48339e5d. Creation Club scan is opt-in and was stopped without result. |
| Java and Ghidra | Java 21.0.10 native version probe; Ghidra 12.0.4 headless help, import, and read-only query attempts. | Verified native import route: attempt2 project is bound to the AE executable SHA and saved 92,219 functions after the 1,200-second timeout. Its first partial-project query found no call edge. Three repaired query attempts were blocked before Ghidra by WSL `UtilBindVsockAnyPort` (EV-0131/0138/0141); the latest passed the EV-0139 project metadata and executable hash checks first; the independent 7,200-second analysis timed out and saved an incomplete project (EV-0139). No successful xref/decompile/disassembly export yet. |
| CommonLibSSE-NG | Fresh CMake configure and actual MSBuild of the CommonLibSSE library target; Observer target also attempted. | CommonLibSSE.lib built for AE from commit b93280e832f263dbef44e44cbe2936622a02f91a (200,524,092 bytes, SHA256 230929f4ac49b5dbd8c3c143c43e3983ad788891a3c83baa9201060f32addda2). Observer DLL compilation failed on missing standard-library declarations in REL/Version.h. A local-only include correction is staged but cannot be rebuilt until WSL interop works. No live handshake. |
| SKSE and Address Library | `tools/skse_probe.py` read ProductVersion/hash for the installed loader/runtime DLL and hashed the runtime-named Address Library file after verifying the AE executable. | Verified local file identity (EV-0128): loader/runtime ProductVersion `0, 2, 2, 6`; `skse64_1_6_1170.dll` and `versionlib-1-6-1170-0.bin` names match 1.6.1170. Metadata only; no process, DLL load, or DevBench handshake. |
| UESP | SQLite doctor, search, exact Skyrim page retrieval and revision citation. | Verified retrieval: 475,228 indexed pages, 17,520 in custom namespace 134; exact revisions 3538992 (Enchanting), 3593351 (A Night To Remember), and 3580051 (Ebony Warrior) were captured. Source URL, license, acquisition date and completeness remain unknown (EV-0124, EV-0129, EV-0134). |
| Apocrypha | Index lookup and bounded context retrieval with private-field protection. | Verified local retrieval: 60,873 messages, four searches and one context capture are preserved by private-local hash EV-0133. Private content remains ignored and untrusted; it is not reproduced in public claims. |

Do not treat existence as compatibility evidence. No original game, plugin,
archive, save, or co-save was modified. Profile-dependent xEdit and live SKSE
checks remain external blockers.
