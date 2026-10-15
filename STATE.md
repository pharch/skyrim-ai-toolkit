# Current harness state — 2026-10-15

## Mission result

Cold-start configuration and closeout verification are complete for the available WSL host, but the harness is not research-ready because the repository Python 3.12 environment cannot be created here. No bounty investigation was started. User-provided mission and bounty files remain intact; no migration files were deleted or staged.

## Readiness gates

- `STATIC_RESEARCH_READY`: BLOCKED_ENVIRONMENT — Python 3.12.3 is present, but this WSL installation lacks `ensurepip`/pip and cannot create `.venv`; the host diagnostic names `python3.12-venv`. The strict dispatcher fails closed.
- `NATIVE_RESEARCH_READY`: PARTIAL — the authoritative bridge `records` query returned one QUST through direct TES4 parsing; no native SSEView record-tree export or selected MO2 winner query ran. The explicit GHIDRA_PROJECT_REP_PATH binding matches the existing GOG project and adjacent .gpr. Its private path verification is in .local/ghidra/binding-verification.json. The documented query stopped at FAIL_VENV_MISSING before probe launch; earlier native diagnostics stopped at Windows ProductVersion interop.
- `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY`: NOT_VERIFIED — Observer is staged only. No deployment, game process, plugin load, handshake, event, or snapshot was observed.

## Final evidence

- EV-0192–EV-0194: helper/config route, source CLI, read-only QUST bridge query, and scoped five-master preparation.
- EV-0195–EV-0196: fresh native access blockers and Observer capability/stage boundary.
- EV-0197: Python 3.12 bootstrap/dependency reproduction; no packages installed.
- EV-0198: earlier doctor and offline source smoke tests; 176 tests ran with 3 dependency-gated skips. UESP revision and private Apocrypha summary-search smoke tests ran, but no Apocrypha context query.
- EV-0199: exact ignored Ghidra project binding and existing `.rep`/`.gpr` verification; no Ghidra query or project write.
- EV-0200: latest doctor has 19 checks (12 PASS, 7 BLOCKED_EXTERNAL, zero FAIL), overall BLOCKED/exit 2; 177 tests ran with 3 dependency-gated skips.
- Repository baseline at capture: branch `glitch-hunting-setup`, HEAD `1f49a48fe1825ca2180137a48a748eeebfd60f11`; 55 dirty entries before closeout artifacts, preserved without reset or staging.

## Ghidra project binding update — 2026-10-15

The ignored `config/local.env` now stores one explicit `GHIDRA_PROJECT_REP_PATH` for the user-specified existing GOG project. Its `.rep` directory and adjacent `.gpr` were verified; the Ghidra probe and local/domain doctors now consume this direct path. No Ghidra project access occurred. The documented Ghidra invocation stopped at `FAIL_VENV_MISSING` before probe launch. The full unittest suite passed: 177 tests, 3 dependency-gated skips. Strict Python check reports valid config and missing repository `.venv`. The first consolidated doctor rerun exposed a stale Markdown inventory; after refreshing it, the final doctor reports config/path/domain/Markdown checks PASS, Python environment BLOCKED_EXTERNAL (`FAIL_VENV_MISSING`), native probes BLOCKED_EXTERNAL, and no FAIL checks; verdict BLOCKED, exit 2.

## Exact next action
On a host with Python 3.12 plus venv/ensurepip and pip, follow docs/LOCAL_RUNTIME_CONTRACT.md to create .venv and install the pinned requirements; run the strict check and consolidated doctor, then reproduce the read-only GOG Ghidra query and Windows-native xEdit gates. Do not begin bounty research until the strict research environment is ready.
