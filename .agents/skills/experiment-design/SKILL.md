---
name: skyrim-discriminating-experiments
description: Design Ghidra, xEdit, SKSE, save-state and player tests that discriminate rival Skyrim glitch mechanisms, preserve raw evidence and do not confuse debug interventions with vanilla exploits.
---

# Experiment construction

Each `EXP-####` must provide: game/build/plugin version, experiment objective, competing hypotheses, predicted outcomes, observables, approved action surface, test save and rollback, minimal controls, instrument commands, data capture and result interpretation. If execution needs user input, record the whole protocol and mark item awaiting-user-data; continue other research.

Prefer measurements that separate multiple plausible mechanisms. Observe precise state transitions, numerical representations and timing where relevant. Treat float rounding and ULP claims as numerical hypotheses requiring raw binary representation tests, not decimal intuition. Use read-only tools by default. Capture empty/negative results with denominators and verified tool liveness. Do not rewrite observed results to match prior predictions.
