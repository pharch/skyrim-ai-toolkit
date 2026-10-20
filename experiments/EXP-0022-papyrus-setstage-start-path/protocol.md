# Protocol

## Goal

Determine how the GOG AE 1.6.1179.0 native path corresponding to Papyrus `Quest.SetStage` handles a stopped quest, and whether event-scoped status blocks start scheduling. Keep alias filling, Steam equivalence, and gameplay reachability separate.

## Inputs and safety

- Use the existing GOG SkyrimSE.exe 1.6.1179.0 Ghidra project and the matching Address Library.
- Keep the installed Steam 1.6.1170.0 executable as a separate target; do not transfer RVAs.
- Run research commands only through `python3 scripts/python_env.py run`.
- Keep Ghidra read-only with auto-analysis disabled. Do not launch Skyrim or change a quest/save/plugin.

## Steps

1. Search the configured CommonLib source for `SetStage`, `SetCurrentStage`, and `StartQuest` hints. Record source-relative paths and hashes; treat them as discovery only.
2. Resolve `TESQuest::EnsureQuestStarted` and `BGSStoryTeller::BeginStartUpQuest` through the matching GOG Address Library.
3. Query those RVAs in the existing GOG Ghidra project. Inspect direct and incoming edges and decompilation.
4. Follow the GOG callers/helpers at `0x3C9E40` (stage writer), `0x9B2150` (deferred work), `0x3CCD90` (start helper), and `0x3CEF70` (per-entry helper). Preserve raw stdout hashes and query metadata under ignored `.local/ghidra/`.
5. Mark the native identity of `FUN_140a48aa0` as inferred unless a symbolic registration is independently found. Record direct conditions separately from semantic interpretations.
6. Stop short of an alias-fill or level-one claim unless a named alias routine or exact-target read-only test supplies that evidence.

## Reproduction commands

```sh
python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'TESQuest::EnsureQuestStarted'
python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'BGSStoryTeller::BeginStartUpQuest'
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x3C9D30 --timeout 600
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x532E60 --timeout 600
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x3C9E40 --timeout 600
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x9B2150 --timeout 600
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x3CCD90 --timeout 600
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x3CEF70 --timeout 600
```

The query adapter validates GOG binary identity on each invocation. Raw results are private local artifacts and are not committed.
