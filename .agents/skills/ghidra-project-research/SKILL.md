---
name: ghidra-project-research
description: Query the existing GOG Skyrim AE Ghidra project for build-attested functions, xrefs, disassembly, and decompilation.
---

# Existing GOG Ghidra project research

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

Use this skill for static Skyrim AE code questions. The canonical local registry is ignored `config/local.env`. `GHIDRA_PROJECT_REP_PATH` must name the existing GOG `.rep` directory; the adapter verifies its adjacent `.gpr` and derives its project identity from this configured path. Native Windows queries that project directly. When WSL mounts the source read-only, set `GHIDRA_PROJECT_CACHE_WSL` in the ignored config to an absolute path on the WSL-native filesystem, outside `/mnt` and the checkout. The adapter verifies the source snapshot, copies only the existing project files there, and reuses that copy while source metadata is unchanged. This cache location avoids WSL-mounted project-lock failures; query outputs still go below ignored `.local/`. The adapter never creates a blank project, imports a binary, or reanalyzes it. The file binds three separate identities: the GOG `analysis_binary`, its existing `analysis_project`, and the runtime target used for record or live checks.
Never select Ghidra from `SKYRIM_EXE_PATH`; it may identify Steam or another
runtime build.

## Preconditions and query

1. Read `GHIDRA_ANALYSIS_EXE_GOG` ProductVersion and SHA through the adapter;
   require AE 1.6.318+ and the configured existing project/program files.
   The path must be outside this harness checkout.
2. For an exploratory project smoke query, run:

   ```text
   python3 scripts/python_env.py run tools/ghidra_probe.py
   ```

   The adapter invokes the configured existing project, or its WSL working
   copy sourced from it, with `-process SkyrimSE.exe -noanalysis -readOnly`.
   It does not offer import, overwrite, project creation, or full auto-analysis.
3. For a named CommonLib symbol, resolve its ID and build-matched GOG RVA first:

   ```text
   python3 scripts/python_env.py run tools/address_library_probe.py --symbol Namespace::Name
   python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xRVA
   ```

   The Address Library probe reuses the tested legacy decoder, checks the
   executable ProductVersion against the library's internal version, hashes
   the executable/library, and reports any unproven legacy-map disagreement.
   A returned RVA is scoped to that GOG executable build.

## Evidence and interpretation

- Keep metadata, stdout/stderr, Ghidra logs, and scripts under ignored
  `.local/ghidra/`. Cite the metadata artifact hash, executable version/hash,
  project alias/program, requested RVA when used, and each successful query
  component.
- Ghidra may refresh internal project index timestamp files while opening a
  working project. In WSL read-only-mount mode, those writes stay in the
  ignored working copy; the configured source project is never modified.
- Function names and nearby instructions do not establish gameplay meaning.
  Trace call/data flow, types, callers, and records; keep observations,
  hypotheses, and mechanism inferences distinct.
- Never transfer GOG addresses to a distinct runtime. Obtain independent
  runtime mapping evidence and record the generalization as a separate claim.
- EV-0167 is an integration example: GOG 1.6.1179.0, CommonLib
  `MagicItem::CalculateCost` AE ID 11321, RVA `0x14C020`; the existing project
  resolved a function, incoming call edge, disassembly, and decompilation.
  It validates the tool route only, not a game mechanic.

  Current cold-start status is in docs/HARNESS_READINESS.md. A returned RVA
  must come from a fresh Address Library probe in this session; stop when
  identity validation fails and do not run a remembered RVA.
