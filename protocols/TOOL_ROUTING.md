# Tool Routing: Research First, Mod-Building Second

## Preserve these upstream tools (do not reinvent them)

| Tool | Research role | Preconditions / cautions |
|---|---|---|
| xeditlib / `tools/xelib/*` | Inspect base records, conditions, quest/dialogue, MagicEffects, perk entry points, full-load-order overrides | Install `npm install github:WingedGuardian/xeditlib`; Windows DLL/registry assumptions; always check entire active load order, especially MO2 virtualized profiles. Do not use only selected plugins for a negative result. |
| `tools/skyrim-winner.sh` | Determine final winning record and complete override chain | Wrapper exit code is authoritative (raw Node process can have abnormal exit status). Needs xeditlib and correctly resolved plugin list. |
| `tools/resaver-cli.sh` | Read and compare save/changeforms, global data, effect/persistence candidates | Preserve original `.ess`; prefer read-only ops; review all mutation modes; never run `--apply` against a valuable save. |
| `tools/cosave-cli.sh` | Read co-save plugin footprints / container layout | Read-only; does **not** prove exact player AV or ActiveEffect state. |
| Champollion | Decompile `.pex` quest/perk scripts to assist hypothesis generation | Decompiled output is not the original source; note ambiguity and dependencies. |
| Caprica | Compile temporary probe `.psc` in controlled sandbox | Do not automatically deploy compiled output to the game. |
| `tools/devbench-cli.sh` | Live state, console output, Papyrus calls, game liveness | Only when DevBench is explicitly installed via mod manager and user approved live lane. See `protocols/LIVE_GAME.md`. May assume toolkit lives inside game root; test routing before trusting it. |
| `tools/papyrus-triage.py` | Parse whole Papyrus logs without silently dropping severity variants | Counts must reconcile to denominator; compare the correct game install, not whichever directory happens to be found. |
| `tools/crash-triage.py` | Group crashes by module+offset and detect repeated known errors | Be aware of `.log`/`.txt` formats and dropped-file counts. |
| Spriggit | Serialize records for auditable offline diffs | Diagnosis first; do not overwrite original plugins; test on copied workspace. |
| Ghidra (user's existing project) | Native code, precise function/branch/float-state causality | Record binary hash, version, address space, exact addresses, function signatures, and decompiler uncertainty. Tooling is NOT bundled in upstream toolkit. |
| UESP / Apocrypha | Fact-check basic assumptions, harvest claims and proposed tests | Second-order source, not a replacement for direct code/runtime evidence. See `protocols/SOURCES.md`. |

## Deprioritize or remove after inventory

NIF authoring, PyFFI, PyNifly, Blender render-verification, NifSkope visual workflows, texture shaders, audio authoring, MCM UI generators, asset examples, VR controller/animation authoring. Keep their **unique engine facts** in an archive before deletion if they can influence a target. Retain **BSA read/extract capability** and ESP record tooling even if the bundled AutoMod package also supports unrelated asset operations. Do not delete `tools/automod-cli.sh` until a replacement read-only BSA/ESP capability is demonstrated.

## Tool-selection policy

1. Search for an already functioning tool before writing another custom parser/bridge.
2. Validate game version and game-root/load-order resolution.
3. Run `--help`, read source and test a small known-positive and known-negative case.
4. Treat empty output or zero results as ambiguous until checked for correct input, coverage, process exit, and logging.
5. Capture raw tool responses with command, timestamp, version, game build, file hashes, and denominators.
6. Prefer independent validation: xEdit vs raw records, Ghidra vs probes, expected quest condition vs live game observation.

## Important layout incompatibility

Upstream installs tools directly into game root, and some scripts infer the root from their own location. This Codex repo should remain **outside** game root. Do not invoke `setup.sh` or wrappers making such assumptions until a path-compatibility audit passes. Use local path config, adapt wrappers to accept explicit `GAME_ROOT`/load-order variables, and test with a deliberately different read-only fixture path.
