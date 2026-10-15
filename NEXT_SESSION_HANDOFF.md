# Next session handoff — research ready

Static setup is complete. This session did not begin bounty research or launch
Skyrim. Read `docs/HARNESS_READINESS.md` for verified and unverified gates,
`docs/LOCAL_RUNTIME_CONTRACT.md` for canonical tool commands, and
`docs/RESEARCH_START_PROMPT.md` for the first transaction and research prompt.
Older setup attempts remain in `STATE.md`, `research/SESSION_LOG.md`, and
`docs/LOCAL_TOOL_HANDOFF.md` as history.

## Verified workflow

- The WSL2 Ubuntu 24.04 host uses CPython 3.12.3 in ignored
  `.local/python-envs/wsl`. All seven pins pass strict validation. EV-0203
  records creation from an absent environment, reuse, and missing-package
  repair without recreating the active environment.
- The configured GOG executable is ProductVersion 1.6.1179.0. The matching
  Address Library query resolved `MagicItem::CalculateCost` to RVA `0x14C020`;
  the existing configured GOG Ghidra project returned function, xref,
  disassembly, and decompilation in read-only/no-analysis mode (EV-0204).
- `tools/xedit_bridge.py file-records` remains the separate read-only TES4
  parser route (EV-0205). The native `native-query` route was also reproduced:
  SSEView 4.1.5f loaded only the five official masters and exported 149 fields
  for `dunDA14MorvunskarQST`, including the stage 100 shutdown flag (EV-0207).
  It requires the local xEdit bindings but no MO2 profile. Its winner is scoped
  to the five masters.
- UESP and private Apocrypha local retrieval passed (EV-0170, EV-0171).
  Research-state validation passed, recovery is idle, and `Q-0001` is next.

## Separate limits

- No selected MO2 profile/full order is configured. Profile-specific winners
  and negative claims require the target's actual complete order.
- SKSE installed file identity passes for Steam AE 1.6.1170.0. Live game,
  Observer load, handshake, event, snapshot, and DevBench capabilities remain
  unverified; they are not required for static research.
- The xEdit native operation ran from WSL through Windows PowerShell and
  launched the real configured SSEView application. That is evidence for this
  configured xEdit route and official-master scope, not for a live game or
  profile-specific load order.

## Start the research session

From the repository root on Linux/WSL:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
```

On native Windows, replace `python3` with `py -3.12`. Then read and paste the
**Initial Codex prompt** in `docs/RESEARCH_START_PROMPT.md`; it starts
`TX-0005` / `Q-0001` only in that new research session. Once strict Python,
research-state validation, GOG, and xEdit gates pass, proceed with the
frontier rather than repeating setup work.
