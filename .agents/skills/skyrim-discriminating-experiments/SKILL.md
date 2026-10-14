---
name: skyrim-discriminating-experiments
description: Design Ghidra, xEdit, SKSE, save-state and player tests that discriminate rival Skyrim glitch mechanisms, preserve raw evidence and do not confuse debug interventions with vanilla exploits.
---

# Skyrim AE experiment construction

Each `EXP-####` must provide: game/build/plugin version, experiment objective, competing hypotheses, predicted outcomes, observables, approved action surface, test save and rollback, minimal controls, instrument commands, data capture and result interpretation. If execution needs user input, record the whole protocol and mark item awaiting-user-data; continue other research.

Prefer measurements that separate multiple plausible mechanisms. Observe precise state transitions, numerical representations and timing where relevant. Treat float rounding and ULP claims as numerical hypotheses requiring raw binary representation tests, not decimal intuition. Use read-only tools by default. Capture empty/negative results with denominators and verified tool liveness. Do not rewrite observed results to match prior predictions.

For AE work, attach the verified runtime and active-profile identity to the
manifest. If either is unavailable, do not schedule an in-game action: write
the missing prerequisite and the offline discriminant into the frontier.

## Python routes and evidence

- Use `python3 scripts/python_env.py run tools/ghidra_probe.py` for native
  binary evidence, `tools/plugin_reader.py record` for one explicit plugin,
  `scripts/read-save.py` / `tools/cosave-info.py` for read-only save structure,
  and `scripts/validate_research.py` to verify durable links.
- Save experiment protocol and raw outputs under ignored `.local/`; cite EV
  IDs, executable/plugin hashes, exact measurements, lane, controls, and
  coverage in the experiment record. Do not expose personal save paths.
- Missing runtime/profile, failed tool invocation, dropped samples, or an
  unsupported parser path blocks the dependent experiment. Continue with an
  independent offline frontier item and keep interventions out of vanilla
  reproduction claims.
