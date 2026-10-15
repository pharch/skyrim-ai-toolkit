---
name: skyrim-discriminating-experiments
description: Design Ghidra, xEdit, SKSE, save-state and player tests that discriminate rival Skyrim glitch mechanisms, preserve raw evidence and do not confuse debug interventions with vanilla exploits.
---

# Skyrim AE experiment construction

The cold-start tool boundary is recorded in
../../../docs/HARNESS_READINESS.md. A staged Observer is not a live connection
or state capture; do not launch the game from a readiness or unattended run.

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

Each `EXP-####` must provide: game/build/plugin version, experiment objective, competing hypotheses, predicted outcomes, observables, approved action surface, test save and rollback, minimal controls, instrument commands, data capture and result interpretation. If execution needs user input, record the whole protocol and mark item awaiting-user-data; continue other research.

Prefer measurements that separate multiple plausible mechanisms. Observe precise state transitions, numerical representations and timing where relevant. Treat float rounding and ULP claims as numerical hypotheses requiring raw binary representation tests, not decimal intuition. Use read-only tools by default. Capture empty/negative results with denominators and verified tool liveness. Do not rewrite observed results to match prior predictions.

For AE work, attach the verified runtime and active-profile identity to the
manifest. If either is unavailable, do not schedule an in-game action: write
the missing prerequisite and the offline discriminant into the frontier.

The current Observer is a fresh Release build from an isolated authoritative
`skyrim/observer` source copy (EV-0186); its launcher has produced a verified
prepare-only manifest with the staged DLL and Steam 1.6.1170 identity (EV-0188).
It has not been deployed or loaded. The live instrumentation gate therefore
remains `NOT_VERIFIED`; require a complete disposable profile/save and reviewed
Observer deployment path before proposing an in-game run. Treat Observer data
as diagnostic-only, never as vanilla reproduction by itself.

## Python routes and evidence

- Use `python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]`
  to query the existing GOG project with analysis disabled and read-only mode.
  Resolve named relocations with `tools/address_library_probe.py --symbol
  Namespace::Name`; preserve the GOG build identity and never transfer its RVA
  to a different runtime without independent mapping. Use
  `tools/plugin_reader.py record` for one explicit plugin,
  `tools/cosave-info.py` for read-only save structure, and
  `scripts/validate_research.py` to verify durable links.
- Save experiment protocol and raw outputs under ignored `.local/`; cite EV
  IDs, executable/plugin hashes, exact measurements, lane, controls, and
  coverage in the experiment record. Do not expose personal save paths.
- Missing runtime/profile, failed tool invocation, dropped samples, or an
  unsupported parser path blocks the dependent experiment. Continue with an
  independent offline frontier item and keep interventions out of vanilla
  reproduction claims.
