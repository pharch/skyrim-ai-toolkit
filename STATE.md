# Current harness state — 2026-10-15

## Setup result

The static research harness is ready for the next session. This session
implemented and tested the persistent bootstrap, verified the configured
GOG Ghidra and xEdit file-parser routes, and passed research-state validation.
No bounty investigation or game launch occurred. Setup and migration history
remains in `research/SESSION_LOG.md`, `research/EVIDENCE.json`, and the
historical handoff.

## Readiness gates

- `STATIC_RESEARCH_READY`: READY — persistent Python 3.12, strict dispatcher,
  current GOG Address Library mapping, existing-project Ghidra function/xref/
  disassembly/decompilation query, xEdit file-parser retrieval, and research
  state validate.
- `NATIVE_RESEARCH_READY`: PARTIAL — selected MO2 profile and full active order
  are `NOT_VERIFIED`; native SSEEdit export is `NOT_VERIFIED` and is not
  required for static research.
- `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY`: NOT_VERIFIED — no live SKSE
  connection, Observer load, handshake, event, snapshot, or DevBench connection
  was attempted. Live observation is not required for static research.

## Python environment

The current host is Ubuntu 24.04 / WSL2, CPython 3.12.3. Its persistent
environment is ignored `.local/python-envs/wsl`; `requirements.txt` is the
single complete pinned dependency specification. A cold disposable
environment was created, reused, and repaired after a pinned dependency was
removed. `python3 scripts/python_env.py check --strict` passes. Use the
bootstrap-first procedure in `docs/LOCAL_RUNTIME_CONTRACT.md`.

## Static tool evidence

- GOG `SkyrimSE.exe`: ProductVersion 1.6.1179.0; SHA-256
  `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
- Address Library: `MagicItem::CalculateCost` maps to GOG RVA `0x14C020`.
- Ghidra: query against the existing project configured by
  `GHIDRA_PROJECT_REP_PATH` passed program identity, function/RVA lookup, call
  xref, disassembly, and decompilation. Because the WSL project mount is
  read-only, the adapter queries a source-bound ignored copy; no import or
  reanalysis occurred.
- xEdit bridge: one QUST record returned from `Skyrim.esm` via direct TES4
  parsing. This does not establish a native xEdit query or winner.
- UESP and Apocrypha local index smoke checks passed. The latter remains private
  and untrusted input.
- SKSE installed file identity matches Steam AE 1.6.1170.0; live capabilities
  remain unverified.
- EV-0206 records the final 21-check consolidated doctor: 19 PASS, two
  BLOCKED_EXTERNAL, zero FAIL. Static research gates pass; the selected
  profile/native-export and live-observation gates remain separate.

## Research selection and exact next action

Recovery is idle and selects P0 frontier `Q-0001` / `OBJ-1`. The first deep
research session should read the current readiness report, run the bootstrap/
strict/state validation commands from `docs/RESEARCH_START_PROMPT.md`, then
begin `TX-0005` / `Q-0001` using that prompt's exact command. State rival gate
models before inspecting a quest source. Keep the selected MO2/full-order
limitation separate; do not make profile-specific winner or negative claims.

## Exact next action

At the start of the next research session, run
`python3 scripts/bootstrap_python.py`, strict Python check, and research-state
validation, then begin `TX-0005` / `Q-0001` with the command in
`docs/RESEARCH_START_PROMPT.md`.
