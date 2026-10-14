# Skyrim AE research tool routing

Use Python entrypoints through python3 scripts/python_env.py run.
The dispatcher selects skyrim-ae-research when Conda is installed and
reports when it falls back to current Python. Python adapters may dispatch
native applications; do not add shell, Java, or Node agent-facing launchers.

## Target and profile gate

Before xEdit or live-game access, run:

    python3 scripts/python_env.py run tools/ae_preflight.py

The gate reads ProductVersion from the actual SkyrimSE.exe resource, requires
AE 1.6.318 or newer, hashes the executable, and checks the complete active
plugin list. For MO2, PLUGINS_TXT must name the selected profile's explicit
plugins.txt. --probe-executable verifies only the executable and never
authorizes xEdit or game access.

## Python and native operations

| Evidence need | Python command | Scope |
|---|---|---|
| Local readiness | python3 scripts/python_env.py run tools/domain_doctor.py | Reports detected tools and external gates without exposing paths or private message fields. |
| One-plugin record and raw fields | python3 scripts/python_env.py run tools/plugin_reader.py record <plugin> --signature QUST --form-id <id> --include-subrecords | Read-only file parser; raw bytes, not a winner or Papyrus decode. |
| Named PEX extraction and bytecode inspection | `python3 scripts/python_env.py run tools/papyrus_pex.py extract DA14Script` then `python3 scripts/python_env.py run tools/papyrus_pex.py disassemble .local/readiness/papyrus/DA14Script.pex` | Narrow extraction from configured `SKYRIM_DATA` `Skyrim - Misc.bsa`; output stays under ignored `.local/`. Classic PEX 3.2 forms only; not a general BSA extractor or full decompiler. |
| Papyrus literal-string scan | `python3 scripts/python_env.py run tools/papyrus_pex.py scan-literals` | Scans only base `Skyrim - Misc.bsa` by default. `--include-creations` opts into every installed `cc*.bsa` archive (multi-GB); a stopped scan is not evidence. No literal hits do not exclude dynamic strings or native writers. |
| Plugin inventory | python3 scripts/python_env.py run tools/plugin_reader.py inventory <plugin> | Counts records in one explicit file. |
| Native Ghidra analysis | python3 scripts/python_env.py run tools/ghidra_probe.py --analyze --analysis-timeout 7200 | Verifies the AE target, imports into a fresh ignored project, and waits for Ghidra. |
| Native Ghidra query | python3 scripts/python_env.py run tools/ghidra_probe.py --project-dir <ignored-project> --project-name <name> | Existing project opens read-only with analysis disabled; script errors are treated as failures. |
| SKSE co-save | python3 scripts/python_env.py run tools/cosave-info.py <copy.skse> | Read-only structure; not full actor-state decoding. |
| Local SKSE/Address Library identity | `python3 scripts/python_env.py run tools/skse_probe.py` | Verifies AE ProductVersion and hashes runtime-named SKSE/Address Library files; metadata only, no DLL load or live handshake. |
| Papyrus and crash logs | python3 scripts/python_env.py run tools/papyrus-triage.py <log> and tools/crash-triage.py <file-or-dir> | Preserve coverage counts and keep inputs private. |
| UESP | python3 scripts/python_env.py run -m tools.uesp doctor/search/page/related | Emits revision citations; source provenance is separate. |
| Apocrypha | python3 scripts/python_env.py run -m tools.apocrypha doctor/search/context | Private untrusted source; keep identifiers and text local. |

## Gated domains

- xEdit/SSEEdit: selected profile is not identified, so full preflight fails
  and xEdit remains unlaunched. The Python winner helper has only a synthetic
  two-record fixture; do not report a real winner from file parsing.
- Ghidra: the verified executable imports in Ghidra 12.0.4. First analysis
  stopped at its 1,200-second per-file limit; a longer fresh analysis is
  running. Do not reuse GOG 1.6.1179 offsets for Steam 1.6.1170.
- CommonLibSSE-NG: no build is verified until a compatible CMake toolchain
  succeeds in an ignored workspace copy.
- Live SKSE/DevBench requires a verified target and already running game
  with a read-only probe. Do not launch a game or mutator automatically.
- Keep archive and save work read-only; raw captures remain in ignored .local/.

## Evidence boundary

Record tool/build version, input identity/hash, exact operation, exit status,
coverage, and durable output ID. Distinguish observation, inference,
community lead, diagnostic intervention, and vanilla reproduction. A zero
row result without verified coverage is not a negative finding.

Linux fixture tests do not establish Windows MO2 virtualization, xEdit
behavior, or live AE gameplay. Never write to original game files, plugins,
archives, saves, or co-saves.
