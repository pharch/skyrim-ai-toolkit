# Current harness state — 2026-10-15

## Mission result

Cold-start configuration and closeout verification are complete for the available WSL host, but the harness is not research-ready because the repository Python 3.12 environment cannot be created here. No bounty investigation was started. User-provided mission and bounty files remain intact; no migration files were deleted or staged.

## Readiness gates

- `STATIC_RESEARCH_READY`: BLOCKED_ENVIRONMENT — strict check reports `FAIL_VENV_MISSING`; WSL lacks ensurepip/pip and Windows process interop is unavailable.
- `NATIVE_RESEARCH_READY`: PARTIAL — EV-0201 blocks current Ghidra/xEdit dispatch before tool launch. The exact GOG `.rep`/`.gpr` binding is verified (EV-0199); no fresh function query or selected MO2 profile was verified.
- `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY`: NOT_VERIFIED — Observer is staged only; no deployment, game process, plugin load, handshake, event, or snapshot was observed.

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

## Exact next action: On the intended Windows host, create the Python 3.12 repository .venv and install requirements-dev.txt; pass check --strict, reproduce the verified GOG Address Library and read-only Ghidra query, then run the exact research-start validator. Do not begin bounty research before those gates pass.
Align AGENTS.md Python 3.12 repository-.venv instructions with docs/LOCAL_RUNTIME_CONTRACT.md, verify active Ghidra/xEdit/SKSE skill routes and local GOG project binding, then bootstrap and strictly validate the repository environment before the read-only Ghidra query.
- EV-0201: fresh strict-dispatch and consolidated-doctor results; 12 PASS, 7 BLOCKED_EXTERNAL, zero FAIL, exit 2.
