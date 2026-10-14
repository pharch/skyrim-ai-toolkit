# Pre-push setup summary

Date: 2026-10-14

## Reviewer status

**Readiness: `READY_FOR_STATIC_RESEARCH`.** The Windows/AE runtime lab and deep
autonomous continuity pilot are not ready. Agent skills and active tools use
Python. Current setup and per-domain capability are summarized below; the
authoritative 86-item ledger is [`LOCAL_SETUP_CHECKLIST.md`](LOCAL_SETUP_CHECKLIST.md).

Branch: `glitch-hunting-setup`. HEAD before these local changes:
`146ef076a5cf91e00fa7a0aed29dde0c8a747aed`.

| Area | Status |
|---|---|
| Checklist | 62 PASS, 24 BLOCKED_EXTERNAL, 0 TODO/IN_PROGRESS/FAIL |
| Legacy migration gates | G01 is blocked because the old checkout's Git metadata is empty; G10 is blocked because native Ghidra/SKSE/xEdit/CommonLib procedures could not all be exercised in this shell. The other 10 G criteria pass. |
| Python tool surface | Active `tools/` and `scripts/` entrypoints are Python; old Node/shell/Java launchers and Node lockfile are archived under `archived_tools/legacy_nonpython/`. |
| Conda environment | `environment.yml` defines `skyrim-ae-research` with Python 3.12 and test/tool dependencies. Dispatcher uses `conda run` when present. Conda is absent in this shell; system Python 3.12.3 fallback was used. |
| Focused tests | 31 standard-library tests pass; research validator and synthetic Papyrus/crash CLI probes pass. Full pytest suite was not run because pytest/Conda are unavailable. |
| SKSE | Python co-save parser responds on a synthetic fixture (one chunk, full fixture coverage); no real co-save or live handshake. |
| Ghidra | Doctor responds; candidate paths exist; blocked because Java is unavailable; no analysis run. |
| CommonLibSSE | Doctor responds; source/CMake project candidate exists; blocked because CMake is unavailable; no build run. |
| SSEEdit | Doctor responds; executable candidate exists; blocked by Linux host and unverified ProductVersion/full profile order; no xEdit call. |
| UESP | Local doctor/search/page respond; 475,228 pages, 17,520 Skyrim namespace pages, sample revision 3629292. Source provenance/license/completeness unverified. |
| Apocrypha | Local aggregate doctor/search respond; 60,873 messages match the declared count; private fields were suppressed. |

## Artifact and ignore audit

Final result: **PASS** `python3 scripts/pre_push_audit.py` (2026-10-14).

The audit found 0 tracked raw artifacts, 0 tracked files at or above 5 MiB,
and 0 unignored untracked raw artifacts. All 11 synthetic ignore probes
passed. Two ignored local SQLite databases total 2,498.9 MiB; the audit emits
only aggregate counts and types, not local paths or names.

The audit reports only aggregate local corpus counts/types and checks that
`session_prompt.md`, local config, raw/log/export/capture/dump paths, game
saves/co-saves, wiki/Discord exports, database files, and compressed archives
are ignored. Local UESP/Apocrypha databases remain in `.local/`, outside Git.
The audit found no compressed source archive there. Research results are
summarized in Markdown/JSON; no raw runtime result is claimed.

## First-use blockers

- Configure the selected Windows AE executable and explicit full MO2 `plugins.txt`,
  then run `python3 scripts/python_env.py run tools/ae_preflight.py`.
- Install the Conda environment with `conda env create -f environment.yml` to
  enable the complete pytest suite and the named environment for agent tools.
- Verify Ghidra/Java, CommonLib/CMake, and SSEEdit behavior only after the AE
  target/order gate passes. Linux doctor output is readiness metadata, not a
  native-tool run.
- UESP acquisition/license/completeness and the fresh-context/forced-resume
  pilot remain unverified.

No commit or push was made. The user will perform those actions after review.
