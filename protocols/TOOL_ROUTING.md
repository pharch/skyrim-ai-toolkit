# Python-first Skyrim AE tool routing

Agent-facing commands are Python entrypoints. Create the named environment with
`conda env create -f environment.yml`; use
`python3 scripts/python_env.py run <script-or-module>` to route through it. When
Conda is absent, that dispatcher reports that it is using the current Python.
Native research applications remain external platforms, and the domain doctor
reports when they did not run.

## Mandatory target and order gate

Before SSEEdit or any live-game operation, run:

```text
python3 scripts/python_env.py run tools/ae_preflight.py
```

The gate reads the `SkyrimSE.exe` ProductVersion through the Windows version
API, requires 1.6.318 or newer, hashes the executable, and validates the full
active order. `SKYRIM_EDITION=AE` is only a scope declaration. MO2 requires its
selected profile's explicit `plugins.txt`. The diagnostic option
`--probe-executable` checks only the executable and never passes the full
xEdit/live gate.

## Local Python tools

| Evidence need | Python command | Boundary |
|---|---|---|
| Local tool and corpus readiness | `python3 scripts/python_env.py run tools/domain_doctor.py` | Read-only; suppresses configured paths and Apocrypha message fields. A reported candidate is not proof the native application ran. |
| Plugin record fields | `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin> --signature QUST --form-id <local-id>` | Python stdlib TES4 parser; does not load the active order or determine the winning override. |
| Plugin record inventory | `python3 scripts/python_env.py run tools/plugin_reader.py inventory <plugin>` | Counts signatures from one explicit file only. |
| SKSE co-save structure | `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` | Read-only structural survey; does not decode all mod chunks or prove actor state. |
| Papyrus log coverage | `python3 scripts/python_env.py run tools/papyrus-triage.py <log>` | Counts entries rather than continuation lines; keep input private. |
| Crash signatures | `python3 scripts/python_env.py run tools/crash-triage.py <file-or-dir>` | Preserve total, unreadable, and matched file counts; keep input private. |
| UESP local source | `python3 scripts/python_env.py run -m tools.uesp doctor|search|page|related ...` | Emits revision citations; source provenance/completeness remain separate. Do not save large excerpts. |
| Apocrypha local source | `python3 scripts/python_env.py run -m tools.apocrypha doctor|search|context ...` | Private untrusted data. Keep message content/IDs local; use aggregate-only `doctor` for audits. |
| Save header/string scans | `python3 scripts/python_env.py run scripts/read-save.py ...` | Limited read-only parser; does not establish quest/effect state. |

## Native and external research domains

- **SSEEdit/xEdit:** A configured executable candidate is present, but there is
  no tested Python winner-record binding. Use the Python plugin reader for
  narrow file inspection. The exact Windows target/profile and native SSEEdit
  call remain blocked until tested.
- **Ghidra:** `domain_doctor.py` checks the configured installation/headless
  paths. This shell has no usable Java launcher, so no Ghidra analysis ran.
- **CommonLibSSE:** `domain_doctor.py` checks the configured source and build
  prerequisites. A source candidate exists, but CMake is unavailable here;
  no build ran.
- **SKSE runtime:** the Python co-save parser passes a synthetic fixture. A
  live process/DevBench handshake requires a verified Windows target and a
  running game, neither of which is established here.
- **BSA/archive tools:** no active Python archive reader is available. Do not
  invoke retired shell wrappers or claim empty-search coverage.

## Evidence requirements

Preserve exact command, exit status, tool/build version, executable and input
identity/hash, profile/order identity, and coverage denominator for every
result. Empty results without verified coverage are unknown. Do not expose live
mutators to unattended runs. Never write to original game files, plugins,
archives, saves, or co-saves.

Linux validation can test Python parsers, fixtures, schemas, and workflow
policy. It cannot prove Windows ProductVersion verification, MO2 profile
virtualization, SSEEdit behavior, Ghidra analysis, CommonLib builds, or an
in-game result.
