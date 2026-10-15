# Local tool path verification

> Historical snapshot from the prior Steam-oriented setup pass. Superseded for
> current GOG/runtime bindings and readiness by
> `migration/FINAL_ALIGNMENT_REPORT.md`; EV IDs below remain historical unless
> the final report explicitly reuses them.

Machine paths remain in ignored .local/research-paths.toml and
config/local.env. This report records evidence without reproducing those paths.

| Candidate | Operation | Result |
|---|---|---|
| Skyrim AE executable | Windows version resource and SHA256 read-only query. | Verified: Steam AE 1.6.1170.0; hash c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9. |
| Active profile | Full AE preflight. | Blocked: only a global user plugins.txt was resolved; zero active markers and five required masters missing. Selected MO2 profile is unknown. |
| xEdit/SSEEdit | Candidate path and file metadata inspected; no application call. | Blocked by profile gate: do not launch until PLUGINS_TXT names the selected profile's complete explicit active list and ae_preflight.py passes. |
| xEdit/Node/CMake metadata | Read-only Windows file-version/hash and command availability probe; VS-bundled CMake used for the native build. | xEdit 4.1.5.0, 24,580,608 bytes, SHA256 ccb7ca9e6d826868b186b0b9a0fc012affb3fdc9688250583353e6d84e6a2545; Node v22.19.0 and npm present. Standalone CMake is not on PATH; the Visual Studio bundled CMake/MSBuild built the Observer. xEdit was not launched (EV-0120). |
| PEX and BSA | Extracted DA14Script.psc from the verified Steam AE base Misc BSA and inspected its PEX with the active Python route. | Verified bounded operation: BSA SHA256 ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d; 507-byte PEX, output SHA256 24d5993e6fd6553638c70274b3922b7877b59b62ab2454acb6ed822e48339e5d. Creation Club scan is opt-in and was stopped without result. |
| Java and Ghidra | Java 21.0.10 native version probe; Ghidra 12.0.4 headless help/import and a successful read-only query. | EV-0152 records exit 0 on the EV-0139-attested Steam AE project: 93,587 functions, function lookup FUN_1400010d0, call edge 140001164 → 14000110c, 24 disassembly instructions and decompilation of FUN_140001160. The earlier 7,200-second analysis timed out and saved an incomplete project; this generic sample is not gameplay-identified and no old offset is reused. |
| CommonLibSSE-NG | Fresh AE CMake configure and actual MSBuild of CommonLibSSE plus the ignored read-only Observer copy. | CommonLibSSE.lib built for AE from commit b93280e832f263dbef44e44cbe2936622a02f91a (EV-0130); Observer Release DLL built successfully, 584,192 bytes (EV-0154). PE32+ x64 and exports SKSEPlugin_Load, SKSEPlugin_Query and SKSEPlugin_Version verified; DLL SHA256 8ef8a660c8fe2878ee12b445740b70c99b995280bcc58776dba9820f7183e50b (EV-0155). Only the ignored source copy received API/PCH fixes. No live handshake. |
| SKSE and Address Library | `tools/skse_probe.py` read ProductVersion/hash for the installed loader/runtime DLL and hashed the runtime-named Address Library file after verifying the AE executable. | Verified local file identity (EV-0128): loader/runtime ProductVersion `0, 2, 2, 6`; `skse64_1_6_1170.dll` and `versionlib-1-6-1170-0.bin` names match 1.6.1170. Metadata only; no process, DLL load, or DevBench handshake. |
| UESP | SQLite doctor, search, exact Skyrim page retrieval and revision citation. | Verified retrieval: 475,228 indexed pages, 17,520 in custom namespace 134; exact revisions 3538992 (Enchanting), 3593351 (A Night To Remember), and 3580051 (Ebony Warrior) were captured. Source URL, license, acquisition date and completeness remain unknown (EV-0124, EV-0129, EV-0134). |
| Apocrypha | Index lookup and bounded context retrieval with private-field protection. | Verified local retrieval: 60,873 messages, four searches and one context capture are preserved by private-local hash EV-0133. Private content remains ignored and untrusted; it is not reproduced in public claims. |

Do not treat existence as compatibility evidence. No original game, plugin,
archive, save, or co-save was modified. Profile-dependent xEdit and live SKSE
checks remain external blockers.
