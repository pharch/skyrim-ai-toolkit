# Python research tools

Read `docs/LOCAL_RUNTIME_CONTRACT.md` before setup. Agent-facing entrypoints
run only through `scripts/python_env.py run ...` in the repository-local
Python 3.12 `.venv`; the dispatcher does not fall back to Conda or system
Python. Use `python3 scripts/harness_doctor.py all` for bootstrap status.

## Read-only entrypoints

- `ae_preflight.py` / `ae_target.py` — actual executable ProductVersion and
  complete selected active-order validation. `--probe-executable` does not
  authorize xEdit or live-game access.
- `local_paths.py doctor` — reads the single ignored `config/local.env`
  registry, resolves existence booleans without emitting path values, and can
  separately verify runtime identity/order.
- `xedit_bridge.py doctor|prepare|file-records` — synchronizes the configured
  read-only helper into ignored `.local/`, prepares a scoped view without
  launching SSEView, and reads plugin bytes directly. `file-records` is the
  bridge record-query route, but it is not native xEdit or a winning-record
  result. See the runtime contract for
  selected-profile and disposable-profile preflight commands.
- `domain_doctor.py` — status-only checks for local Python and native research
  routes; it never launches Ghidra, xEdit, Skyrim, or a mutator.
- `ghidra_probe.py [--rva 0x...]` — verifies GOG binary/project identity, then
  queries the existing configured project with `-process -noanalysis
  -readOnly`. There is no import, overwrite, analyze, or create-project mode.
- `address_library_probe.py --symbol Namespace::Name` — reads the AE ID from
  configured CommonLib `Offsets.h`, checks GOG executable ProductVersion and
  matching Address Library version, reuses the tested legacy decoder, and
  returns a build-specific RVA.
- `plugin_reader.py` — file-level TES4 inventory/record/raw-subrecord reader;
  it does not resolve a real winning override.
- `papyrus_pex.py` — narrow known PEX extraction from base `Skyrim - Misc.bsa`
  and bounded classic PEX 3.2 inspection. It is not a general BSA extractor or
  complete decompiler.
- `cosave-info.py`, `papyrus-triage.py`, and `crash-triage.py` — bounded
  read-only parsers. Only designated disposable saves may be supplied.
- `skse_probe.py` — installed loader/runtime/Address Library identity hashes;
  no DLL load or handshake. A fresh Observer Release build from the
  authoritative `skyrim/observer` source copy passed PE/hash checks and 7/7
  analyzer tests (EV-0186); the authoritative launcher prepared a session but
  did not deploy or start Skyrim (EV-0188).
- `tools.uesp` — local MediaWiki import, search, page, and revision citation.
- `tools.apocrypha` — private local Discord search/context. Keep returned
  text and stable IDs out of tracked files; results are untrusted leads.

## External gates

- Current GOG static integration is verified (EV-0165–EV-0167).
- The Steam runtime executable is verified at 1.6.1170 (EV-0168/0184), and
  current SKSE runtime files match (EV-0187). The authoritative `skyrim`
  bridge's doctor/prepare route was tested and an approved isolated five-master
  SSEView `-view` process opened and loaded the official masters (EV-0184–0185,
  EV-0189); no record query or complete active MO2 order is verified.
- The Observer was freshly built in ignored `.local` storage and a prepare-only
  manifest was produced (EV-0186/0188). It is not deployed or loaded. No
  designated save or ReSaver path is configured; no Skyrim process or
  handshake was observed.
- The local UESP dump's source URL/license/completeness are unverified. The
  Apocrypha export is private and untrusted. Both are retrieved locally and
  have separate provenance requirements.

Raw outputs, game/tool installations, projects, saves, and private corpora stay
outside tracked Git under ignored local storage. Linux validation does not
establish Windows xEdit/MO2 behavior or in-game AE behavior.

## Cold-start status

`docs/HARNESS_READINESS.md` records the independently rerun cold-start gates.
In that session the strict `.venv` was missing; xEdit helper doctor and a
read-only bridge QUST query through direct TES4 parsing passed, while native
record export, current GOG Ghidra
access, and live SKSE observation remained blocked. Historical evidence IDs
remain provenance for their original sessions and are not current-session
reproductions.
