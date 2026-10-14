---
name: retained-tool-operations
description: Route Skyrim AE research through Python entrypoints, with exact inputs, platform gates, and read-only behavior.
---

# Retained tool operations (Skyrim AE)

Use Python entrypoints for every agent-facing command. Set up the Conda
environment with `conda env create -f environment.yml`; then dispatch through
`python3 scripts/python_env.py run ...`. The dispatcher uses the named Conda
environment when available and falls back to the current Python interpreter
when Conda is absent. It never launches Node or a shell wrapper.

## Target and record tools

- Run `python3 scripts/python_env.py run tools/ae_preflight.py` before any xEdit
  or live-game operation. The gate requires `SkyrimSE.exe` ProductVersion
  1.6.318+, explicit AE scope, and the selected profile's complete active
  `plugins.txt`. A typed version is not evidence. `--probe-executable` is
  diagnostic only and does not authorize xEdit/live access.
- Run `python3 scripts/python_env.py run tools/plugin_reader.py doctor` to test
  the stdlib TES4 reader. Query one file with `record` or `inventory`. This
  reader does not establish the active order or determine winning overrides;
  incomplete inputs cannot support negative findings.
- `python3 scripts/python_env.py run tools/domain_doctor.py` tests the installed local routes and reports
  external prerequisites without printing configured paths or private message
  rows. Run it before selecting an external domain tool.
- The old xEditLib/xelib Node integration is retired. Native SSEEdit remains a
  Windows-only external tool; there is no tested Python binding for its winner
  API in this checkout. Do not use archived scripts or describe the Python
  reader as xEdit output.

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

- `python3 scripts/python_env.py run tools/domain_doctor.py` reports local tool candidates and actual
  prerequisites. The current session has a Ghidra candidate but lacks Java,
  a CommonLibSSE source candidate but lacks CMake, and an SSEEdit candidate
  without a verified AE target/order. It does not pretend these native tools
  ran.
- Use the Python TES4 reader for static record fields. Winning-record queries,
  Ghidra decompilation, CommonLib builds, and BSA listing/extraction remain
  blocked until their external runtimes are available and a Python entrypoint
  has a passing test. Do not invoke the archived shell/Node/Java wrappers.
- Never write to original game files, plugins, archives, saves, or co-saves.
  If a later tool writes a derived artifact, keep it in ignored local storage
  and preserve the source hash and exact command.

For every result, retain the command, tool version, input identity/hash,
coverage denominator, and epistemic status. Source assertions, inferences,
diagnostic interventions, and vanilla reproductions remain separate.
