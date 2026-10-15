---
name: save-state-forensics
description: Use read-only Skyrim save and co-save analysis to test quest-state, ActiveEffect, serialization, and experiment-baseline hypotheses.
---

# Save-state forensics

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

1. Confirm the save belongs to the stated edition and test lane; record its path
   privately, file size, modification time, and cryptographic hash. Never edit,
   overwrite, or clean the original save.
2. Use `python3 scripts/python_env.py run scripts/read-save.py` only for its
   documented header/string/byte scans, and
   `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` for a
   structural co-save survey. `read-save.py` requires the pinned `lz4==4.3.3`
   dependency in the persistent host environment. If the strict dispatcher
   reports it missing, add/confirm its exact pin in `requirements.txt`, rerun
   `scripts/bootstrap_python.py`, and repeat the strict check.
   These tools do not parse Papyrus variables or
   prove an ActiveEffect remains active. Structured ReSaver analysis is not an
   active Python tool in this checkout; do not invoke retired Java/shell
   entrypoints.
3. Record exact command, tool/JAR version, exit code, and complete output. Resolve
   FormIDs against the matching plugin set before interpreting them.
4. For quest experiments, distinguish a quest's changeform/stage from actual event
   initiation, dialogue availability, alias fill, and world encounter state.
5. For alchemy, distinguish a displayed duration from the saved active instance,
   remaining duration, a permanent ability/enchantment, and an effect that was
   reapplied. Compare before/after saves and save-load controls.
6. Keep diagnostic-intervention saves in a separate, clearly named lane. Do not
   infer a vanilla exploit from a console-forced stage, injected script, or
   modified plugin.
7. Treat all save-mutation operations (`--apply`, cleanup, reset, or write modes) as
   out of scope unless the user explicitly authorizes a disposable copy and the
   protocol records the independently verified copy path.

## Evidence and failure modes

- Run the documented commands through `python3 scripts/python_env.py run`.
  Keep raw output and source hashes in ignored `.local/`; record file size,
  timestamp, hash, save/runtime identity, tool version, coverage, and EV ID.
- A retained local co-save output alias exists at
  `.local/readiness/cosave/SAVE-LOCAL-001.stdout.raw` (EV-0125), but the
  original input bytes, source path, and input hash are unavailable. Treat its
  structural result as a bounded retained capture, not a re-identifiable save.
  Current synthetic fixtures (EV-0126/0127) validate parser behavior only.
- Truncation, low co-save coverage, unknown plugin mapping, and missing ReSaver
  are failures/limits to record. Do not treat a parser launch or a zero-result
  scan as proof that a state is absent.
