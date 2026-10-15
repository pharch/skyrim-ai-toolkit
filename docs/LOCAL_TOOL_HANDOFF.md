# Local tool handoff

> Historical setup snapshot. The operation notes below preserve earlier
> captures and may describe status that has since changed. They are not the
> current readiness report or an alternate invocation contract. Use
> `docs/HARNESS_READINESS.md` for current gates and
> `docs/LOCAL_RUNTIME_CONTRACT.md` for the strict Python 3.12 `.venv`, local
> configuration, and implemented commands. System-Python/Conda entries below
> are historical diagnostics, never a research fallback.

**Captured 2026-10-15.** This is an evidence-backed record of the local
operations already performed. It does not add another execution protocol:
`protocols/TOOL_ROUTING.md`, `docs/LOCAL_TOOL_BINDINGS.md`, and the relevant
`.agents/skills/` files remain the operating instructions. Machine paths are
kept in the ignored `config/LOCAL_TOOL_HANDOFF.private.md`; raw output and
large/private inputs remain under ignored `.local/`.

## Verified state

The current alignment report records 50 of 52 criteria as `PASS` and two as
`BLOCKED_EXTERNAL`. The gates are `STATIC_RESEARCH_READY=READY`,
`NATIVE_RESEARCH_READY=PARTIAL`, and
`INSTRUMENTED_AUTONOMOUS_RESEARCH_READY=NOT_VERIFIED`. No open-ended glitch
research was started.

The current handoff probes are preserved under
`.local/alignment/operational-handoff-20261015/`. Their captured exits were:

| Command | Result | Evidence location |
|---|---|---|
| `python3 scripts/python_env.py check` | Exit 0. System Python 3.12.3 works; Conda and `pytest`, `pydantic`, `cattrs` are unavailable. The named Conda environment is not verified. | `python-env-check.stdout.raw` |
| `python3 scripts/python_env.py run scripts/local_paths.py doctor` | Exit 0. Local config and installations are present; ProductVersion and complete active load order are not verified by this WSL doctor. | `local-paths-doctor.stdout.raw` |
| `python3 scripts/python_env.py run tools/domain_doctor.py` | Exit 0. GOG project, CommonLib source, xEdit executable, UESP and Apocrypha indexes are found. No xEdit/live call was made. | `domain-doctor.stdout.raw` |
| `python3 scripts/python_env.py run scripts/research_state.py validate` | Exit 0: `PASS research frontier, evidence links, and recovery state`. | `research-state-validator.stdout.raw` |

Earlier operation evidence is indexed by `research/EVIDENCE.json`. In
particular, EV-0165–EV-0167 cover Ghidra, EV-0169 Papyrus/BSA, EV-0170 UESP,
EV-0171 Apocrypha, EV-0175 cross-process recovery, EV-0176 portable tests,
EV-0184–EV-0189 xEdit/SKSE preparation and EV-0191 the final helper replay and
post-edit checks. These IDs link to ignored raw artifacts and hashes; do not
move their raw contents into Git.

## Tool-by-tool reproduction record

| Tool | Actual tested invocation and result | Persistence and reproduction boundary |
|---|---|---|
| Python dispatcher and validators | `python3 scripts/python_env.py check`; `python3 scripts/python_env.py run -m unittest discover -s tests -v`; `python3 scripts/python_env.py run -m compileall -q scripts tools tests`; `python3 scripts/python_env.py run scripts/validate_research.py`; `python3 scripts/python_env.py run scripts/research_state.py validate`; `python3 scripts/python_env.py run scripts/research_transactions.py validate`; `python3 scripts/python_env.py run scripts/validate_overlay.py`; `python3 scripts/python_env.py run scripts/setup_research.py check`; `python3 scripts/python_env.py run scripts/pre_push_audit.py`. EV-0191 records 151/151 unittests, 13 active-skill validations, and the captured repository validators passing. | Entrypoints and `environment.yml` are tracked. This machine uses system Python 3.12.3 because Conda is unavailable. Another session can reproduce the unittest/stdlib path in this checkout; it cannot claim `skyrim-ae-research` is active. `pytest` is missing. `read-save.py --help` fails at import because `lz4` is missing. No packages were installed in the handoff pass. |
| xEdit / SSEView bridge | On this checkout the successful replay commands were `python3 scripts/python_env.py run .local/xedit-authoritative-copy/scripts/skyrim_tool.py doctor` and `python3 scripts/python_env.py run .local/xedit-authoritative-copy/scripts/skyrim_tool.py prepare-xedit`, followed by `PLUGINS_TXT=<prepared-session>/plugins.txt python3 scripts/python_env.py run tools/ae_preflight.py`. The native executable received `-SSE -view -DontCache -D:<Skyrim Data> -P:<session>\plugins.txt -I:<session>\Skyrim.ini -R:<session>\session.log -O:<session> -S:<session>\`; no `-autoload`. User-approved SSEView 4.1.5f opened (PID 3948, responding) and its five-official-master Background Loader finished (EV-0184–EV-0185/0189). PID 3948 is historical; current process liveness was not rechecked during this handoff. | **Not permanently implemented in this toolkit.** The authoritative bridge is in the sibling `skyrim` checkout. Eight helper/template files were copied byte-identically into ignored `.local/xedit-authoritative-copy/`; the bridge reads its own ignored `.local/xedit-authoritative-copy/config/local.env`, while toolkit AE preflight reads root `config/local.env`; both held matching values, but the snapshots do not synchronize. The later EV-0191 replay only prepared a new session; it did not relaunch xEdit. A fresh clone lacks the ignored helper copy. The exact local source/copy paths and full expanded argument line are in the ignored private note. No `session.log`, record query, or export was produced. The selection-based exporter was not run. |
The EV-0184 output below is real; only the machine-specific `load_order` path
is redacted. The five plugins were Skyrim.esm, Update.esm, Dawnguard.esm,
HearthFires.esm, and Dragonborn.esm. This is not the selected MO2 order.

```json
{
  "edition": "AE",
  "runtime": "1.6.1170",
  "executable_sha256": "c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9",
  "active_plugins": 5,
  "base_plugin": "Skyrim.esm",
  "load_order": "<ignored session path>/plugins.txt",
  "load_order_sha256": "ac010eb54beb86c564605ba023b3192879f9870d409c60a057921e49e6e1bc03",
  "live_runtime_tested": false
}
```
| Ghidra | `python3 scripts/python_env.py run tools/ghidra_probe.py --timeout 600 --rva 0x14C020`; symbol mapping: `python3 scripts/python_env.py run tools/address_library_probe.py --symbol MagicItem::CalculateCost`. The adapter queried the existing GOG project read-only (`-process SkyrimSE.exe -noanalysis -readOnly -postScript ReadOnlyTargetedQuery.java`), resolving `FUN_14014c020`, a real call xref, disassembly and decompilation (EV-0165–EV-0167). | Project/program alias and paths are in ignored `config/local.env`; the authoritative project remains in the external GOG research checkout. Same workstation/session configuration requires no rebind while those paths remain valid. A new clone needs its own bindings. The current Linux doctor cannot verify a host Java executable; actual query evidence came from the configured Windows Ghidra path. Opening in read-only mode refreshed four project index timestamps; no import, overwrite, or analysis ran. GOG 1.6.1179.0 hash is `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; never transfer its RVA to Steam. |
| CommonLibSSE / Address Library | `python3 scripts/python_env.py run tools/address_library_probe.py --symbol MagicItem::CalculateCost` mapped AE ID 11321 to GOG RVA `0x14C020` (EV-0167). The Observer build target used `cmake.exe --build <ignored-build> --target SkyrimStateObserver --config Release -- /m:2`; the first captured compile failed, then a repaired isolated-copy rebuild completed with exit 0 (EV-0186). | `COMMONLIBSSE_ROOT`, `VCPKG_ROOT`, and `ADDRESS_LIBRARY_DIR` are in ignored `config/local.env`. The build tree, local compatibility edits and products are under ignored `.local/readiness/`. The successful rebuild's output/hash are preserved, but its final wrapper invocation was not independently logged as a literal command; do not claim more exact command provenance than the first captured command plus successful build record. No native package was installed by the handoff task. |
| SKSE / Observer | Identity probe: `python3 scripts/python_env.py run tools/skse_probe.py`. It verified Steam runtime 1.6.1170.0, SKSE loader/runtime DLL ProductVersion `0,2,2,6`, and matching `versionlib-1-6-1170-0.bin` (EV-0187). The staged Release DLL is x64 PE32+, 584,192 bytes, SHA-256 `108a4b9a73c97b0517a5cf23f11c02778b9ec3a8f88ac7aadc4fe129a7f7b084`; analyzer fixtures passed 7/7 (EV-0186). The authoritative launcher prepared a manifest with `launch_requested=false` (EV-0188). | **Build is not runtime observation.** Twenty-two source files were copied from `skyrim/observer`; 19 matched exactly and 3 local compatibility edits are in the isolated copy. DLL remains staged under ignored `.local`, not deployed. Toolkit `config/local.env` has `SKSE_LOADER`, while deployment DLL and plugin-list bindings are unset. The prepare copy has its own ignored `config/local.env` containing runtime and loader paths; it does not synchronize with the toolkit registry. The launcher action was a PowerShell `Start-Process` preparation with explicit staged DLL and no `-Launch`; its exact wrapper argv was not retained. No Skyrim process, SKSE connection, plugin load, handshake, or game-state retrieval was observed. The exact staged path and local build inputs are private. |
| MO2 / active order | The xEdit session used the generated five-master list. | `MO2_PROFILE_DIR`, `PLUGINS_TXT`, and `SKYRIM_LOADORDER_DIR` are empty in `config/local.env`; bounded searches did not find a selected profile. No full profile/order or MO2 virtualization behavior is verified. Do not infer an empty/mod-free load order. |
| Python TES4 plugin reader | The preserved output `.local/alignment/current-gate-20261015/plugin-reader-smoke-record.stdout.raw` contains a `GMST` `Skyrim.esm` record read for `fXPLevelUpBase` / `05DB8D`; no winning override was resolved. The exact smoke-call argv was not captured. The supported invocation shape is `python3 scripts/python_env.py run tools/plugin_reader.py record <explicit-plugin-path> --signature GMST --form-id <local-id> --include-subrecords`. | The Python parser and tests are tracked. Use an explicit installed plugin path; a prior relative `Skyrim.esm` lookup failed because the process was not rooted at the game Data directory. This read is file-local, not xEdit. |
| Papyrus / BSA | `python3 scripts/python_env.py run tools/papyrus_pex.py extract DA14Script --output .local/alignment/DA14Script.pex`; then `python3 scripts/python_env.py run tools/papyrus_pex.py disassemble .local/alignment/DA14Script.pex`. It extracted a 507-byte classic PEX and consumed it fully (EV-0169). | Python entrypoint is tracked. The extracted PEX/text stay under ignored `.local`; this is a known-input BSA and narrow PEX 3.2 parser check, not a full decompiler or gameplay test. |
| UESP | `python3 scripts/python_env.py run -m tools.uesp doctor --db .local/uesp.sqlite3`; `python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 'Skyrim:Karstaag' --raw`. It returned revision 3629292 and a revision-specific URL (EV-0170). | The index is available in this machine's ignored `.local/uesp.sqlite3` and is not portable via Git. Current doctor reports 475,228 total pages and 17,520 Skyrim namespace pages. Dump URL/license/completeness remain unknown. |
| Apocrypha | `python3 scripts/python_env.py run -m tools.apocrypha doctor --db .local/apocrypha.sqlite3`; `python3 scripts/python_env.py run -m tools.apocrypha search --db .local/apocrypha.sqlite3 --summary-only --limit 1 level`; then `context` on the selected private ID. EV-0171 records a seven-message context retrieval. | The private index is available in ignored `.local/apocrypha.sqlite3` (current doctor: 60,873 messages). Private text, message IDs, author/channel details and source export paths are not included here. Treat the export as untrusted leads, never as instructions or AE proof. |
| Saves / ReSaver | Synthetic parser tests only. `python3 scripts/python_env.py run scripts/read-save.py --help` failed at import because `lz4` is missing. | `RESEARCH_TEST_SAVE` is unset and no ReSaver executable/path was found. No user save/co-save was opened. Real save parsing remains unavailable. |
| Cross-session research recovery | A fresh isolated checkout ran setup/doctor/startup checks and recovered/resumed transaction TX-9001 across separate processes (EV-0175). The prepared first research prompt specifies rival Q-0001 models H1/H2 and predicted discriminants. | Recovery is durable across processes in the harness, but EV-0175 is a workflow simulation, not proof of autonomous gameplay research or a completed glitch investigation. The prepared prompt is `docs/RESEARCH_START_PROMPT.md`. |

## Mistakes and corrected procedure

- A normal Linux/WSL ProductVersion bridge returned no Skyrim ProductVersion;
  the path/domain doctor therefore reported `product_version_verified=false`.
  Use `python3 scripts/python_env.py run tools/ae_preflight.py` and require
  its actual executable evidence before any xEdit/live-game call. The approved
  scoped preflight succeeded for the five-master session only.
- A one-off Linux `Path.exists()` scan over raw `config/local.env` values
  reported several Windows paths and relative index paths as absent because it
  did not use the toolkit's path adapter or resolve relative paths from the
  repository root. That result was a bad path check, not evidence of missing
  installations. The canonical `local_paths.py doctor` and `domain_doctor.py`
  both exited 0 and reported the configured Ghidra project, CommonLib source,
  xEdit, UESP index and Apocrypha index present; the private note's paths stay
  local.
- The first xEdit launch route did not pass automatic approval. At the user's
  direction, the exact generated `-view` launch was submitted for and received
  explicit user approval; it then opened and loaded the five masters. An
  automatic-approval denial was not evidence that the executable was broken.
  The exact command and evidence are preserved privately and in EV-0184–0189.
- The first native Observer compile failed on local CommonLibSSE API/include
  mismatches (`GetLifeState`, actor-value methods, and standard type includes).
  Compatibility edits were made only in the ignored isolated source copy and
  the later build exited 0. Do not patch the authoritative repository or
  mistake the initial failed output for the later success.
- A relative `Skyrim.esm` record-reader path failed outside the game Data
  working directory. Pass the explicit plugin path.
- A prior analyzer test discovery from the wrong working directory collected
  no tests. Run from the toolkit root with the recorded `unittest discover`
  command; the final Observer analyzer run found and passed seven tests.
- The xEdit UI exposed only panes, no tree/tree-item selection controls. The
  safe response was to stop before record selection/export. Do not send blind
  keyboard input or treat the five-master session as a modded winner result.
- `read-save.py --help` is not a harmless available route here: import fails
  before help because `lz4` is missing. Do not claim ReSaver or a real-save
  parse from synthetic fixtures.
- The bounded MO2 discovery did not identify a selected profile. Its raw
  candidate lists are ignored under `.local/alignment/`; the exact Windows
  enumeration invocations were not retained. Use the actual profile selected
  in MO2 and its explicit `plugins.txt`, not those candidate files.
- Conda, pytest and `lz4` are absent in the current Linux fallback. The passed
  unittest/validator run does not establish the named Conda environment,
  Windows MO2 behavior or in-game AE behavior.

## Git and data boundary

Machine paths are kept in ignored `config/local.env` and
`config/LOCAL_TOOL_HANDOFF.private.md`. Binaries, project stores, local indexes,
raw captures and build products are kept outside Git or under ignored `.local/`.
The Apocrypha source and private message data are deliberately omitted from
this tracked document. Do not add game files, plugin/archive bytes, saves,
credentials, Ghidra databases, UESP dump bytes, or private Discord content to a
commit.

Git closeout status is reported with this handoff. The private path note and
all `.local/` artifacts remain ignored.

## Cold-start reproducibility rerun — 2026-10-15

This section supersedes the earlier handoff only for the later fresh-context
checks. Earlier rows describe the configuration snapshot and successful calls
from their capture time; they are not proof that the next session can invoke
the same tools.

- The toolkit now has a tracked `tools/xedit_bridge.py` route. Its doctor
  staged and hash-checked eight helper/template files; its file-records call
  returned one `Skyrim.esm` QUST from the direct TES4 file parser; and prepare
  generated the five-master view session without launch. The record result is
  not a native xEdit query. The current WSL session cannot start the Windows
  PowerShell/SSEView process, and the available UI automation has no safe
  record-tree selection control for the selection-based Pascal export.
  The configured authoritative `scripts/skyrim_tool.py` help independently
  exposed `records` and `inventory` alongside `doctor`/`prepare-xedit`; the
  exact `records --signature QUST --plugin Skyrim.esm --editor-id
  CreatureDialogueWerewolf` query also exited 0 with the same one-record
  result. Source inspection confirms it dispatches to the direct TES4
  `read_plugin` parser. This is a real read-only bridge record retrieval, not
  native SSEEdit record-tree export or a winning override. Current artifact
  IDs: EV-0192–EV-0194.
- Fresh GOG Address Library, Ghidra, SKSE identity, and scoped AE preflight
  calls stopped before external-tool access because the Windows PowerShell
  bridge did not return ProductVersion. Current raw artifacts are under
  ignored `.local/alignment/cold-start-final-20261015/`; see EV-0195–EV-0196.
- The staged Observer remains a build artifact. Read-only source inspection of
  `observer/docs/README.md` (SHA-256
  `7e237e9932e34ccbda4fedced5a734a25ff922a15c8c758d8793f50d4ed56049`)
  confirms a bounded fixed-size event sink, requested snapshot/flush/abort
  controls, and offline timeline/state-diff analysis. It explicitly lacks
  native skill-use, ActiveEffect-lifetime, craft, hit-routing, inventory
  ExtraData, perk/spell-list, and Story Manager hooks. The extension plan is
  proposed work, not an implemented capability. This rerun observed no
  deployed DLL, game process, plugin load, handshake, snapshot, or DevBench
  connection.
- The ignored root config was aligned with the example only after verifying
  that the deprecated executable alias matched the canonical value. Empty
  deprecated global list fields were removed; selected and disposable profile
  bindings remain empty. Private values were not printed.
- `python3 tools/xedit_bridge.py --help` exposes `doctor`, `prepare`, and
  `file-records` only; it explicitly disclaims native record export. The fresh
  Ghidra, Address Library, SKSE, and preflight diagnostic scripts were invoked
  directly with system Python only after the strict dispatcher gate failed;
  all stopped at ProductVersion/Windows interop before native access. They are
  not new supported invocation routes.
- A repeat clean-venv attempt failed because `ensurepip` is absent; system pip,
  uv, pip3, Conda, and `py` are unavailable. The save reader still fails import
  because `lz4` is absent. No package installation was attempted.
- The primary Python route is now the repository-local Python 3.12 `.venv`
  with pinned `lz4` and PyYAML. This host lacks `.venv`, ensurepip/pip, and
  `lz4`; `python_env.py` fails closed instead of falling back. See
  `docs/LOCAL_RUNTIME_CONTRACT.md` and `docs/HARNESS_READINESS.md`.

The repeat environment capture is under `.local/alignment/cold-start-final-20261015/python-bootstrap-repro/` and its redacted summary is `python_environment_repro.json`. A clean Python 3.12 venv failed because `ensurepip` is absent; pip, uv, pip3, Conda and the Windows `py` launcher were not installed. `read-save.py --help` failed because lz4 is absent. No packages were installed. The consolidated doctor artifact at `.local/alignment/harness-doctor/20261015T082659.406448Z/harness_doctor.json` (EV-0198) reports 19 checks, 12 PASS and 7 BLOCKED_EXTERNAL, zero FAIL, exit 2; its system-Python suite ran 176 tests with 3 dependency-gated skips. `python3 tools/xedit_bridge.py --help` confirms the wrapper exposes no native record query/export command. EV-0197 records the Python probe; EV-0198 is the final consolidated doctor capture.

The previous Conda/system-Python fallback text in older handoff material is
historical; the current dispatcher contract is strict. The current worktree
retains the user-provided untracked closeout mission and bounty packet. No
bounty research was started.
