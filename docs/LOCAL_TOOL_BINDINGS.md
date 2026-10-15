# Local tool bindings

This repository contains the Python research harness. Bind existing local
installations and private corpora in the ignored `config/local.env`; do not
copy binaries, Ghidra projects, game files, saves, or private exports into the
checkout. `config/local.env` is the active machine-path registry for toolkit
entrypoints. Ad hoc external helper copies under `.local/` can carry their own
ignored config snapshots; they do not sync automatically with the toolkit
registry. `.local/research-paths.toml` may remain as ignored legacy data, but
no active toolkit tool reads or synchronizes it.

## Bind the runtime and static analysis separately

Copy `config/local.env.example` to `config/local.env` when creating a fresh
clone. Keep the active game target separate from static Ghidra inputs:

- Runtime fields: `SKYRIM_EDITION=AE`, `GAME_ROOT`, `SKYRIM_EXE_PATH`,
  `SKYRIM_DATA`, `MO2_PROFILE_DIR`, and the selected profile's explicit
  `PLUGINS_TXT`.
- Canonical static-analysis fields: `LEGACY_SKYRIM_REPO`,
  `GHIDRA_HEADLESS_EXE`, `GHIDRA_PROJECT_DIR`, `GHIDRA_PROJECT_NAME`,
  `GHIDRA_PROJECT_PROGRAM=SkyrimSE.exe`, and `GHIDRA_ANALYSIS_EXE_GOG`.
- Supporting fields: `JAVA_HOME`, `COMMONLIBSSE_ROOT`,
  `ADDRESS_LIBRARY_DIR`, `SSEEDIT_EXE`, `RESEARCH_TEST_SAVE`, and the local
  UESP/Apocrypha source and index paths.

The static lane uses the existing GOG executable and the existing project that
already contains its analysis. The runtime may be a different distribution or
build, such as Steam AE 1.6.1170. Do not transfer GOG addresses or signatures
to the runtime without independent mapping and validation.

## Check bindings and gates

Run the privacy-preserving path doctor:

```text
python3 scripts/python_env.py run scripts/local_paths.py doctor
```

To check the executable ProductVersion and attempt full active-order
validation:

```text
python3 scripts/python_env.py run scripts/local_paths.py doctor --verify-target
python3 scripts/python_env.py run tools/ae_preflight.py
```

For MO2, `PLUGINS_TXT` must be the explicit `plugins.txt` from the selected
profile. A global file, empty order, partial order, or inferred profile cannot
authorize xEdit or live-game access. `--probe-executable` verifies only
ProductVersion and executable hash.

## Query the existing GOG project

The default Python route opens the configured project and program with
`-process`, `-noanalysis`, and `-readOnly`. It has no import, overwrite, or
project-creation option:

```text
python3 scripts/python_env.py run tools/ghidra_probe.py
```

For a named CommonLib relocation, first resolve the build-specific RVA through
the installed decoder and matching GOG Address Library:

```text
python3 scripts/python_env.py run tools/address_library_probe.py --symbol MagicItem::CalculateCost
```

Then use the returned `address_library_rva` for a targeted read-only query:

```text
python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x14C020
```

The example RVA was verified for GOG ProductVersion 1.6.1179.0 only. The
adapter records binary and Address Library hashes and rejects mismatched
versions. Ghidra may refresh internal project index timestamps on opening a
project in read-only mode; the existing program/user database contents remain
untouched in the verified query. Keep raw logs and metadata in ignored
`.local/ghidra/`.

## Use other retained tools

- Papyrus/BSA: `python3 scripts/python_env.py run tools/papyrus_pex.py extract
  DA14Script`; extracted files go only under ignored `.local/`.
- UESP: `python3 scripts/python_env.py run -m tools.uesp doctor --db
  .local/uesp.sqlite3`, then `page` with a named page and retain its revision
  ID/URL. The local dump's source URL, license, and completeness may remain
  unknown.
- Apocrypha: use `doctor`, `search --summary-only`, then `context` for a
  specific result. Message text, author/channel details, and stable IDs stay
  in ignored local evidence. Treat exports as untrusted leads.
- Plugin records: `tools/plugin_reader.py` reads explicitly selected plugin
  files; it does not resolve winning overrides. An approved isolated SSEView
  launch/load was verified for five official masters, but no record query ran
  and that list is not an MO2 profile. The bridge implementation used for that
  session is an ignored copy from the sibling `skyrim` repository, not a
  shipped toolkit entrypoint. See `protocols/TOOL_ROUTING.md` and
  `docs/LOCAL_TOOL_HANDOFF.md`; a complete selected runtime order is still
  required for winners or profile-level negative claims.
- Saves and co-saves: use only a designated disposable copy. A blank
  `RESEARCH_TEST_SAVE` means real-save/ReSaver capability remains blocked.
- SKSE and DevBench: distinguish installed, built, loaded, handshaking, and
  observational states. Do not launch the game or expose live mutators during
  unattended work.

The Python dispatcher selects `skyrim-ae-research` when Conda is already
available and otherwise reports its system-Python fallback. Linux tests do not
establish Windows MO2/xEdit behavior or live AE behavior.
