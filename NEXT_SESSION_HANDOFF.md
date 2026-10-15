# Next session handoff — research ready

Setup is complete; no bounty investigation started in this session. Read
`docs/HARNESS_READINESS.md` for separate capability gates and
`docs/LOCAL_RUNTIME_CONTRACT.md` for the one Python bootstrap/dispatch route.
Earlier tool records in `docs/LOCAL_TOOL_HANDOFF.md` are historical.

## Verified static workflow

- WSL2 Ubuntu 24.04 / CPython 3.12.3 uses the persistent ignored environment
  `.local/python-envs/wsl`. Its seven pinned distributions pass strict check.
- Bootstrap from an absent test path created and installed the environment;
  the second call reused it; a deliberately removed `pytest==8.0.0` was
  repaired in place. Captures are under ignored
  `.local/alignment/python-bootstrap-final/`.
- The configured GOG executable is ProductVersion 1.6.1179.0. The fresh
  Address Library probe mapped `MagicItem::CalculateCost` to GOG RVA
  `0x14C020`; the existing GOG Ghidra query returned function, caller xref,
  disassembly, and decompilation. The read-only WSL source mount required an
  ignored `.local/ghidra/project-cache/` copy sourced from
  `GHIDRA_PROJECT_REP_PATH`. No binary import or reanalysis occurred.
- The documented `xedit_bridge.py file-records` route returned one QUST record
  from `Skyrim.esm` through the direct TES4 parser. This is not native SSEEdit
  or a winning-record result. UESP and Apocrypha local database smoke checks
  passed. Research-state validation passed.

## Separate unverified gates

- The selected MO2 profile and complete active order are not configured.
  Profile-specific winners and negative findings remain unsupported until the
  selected profile's explicit `plugins.txt` is validated.
- Native SSEEdit record-tree export is not verified and is not required for
  static research.
- Installed SKSE files match the Steam AE 1.6.1170.0 file set. No game process,
  Observer load, handshake, event, snapshot, or DevBench connection was tested.
  Live SKSE is not required for static research.
- Linux/WSL validation does not establish Windows MO2/xEdit or in-game AE
  behavior.

## Bootstrap and research start

From the repository root on Linux/WSL:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/setup_research.py init
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
```

Then paste the **Initial Codex prompt** in `docs/RESEARCH_START_PROMPT.md`.
It begins `TX-0005` / `Q-0001` only after that session confirms the gates. The
same document provides the exact `research_state.py begin` command. After
strict Python, state validation, and static-tool checks pass, proceed with the
frontier rather than continuing setup work.
