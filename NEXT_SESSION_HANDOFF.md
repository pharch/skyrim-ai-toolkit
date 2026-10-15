# Next session handoff — setup status

This is a setup handoff only; no bounty investigation started. Read
`docs/HARNESS_READINESS.md` for the separate readiness gates and
`docs/LOCAL_RUNTIME_CONTRACT.md` for the active setup and invocation
procedure. Earlier rows in `docs/LOCAL_TOOL_HANDOFF.md` are historical.

## Current host blocker

The active shell is Ubuntu 24.04 under WSL2 with CPython 3.12.3. It lacks
`ensurepip` and pip. Installing the documented `python3.12-venv` package
requires an unavailable sudo password. Windows `py.exe` and PowerShell fail
at startup with `UtilBindVsockAnyPort:307`. The incomplete WSL-created
`.venv` was removed. The current strict status is `FAIL_VENV_MISSING`; do
not use system Python, Conda, or an ambient environment to run research tools.
The captured outputs are under
`.local/alignment/research-start-cold-start-20261015/`.

The consolidated doctor’s research-state check passes, but its overall verdict
is BLOCKED because the strict Python, GOG, xEdit, and SKSE identity routes did
not launch. The GOG project binding itself is valid: the configured existing
GOG `.rep` and adjacent `.gpr` exist. No fresh Ghidra query or xEdit record
retrieval was produced.

## Separate external gates

- `MO2_PROFILE_DIR` and `PLUGINS_TXT` are unset. The selected profile and
  complete order are NOT_VERIFIED; this remains a blocker for profile-level
  winner results and negative findings.
- Native SSEEdit record export is not required to start static research.
- SKSE identity and live connection/observation remain NOT_VERIFIED. A prior
  successful build or staged Observer DLL is not a connection, plugin load,
  handshake, or state observation. Live SKSE is not required for static
  research.

## Exact start command after the setup gates pass

In Windows PowerShell, from the repository root:

    & .\.venv\Scripts\python.exe scripts/python_env.py run scripts/research_state.py validate

On Linux/WSL, after that host’s repository `.venv` passes the strict check:

    python3 scripts/python_env.py run scripts/research_state.py validate

Start only after the strict Python environment and the configured GOG
function/xref/decompilation query pass. Then copy the exact initial prompt from
`docs/RESEARCH_START_PROMPT.md`. It selects P0 OBJ-1/Q-0001 and its rival
models. Recovery is idle and `next_frontier_id` is Q-0001; there is no active
research transaction.
