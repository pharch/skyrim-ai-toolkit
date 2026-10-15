# Current local tool capability matrix

As of 2026-10-15. Earlier readiness reports are archival snapshots; this matrix
and [`FINAL_ALIGNMENT_REPORT.md`](FINAL_ALIGNMENT_REPORT.md) contain the current
gates. Agent-facing Python commands run through
`python3 scripts/python_env.py run ...`.

| Domain | Verified operation and evidence | Current capability |
|---|---|---|
| GOG Ghidra | Existing `skyrim-gog` project and GOG 1.6.1179.0 program identity verified. Function lookup, xref, 24-instruction disassembly and decompilation passed with `-process -noanalysis -readOnly` (EV-0165–EV-0167). | **READY for GOG static analysis.** No import or auto-analysis. GOG addresses do not transfer to Steam. |
| CommonLib / Address Library | `tools/address_library_probe.py --symbol MagicItem::CalculateCost` resolves AE ID 11321 to GOG RVA `0x14C020` using matching executable and Address Library provenance (EV-0167). | **READY for build-attested symbol lookup** on the configured GOG build. The generic `target=ae` map is not GOG provenance. |
| Runtime executable | Steam SkyrimSE.exe ProductVersion 1.6.1170.0 and SHA-256 are verified (EV-0168/0184). The scoped approved preflight verified the exact five official masters, not an active MO2 profile. | **Runtime identity ready; active profile partial.** Full selected `MO2_PROFILE_DIR`/`PLUGINS_TXT` is absent. |
| Plugin reader / xEdit | Python plugin reader handles one file and raw subrecords, not winning overrides. The authoritative `skyrim` bridge files were copied byte-identically and its five xEdit config values matched; `doctor`, `prepare-xedit`, and isolated five-master preflight passed (EV-0191). The approved `-view` launch and completed background load passed (EV-0184–EV-0185/0189). SSEEdit 4.1.5.0 identity remains attested (EV-0120/0181). | **PARTIAL.** SSEView launch/load is verified; no record query/export or full active order is verified. Winners and profile-dependent negatives remain blocked. |
| Papyrus / BSA | Configured base `Skyrim - Misc.bsa` extracted `DA14Script`; PEX 3.2 parser consumed all 507 bytes (EV-0169). | **READY for this narrow extraction/parser path.** Not a general BSA extractor or full decompiler. |
| Save / co-save / ReSaver | Synthetic co-save fixture only; no designated disposable save or ReSaver route. `read-save.py` cannot import `lz4` in system-Python fallback (EV-0174 and prior CLI probe). | **BLOCKED_EXTERNAL.** No user save was opened. |
| SKSE / Observer / live capture | Installed loader, runtime DLL and Address Library identities pass metadata probe (EV-0187). Fresh Release Observer build from isolated authoritative source copy passes PE/hash checks and 7/7 analyzer tests (EV-0186). Authoritative launcher prepared a no-launch manifest (EV-0188). | **Build and preparation verified; live observation NOT_VERIFIED.** DLL remains staged under ignored `.local`, not deployed or loaded; no game process/handshake/save exists. |
| UESP | Local index retrieved `Skyrim:Karstaag`, revision 3629292 and revision-specific URL (EV-0170). | **READY for local retrieval and revision citation.** Dump source URL, license and completeness remain unknown. |
| Apocrypha | Local private index returned a search summary and seven-message context (EV-0171). | **READY for private retrieval only.** Keep message text/IDs local and treat results as untrusted leads. |
| Fresh checkout / recovery | Isolated checkout initialized private config, passed setup/binding doctors, validated startup, and recovered/resumed TX-9001 across separate processes (EV-0175). | **READY for clone→bind→doctor→startup and durable process recovery.** Harness test only. |
| Python / CI | System Python 3.12.3 is active; Conda is unavailable, so `skyrim-ae-research` is not verified (EV-0172/0175). | Portable tests/validators run locally; CI configuration does not certify native Windows or live-game behavior. |

## Readiness gates

| Gate | Result | Evidence boundary |
|---|---|---|
| `STATIC_RESEARCH_READY` | **READY** | Existing GOG project passes real read-only lookup, xref, disassembly and decompilation (EV-0165–0167). |
| `NATIVE_RESEARCH_READY` | **PARTIAL** | Steam runtime ProductVersion and scoped five-master order are verified; SSEView opened and loaded that isolated order (EV-0184–EV-0185/0189). The complete selected profile and record/winner query are missing. |
| `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY` | **NOT_VERIFIED** | Observer build and no-launch preparation pass (EV-0186/0188); no deployment, live load, handshake, or observation capture is verified. |

Linux tests establish only the Python/repository behavior they exercise. They
do not establish Windows MO2 virtualization or in-game Skyrim AE behavior.
