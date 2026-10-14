---
name: save-state-forensics
description: Use read-only Skyrim save and co-save analysis to test quest-state, ActiveEffect, serialization, and experiment-baseline hypotheses.
---

# Save-state forensics

1. Confirm the save belongs to the stated edition and test lane; record its path
   privately, file size, modification time, and cryptographic hash. Never edit,
   overwrite, or clean the original save.
2. Use `python3 scripts/python_env.py run scripts/read-save.py` only for its
   documented header/string/byte scans, and
   `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` for a
   structural co-save survey. These tools do not parse Papyrus variables or
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
