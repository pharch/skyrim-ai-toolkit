---
name: retained-tool-operations
description: Route Skyrim AE research through Python entrypoints, with exact inputs, platform gates, and read-only behavior.
---

# Retained tool operations (Skyrim AE)

Use Python entrypoints for every agent-facing command. Set up the Conda
environment with `conda env create -f environment.yml`; then dispatch through
`python3 scripts/python_env.py run ...`. The dispatcher uses the named Conda
environment when available and falls back to the current Python interpreter
when Conda is absent. Native applications can be dispatched by a tested Python
adapter; do not add agent-facing Node, shell, or Java launchers.

## Target and record tools

- Run `python3 scripts/python_env.py run tools/ae_preflight.py` before any xEdit
  or live-game operation. The gate requires `SkyrimSE.exe` ProductVersion
  1.6.318+, explicit AE scope, and the selected profile's complete active
  `plugins.txt`. A typed version is not evidence. `--probe-executable` is
  diagnostic only and does not authorize xEdit/live access.
- Run `python3 scripts/python_env.py run tools/plugin_reader.py doctor` to test
  the stdlib TES4 reader. Query one file with `record` or `inventory`; use
  `--include-subrecords` to preserve raw CTDA, alias, and VMAD data. This reader
  does not establish the active order or determine winning overrides;
  incomplete inputs cannot support negative findings.
- `python3 scripts/python_env.py run tools/domain_doctor.py` tests the installed local routes and reports
  external prerequisites without printing configured paths or private message
  rows. Run it before selecting an external domain tool.
- Native SSEEdit remains a Windows-only tool. The current selected profile is
  unknown, so full preflight fails and xEdit must remain unlaunched. Do not use
  archived scripts or describe the Python reader as xEdit output.

## Logs, saves, and SKSE

- `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` performs a
  read-only structural survey. It does not decode every mod chunk or prove
  player ActorValues/effect state. Tests use a synthetic fixture, not a user's
  save.
- `python3 scripts/python_env.py run tools/papyrus-triage.py <log>` and
  `python3 scripts/python_env.py run tools/crash-triage.py <file-or-dir>` report
  counts and coverage. Keep private log input local; summarize results in the
  experiment Markdown or evidence database.
- `scripts/read-save.py` supports only its documented read-only header/string/
  byte scans. Structured ReSaver analysis is retired until a Python-only
  reader is reviewed.
- A live SKSE/DevBench bridge is not tested in this environment. Do not connect
  until executable identity and full profile order pass preflight. No live
  mutator is exposed to an unattended run.

## Ghidra, CommonLibSSE, SSEEdit, and archives

- Run `python3 scripts/python_env.py run tools/ghidra_probe.py --analyze
  --analysis-timeout 7200` to import the verified executable into a fresh ignored
  project. Use the same Python command without `--analyze` to query an existing
  project read-only. Inspect logs for analyzer timeouts and script errors; a
  process exit code of zero alone is insufficient.
- The installed route is Ghidra 12.0.4 with Java 21. The hash-attested
  read-only query on the saved Steam 1.6.1170 project passed (EV-0152), exporting
  a function lookup, call edge, disassembly and decompilation. The sample routine
  near image entry is not identified as gameplay code; the broader project is
  incomplete after analysis timeout, so do not transfer its sample address into
  a mechanic claim.
- CommonLibSSE-NG compiled for AE, and an Observer Release DLL built from an
  ignored local source copy with API/PCH corrections (EV-0130, EV-0154). The
  PE32+ x64 artifact exports SKSEPlugin_Load, SKSEPlugin_Query and
  SKSEPlugin_Version (EV-0155). No live game load or handshake was tested.
  xEdit winner queries remain gated on the selected complete active profile.
- Keep archive/Papyrus extraction and save analysis read-only. State input
  coverage and preserve raw artifacts under ignored .local/; do not invoke
  retired wrappers or infer a runtime stage call from PEX strings alone.
- Never write to original game files, plugins, archives, saves, or co-saves.
  If a later tool writes a derived artifact, keep it in ignored local storage
  and preserve the source hash and exact command.

For every result, retain the command, tool version, input identity/hash,
coverage denominator, and epistemic status. Source assertions, inferences,
diagnostic interventions, and vanilla reproductions remain separate.
