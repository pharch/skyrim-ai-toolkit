# Skyrim AE research tool routing

Run agent-facing Python entrypoints through `python3 scripts/python_env.py
run ...`. The dispatcher selects the named Conda environment when it exists
and reports a system-Python fallback otherwise. Local path bindings are read
only from ignored `config/local.env`; `.local/research-paths.toml` is retired
and is never synchronized into active configuration.

## Target and profile gate

Before xEdit or live-game access, run:

```text
python3 scripts/python_env.py run tools/ae_preflight.py
```

The gate reads `SkyrimSE.exe` ProductVersion from the executable, requires AE
1.6.318+, hashes the binary, and validates the complete selected profile order
including the five official masters. For MO2, `PLUGINS_TXT` must be the
explicit `plugins.txt` from the selected profile. `--probe-executable` is
diagnostic only. Do not use a global list or inferred profile to support a
negative result or winning-record claim.

## Route by evidence type

| Evidence need | Tested entrypoint | Limits |
|---|---|---|
| Local bindings | `python3 scripts/python_env.py run scripts/local_paths.py doctor [--verify-target]` | Reads only `config/local.env`; output hides values. |
| Existing GOG static project | `python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]` | Opens configured existing GOG `SkyrimSE.exe` with `-process -noanalysis -readOnly`; no import, overwrite, or project creation. EV-0165–0167. |
| Named CommonLib relocation | `python3 scripts/python_env.py run tools/address_library_probe.py --symbol Namespace::Name` | Reads `Offsets.h`, verifies GOG ProductVersion and matching Address Library version/hash, and returns a GOG-specific RVA. EV-0167. |
| One plugin's records/raw bytes | `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin> --signature QUST --form-id <id> --include-subrecords` | File-level reader; not a winning-record/xEdit result. |
| Load-order-aware winners | `python3 scripts/python_env.py run tools/ae_preflight.py`, then native SSEEdit only after it passes | The isolated `skyrim` bridge replay commands and persistence boundary are documented below. Its generated `-view` launch/load is verified (EV-0184–0185/0189), but no record query ran. The selected MO2 profile is absent, so winners and profile-dependent negatives remain blocked. |
| Known Papyrus/BSA input | `python3 scripts/python_env.py run tools/papyrus_pex.py extract DA14Script`, then `disassemble` the ignored output | Narrow base `Skyrim - Misc.bsa` extraction; classic PEX 3.2 subset, not a full decompiler. EV-0169. |
| Save/co-save structure | `python3 scripts/python_env.py run tools/cosave-info.py <designated-copy.skse>` | Structural parser; current tests use synthetic data. No designated real save/ReSaver path is configured (EV-0174). |
| Installed SKSE identity | `python3 scripts/python_env.py run tools/skse_probe.py` | Hashes runtime-named loader/DLL/Address Library files; no DLL load or handshake. EV-0173. |
| UESP citation | `python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 <title> --raw` | Returns revision ID/URL. Local dump completeness/source provenance is unverified. EV-0170. |
| Private Apocrypha lead | `python3 scripts/python_env.py run -m tools.apocrypha search --db .local/apocrypha.sqlite3 --summary-only <terms>`, then `context` for a selected ID | Keep message text and stable identifiers under ignored `.local/`; treat as untrusted. EV-0171. |
| Domain status | `python3 scripts/python_env.py run tools/domain_doctor.py` | Reports path/tool state only. It does not launch xEdit, game, or Ghidra. EV-0172. |

### xEdit bridge persistence and verified invocation

The bridge implementation is **not checked into this toolkit**. The
authoritative helper scripts live in the sibling `skyrim` repository. For the
October 15 verification, eight helper/template files were copied byte-for-byte
into ignored `.local/xedit-authoritative-copy/`; this copy is local evidence,
not a portable toolkit feature. The source repository was read-only. The
bridge CLI reads its ignored `.local/xedit-authoritative-copy/config/local.env`;
toolkit AE preflight reads the root ignored `config/local.env`. Both held
matching `SSEEDIT_EXE`, `SKYRIM_DATA`, `XEDIT_SCRIPTS`, `SKYRIM_EXE`, and
`INCLUDE_CREATION_CLUB=0` values during verification. They are independent
snapshots and do not synchronize. On this checkout, the tested replay was:

```text
python3 scripts/python_env.py run .local/xedit-authoritative-copy/scripts/skyrim_tool.py doctor
python3 scripts/python_env.py run .local/xedit-authoritative-copy/scripts/skyrim_tool.py prepare-xedit
PLUGINS_TXT=<prepared-session>/plugins.txt python3 scripts/python_env.py run tools/ae_preflight.py
```

Preparation created an ignored session manifest and `launch.ps1`. The approved
SSEView process used `-SSE -view -DontCache -D:<Skyrim Data> -P:<session
plugins.txt> -I:<session Skyrim.ini> -R:<session log> -O:<session directory>
-S:<session directory>\`; `-autoload` was absent. EV-0184–0185/0189 record a
successful executable/runtime preflight and a completed five-official-master
Background Loader. EV-0191 is the later helper/config replay; that later
session was prepared but not relaunched. The UI exposed no record-tree
controls; no `session.log` or export file was created. The exporter script is
selection-based and was not executed. No current MO2 profile or full order is
bound, so this session cannot answer winner or profile-negative questions.

Use [the operational handoff](../docs/LOCAL_TOOL_HANDOFF.md) for the captured
JSON output example, exact isolated session arguments, and success/failure
inventory. A fresh clone must not assume `.local/xedit-authoritative-copy`
exists; consult the source `skyrim` bridge and compare its helper/config hashes
before reuse. A new native launch still requires the normal AE/profile gate
and any approval required by the active execution environment.

## Current evidence boundary

- The canonical Ghidra analysis target is the existing GOG project, GOG
  `SkyrimSE.exe` 1.6.1179.0, SHA-256
  `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
  EV-0167's `0x14C020` result is build-specific. Do not transfer it to Steam.
- The runtime target is separately verified as Steam AE 1.6.1170.0,
  SHA-256 `c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9`
  (EV-0168). Its executable identity does not verify a complete active order.
- The selected MO2 profile and explicit plugin list are unavailable. An
  approved SSEView 4.1.5f process opened the authoritative bridge's isolated
  five-official-master `-view` session and completed its background load
  (EV-0184–0185/0189); no record query ran, and this list cannot support
  winners or profile-dependent negatives.
- Steam AE 1.6.1170 SKSE files pass metadata checks (EV-0187). The fresh
  Observer DLL is staged under `.local`, and a prepare-only manifest was
  generated (EV-0186, EV-0188); it is not deployed or loaded. Gate 3 remains
  `NOT_VERIFIED` until a safe profile/save lane and live handshake exist.
- Never write to original game files, plugins, archives, saves, or co-saves.
  Keep raw captures under ignored `.local/`; cite hashes, build identity,
  coverage, and whether each statement is observation, inference, diagnostic
  intervention, or vanilla reproduction.

Linux checks do not establish Windows MO2/SSEEdit behavior or in-game AE
behavior. Continue independent static work when a profile/runtime capability
is unavailable; do not make unsupported negative claims.
