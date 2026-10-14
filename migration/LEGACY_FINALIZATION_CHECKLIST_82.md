> Historical 82-item checklist from the 2026-10-13 Copilot audit. Its former PASS labels are stale and are not evidence for the current audit. Current authority: [`LOCAL_SETUP_CHECKLIST.md`](LOCAL_SETUP_CHECKLIST.md), based on the 86-criterion session prompt.

# Finalization checklist

Source of truth: `migration/FINAL_SETUP_BRIEF.md`, Section 15. Criterion wording below is transcribed verbatim. Status and evidence are maintained per criterion; `TODO` is not a pass.

## Execution metadata

| Field | Value |
|---|---|
| Starting commit | `8b1c0f48d3c134b35e3d125aa3f9e7f6657bffa7` |
| Branch | `glitch-hunting-setup` |
| Initial worktree status | Clean relative to HEAD before this finalization; supplied brief was untracked |
| Date | 2026-10-13 |
| OS | Linux x86_64, Codespaces host |
| Toolchain | Node.js v20.20.2; npm 10.8.2; Python 3.11.15; pytest 9.0.2 |

## Hard external dependencies

| Dependency | Status here | Needed for | Local follow-up |
|---|---|---|---|
| Skyrim AE Windows host with installed `SkyrimSE.exe` | Unavailable | PE ProductVersion/hash and game runtime checks | Follow `docs/WINDOWS_AE_VERIFICATION.md` |
| Selected MO2 profile or verified stock active `plugins.txt` | Unavailable | Active effective load-order identity | Record profile path/hash and verify in MO2 |
| xEdit/xEditLib Windows DLL and registry mapping | Unavailable | Native record-winner integration | Run the documented positive/negative record smoke tests |
| SKSE and any runtime probes/DevBench | Unavailable | Live game observations | Verify exact compatibility and read-only identity before use |
| Disposable test save/profile | Unavailable | Authorized runtime experiments | Create separately; never use or overwrite the primary save |
| Ghidra and exact matching game executable | Unavailable | Build-matched native analysis | Record Ghidra version, executable hash, and mapping evidence |
| User-authorized UESP/Discord research inputs | No local corpus supplied | External-source retrieval/import | Use documented adapters; do not commit private Discord exports |

## A. Scope and preservation

- [ ] **A01** Target branch/commit and workspace status recorded. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **A02** Recursive tracked-file inventory completed; every active Markdown document reviewed. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **A03** Every old skill/doc/tool has an explicit disposition and destination. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **A04** Original technical facts, caveats, commands, failure examples and negative findings preserved with provenance. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **A05** Third-party licenses, source/attribution, and copyright requirements retained. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **A06** Historic instructions segregated and clearly non-authoritative; no active competing policies. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **A07** Pruning choices logged and no retained code depends on removed assets. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## B. Agent control

- [ ] **B01** `AGENTS.md` is concise, Codex-primary and aligned with project mission. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B02** `NORTH_STAR.md`, `ROADMAP.md`, `STATE.md`, research artifacts agree about priorities and current facts. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B03** `.codex/config.toml` parses and uses verified supported configuration keys. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B04** `.github/copilot-instructions.md` exists and is non-conflicting. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B05** No active Claude hook/skills or legacy placeholder guard blocks work. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B06** Clean interactive Codex startup instructions exist, with correct feature detection/fallback. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B07** No 45-minute kill/restart supervisor presented as the primary interface. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **B08** No hidden requirement to install into Skyrim's game folder. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## C. Skills

- [ ] **C01** All source `.claude/skills` audited and disposition recorded. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C02** All retained skills migrated into canonical discoverable Codex skill locations. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C03** Each research skill has real tool procedures, versions, outputs and evidentiary limits, not generic slogans. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C04** All skill YAML metadata validated against actual format. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C05** Skill references, scripts, links, and assets resolve. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C06** Irrelevant asset/VR/mod-authoring skills removed from active discovery. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C07** Quest gate and armor-XP skill workflows give actionable investigation/probe paths. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C08** Enchanting and persistent alchemy workflows are available as P1 skills/protocols. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C09** Static engine, Papyrus, xEdit, save, runtime-probe, experiment, evidence, and synthesis workflows are available and discoverable. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **C10** Skill-routing regression examples/tests pass. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## D. AE targeting

- [ ] **D01** Single explicit AE target config/source-of-truth implemented. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D02** Exact installed executable/runtime determination specified; no invented runtime support. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D03** `tools/skyrim_paths.py` audited/refactored and tested AE-only. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D04** `tools/xelib/active-plugins.js` audited/refactored and tested AE-only. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D05** `tools/devbench-cli.sh` and other wrappers audited; no incompatible fallback. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D06** MO2 virtual profile/load order awareness verified with fixtures. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D07** Wrong/incompatible versions fail closed rather than silently returning plausible data. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D08** Technical `SSE` naming exceptions documented; no active VR, LE, or pre-AE guidance. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **D09** Fake mixed-edition tests demonstrate rejection of incompatible installs. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## E. Toolchain

- [ ] **E01** Retained-tools registry contains actual invocations, versions, purpose, modes, and status. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E02** xEdit/xelib record inspection documented/tested read-only where possible. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E03** Papyrus/decompile/compile workflow documented with real preconditions and test status. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E04** Ghidra code-analysis workflow and version/address evidence protocol documented. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E05** Save/changeform/co-save analysis documented with fixtures where available. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E06** SKSE/runtime probe and DevBench capability status accurate; game-connected tests deferred honestly if unavailable. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E07** Log/crash/load-order/BSA or BA2 analysis capabilities retained where useful and tested where possible. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E08** Irrelevant asset-only programs no longer clutter active tools/install path. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **E09** Fresh cloud install/smoke-test instructions actually execute successfully. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## F. Safety

- [ ] **F01** Cloud, read-only local and disposable runtime experiment modes distinguished. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **F02** External game files/saves protected by enforceable path/mutation controls. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **F03** Default tool behavior read-only; explicit scoped consent for mutating probes. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **F04** Diagnostic state injection cannot be mislabeled vanilla exploit proof. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **F05** Safety tests include wrong paths, symlinks, unconfigured environment and unauthorized mutation. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **F06** Installation avoids automatic arbitrary external writes and risky upstream setup scripts. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## G. Research autonomy/state

- [ ] **G01** Frontier schema, statuses, transitions, unique IDs and links validated. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G02** Research transaction/experiment templates include predictions and raw evidence pointers. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G03** Claims, mechanisms, glitches, contradictions and exploit candidates have provenance/status discipline. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G04** Checkpoint/resume protocol exists and is testable across interrupted sessions. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G05** Completed/falsified investigations cannot vanish without trace. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G06** Every investigation closes with claim updates, successor generation and cross-system implications assessment. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G07** Blocked user test automatically allows selecting an independent frontier item. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G08** Repeated futile work is detected or explicitly handled. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G09** STATE remains compact with links to full evidence rather than a long transcript. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G10** Initial P0 research frontier is specific, tractable and factually scoped; no fabricated findings. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **G11** Offline fake/fixture lifecycle proves follow-up generation and interruption recovery. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## H. Grounding and integrations

- [ ] **H01** UESP lookup/indexing path documented, testable, and access/rights assumptions honest. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **H02** Discord archive ingestion prepared with provenance, privacy controls and a fixture. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **H03** Conflicting Fandom/UESP/community claims stay distinct, not flattened. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **H04** External text treated as untrusted evidence, not executable instructions. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **H05** Skyrim-MCP integration is a documented optional future stage, not falsely installed/merged. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## I. Documentation and CI

- [ ] **I01** README describes finished Codex glitch research, not an overlay/Claude toolkit. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I02** All active Markdown was second-pass reviewed for mod-building mission or other-edition guidance. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I03** Broken Markdown links, command examples, references and paths addressed. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I04** Codespaces static/cloud quickstart validated. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I05** Windows AE install/config guide complete and reproducible on user machine. **Status: BLOCKED_ENV** | Evidence: Linux cannot execute the real Windows AE runtime; follow [docs/WINDOWS_AE_VERIFICATION.md](../docs/WINDOWS_AE_VERIFICATION.md) for the exact Windows preflight and MO2/DevBench validation steps.
- **I05**: Windows AE runtime verification is environment-blocked in Linux because the actual `SkyrimSE.exe`, MO2 profile, xEditLib/registry, and DevBench installation are not available here; the required live checks must be executed on the user’s Windows AE machine.
- [ ] **I06** MO2/version/load-order safety documented accurately. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I07** CI checks research state, skill metadata, AE path fixtures, safety, source consistency, retained tools and tests. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I08** CI triggers on PR and appropriate branches; obsolete Claude/VR release/CI paths gone. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I09** All possible cloud tests pass; runtime-only tests marked `BLOCKED_ENV` with a follow-up guide. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I10** Final validation report includes actual commands, outputs/results, failures, environment and evidence. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I11** All migration records present, complete and non-template. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **I12** Last skeptical audit finds no contradictory active instructions or silent incompatible tool fallback. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.

## J. Final handoff

- [ ] **J01** New agent can start research by reading only canonical top-level state/instructions and select an actionable P0 frontier item. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **J02** All changes committed/reviewable, clear PR diff, no personal or copyrighted data accidentally introduced. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **J03** Final report distinguishes cloud/repo readiness from Windows/AE runtime verification. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **J04** `migration/RESUME.md` accurate and immediately useful even if migration was interrupted. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
- [ ] **J05** No required cloud-verifiable acceptance criterion remains `TODO`, `FAIL`, or improperly `BLOCKED_ENV` when claiming completion. **Status: PASS** | Evidence: Verified in the current repo by `python -m pytest -q`, `python scripts/validate_overlay.py`, and `python scripts/validate_research.py`; see the relevant docs/files in the checkout.
