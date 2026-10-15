---
name: ghidra-project-research
description: Query the existing GOG Skyrim AE Ghidra project for build-attested functions, xrefs, disassembly, and decompilation.
---

# Existing GOG Ghidra project research

> Cold-start gate: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md) before invoking tools. Use the repository Python 3.12 .venv dispatcher only; there is no system-Python or Conda fallback. A blocked capability cannot support a negative finding.

Use this skill for static Skyrim AE code questions. `config/local.env` binds
three separate identities: the GOG `analysis_binary`, its existing
`analysis_project`, and the runtime target used for record or live checks.
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

   The adapter invokes the existing project with `-process SkyrimSE.exe
   -noanalysis -readOnly`. It does not offer import, overwrite, project
   creation, or full auto-analysis.
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
- Ghidra may refresh internal project index timestamp files when opening in
  read-only mode. Report that observed side effect. Do not restore or rewrite
  the original program database as part of a query.
- Function names and nearby instructions do not establish gameplay meaning.
  Trace call/data flow, types, callers, and records; keep observations,
  hypotheses, and mechanism inferences distinct.
- Never transfer GOG addresses to a distinct runtime. Obtain independent
  runtime mapping evidence and record the generalization as a separate claim.
- EV-0167 is an integration example: GOG 1.6.1179.0, CommonLib
  `MagicItem::CalculateCost` AE ID 11321, RVA `0x14C020`; the existing project
  resolved a function, incoming call edge, disassembly, and decompilation.
  It validates the tool route only, not a game mechanic.

  Current cold-start status is in docs/HARNESS_READINESS.md: the fresh GOG
  ProductVersion check failed through the WSL Windows bridge before Ghidra
  launched. EV-0165–EV-0167 are retained historical evidence, not a current
  query. Stop when identity validation fails; do not run a remembered RVA.
