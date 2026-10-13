# Migration progress

## Current state

In progress. The legacy repository and local guidance were reviewed. Codex
research guidance, AE target gates, a versioned evidence register, and initial
tool documentation are being implemented. No Skyrim runtime was accessed.

## Verified in this session

- Node AE target/load-order and winner argument tests: 21 passing (initial
  targeted run before later migration edits).
- Python AE profile path tests: 4 passing (initial targeted run).
- No real PE, xEditLib, MO2, DevBench, Skyrim, save, or in-game test.

## Remaining

1. Recover the authoritative `FINAL_SETUP_BRIEF.md` and transcribe its exact
   82 criteria before checklist completion.
2. Finish Codex skills and active Claude/non-AE/mod-authoring cleanup.
3. Replace CI and obsolete install/release/container docs with Codex-first
   repository validation.
4. Harden and test supervisor checkpoint/recovery and research-data validation.
5. Run the complete Linux suite, static checks, and second independent audit.
6. Perform Windows/AE local steps listed in `UNRESOLVED.md` when available.
