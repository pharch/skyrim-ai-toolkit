# FINAL HARNESS CLOSEOUT MISSION — Skyrim AE Glitch Research

> **Role:** You are the final configuration and verification agent, not the long-running research agent.
>
> **Target:** This checkout of `pharch/skyrim-ai-toolkit`, on the user's intended branch.
>
> **Authority:** This mission takes precedence over obsolete migration instructions. Existing `AGENTS.md`, active skills, safety policies, and protected-data rules continue to apply unless explicitly revised here.
>
> **End state:** A portable, Codex-native research harness whose local prerequisites are documented, whose tool routes are reproducible, whose research state is internally consistent, and whose readiness is demonstrated by evidence rather than optimistic prose. End with one concise current readiness report and a ready-to-use research bounty. **Do not start open-ended exploit research in this setup session.**

## 0. User intent and invariants

The user has a **previously working** local repository at `C:\Users\matth\Documents\GitHub\skyrim`. This is the authoritative source for the tested xEdit bridge, GOG Ghidra project and paths, CommonLibSSE, SKSE probes, Apocrypha export, and legacy research knowledge. **Inspect it read-only. Do not rebuild, replace, relocate, or update its installations or Ghidra program.** Reuse existing working configurations rather than inventing another integration stack.

The public GitHub repository is **only the portable harness**: instructions, skills, adapters, tests, research knowledge and source metadata. Keep absolute local paths, raw dumps, binaries, private Discord text, user saves, `.env`, credentials, compiled DLLs, and Ghidra project data untracked and ignored. Do not print sensitive path values in public reports.

**Static analysis binary:** the already analyzed **GOG AE 1.6.1179.0** `SkyrimSE.exe` in the existing Ghidra project. Its identity and GOG-specific addresses must remain separate from **live Steam AE 1.6.1170.0** (or any runtime actually detected locally). Do not substitute a fresh Steam analysis or cross-apply RVA/function IDs without mapping evidence. AE only; `SkyrimSE.exe`/`SSEEdit` are legitimate technical names.

**Safety:** read-only by default. Never mutate the original game, load order, master/plugin files, original saves/co-saves, or Ghidra project. In-game writes, deployment, user saves, stage changes, and console mutations require an explicitly selected disposable profile/save and approval. Diagnostic forcing is **not** proof of a vanilla exploit. Do not silently run the game for an instrumented test.

## 1. How you must work

1. Record the current branch, HEAD, working tree and local capability paths (path values only in ignored local logs). Do not overwrite existing user edits. Reconcile the recent `migration/FINAL_ALIGNMENT_REPORT.md`, `FINAL_ALIGNMENT_CHECKLIST.md`, `FINAL_ALIGNMENT_CHANGES.md`, current `AGENTS.md`, `protocols/TOOL_ROUTING.md`, `config/local.env.example`, all relevant skills, `environment.yml`, `requirements*.txt`, `scripts/python_env.py`, `scripts/research_state.py`, and the original `skyrim` repo's proven tooling instructions.
2. Create `migration/FINAL_CLOSEOUT_CHECKLIST.md` with every item from the acceptance checklist below, statuses `PASS`, `FAIL_FIXABLE`, `BLOCKED_EXTERNAL`, or `NOT_APPLICABLE`, an evidence file/command and a short result. Never mark PASS because a script exists or because a previous report claims success.
3. Fix and retest independently actionable failures. After a blocked action, pivot immediately to another item; never stop with a generic progress summary. Save durable progress in `migration/FINAL_CLOSEOUT_PROGRESS.md` if interrupted. Do not pretend platform execution limits can be overridden by instructions.
4. Use the original tested bridge where possible. **Do not write a new xEdit implementation, new SKSE framework, or a generic tool-management architecture** unless a concrete missing interface requires a minimal adapter.
5. Once complete, prepare `docs/LOCAL_RUNTIME_CONTRACT.md` (the one short source of truth for this machine's prerequisites and commands) and `docs/HARNESS_READINESS.md` (current verdict with evidence IDs). Reconcile references in active docs and skills to these files. End the session without branching into open-ended Skyrim research.

## 2. Priority repair: make the xEdit bridge a reproducible harness feature

The previous report established: authoritative xEdit helper/config replay; SSEView launch; five-master load; **no record query/export and no selected active MO2 profile**. Do not upgrade that claim silently.

- Locate the original bridge's tested entrypoint (`scripts/skyrim_tool.py` and any companions, if those are in fact the source) and read its invocation contracts, config schema, process lifecycle, output format and read-only guarantees. Determine if the current harness links to an **ignored local copy** or the **authoritative source path**. Both can be valid if documented; the requirement is that a fresh Codex session reads local config and invokes the same bridge reliably.
- Build a canonical tool registry/route that explicitly names the local configuration keys, dependency versions/hashes, exact working example commands, how to obtain structured output, output destination, timeout, process shutdown, and difference between a scoped five-master list and an actual selected MO2 load order.
- Ensure no competing old xeditlib route is presented as the default. The original `skyrim` bridge is primary. Python is allowed to invoke a PowerShell, native SSEEdit, or other proven subprocess; **a Python entrypoint does not imply the underlying tool must be rewritten in Python**.
- Test at least one real, **read-only QUST record retrieval/export** through the bridge on a known official master in an isolated, explicitly labeled vanilla-five-master session, if the bridge supports such a query. Record exact signature/FormID/plugin, observed fields, path to redacted evidence, and completed-process status. If no such interface exists, distinguish "five masters loaded" from "record query working" and identify the smallest viable, testable read-only export path. Do not interact with invisible UI controls by blind keystrokes.
- For real winning-record claims, separately configure the selected MO2 profile and its complete, ordered `plugins.txt`; verify light-plugin/FE handling, Creation Club data where applicable, required masters and resolved files. If the user has not identified the selected profile, mark full-winner mode **BLOCKED_EXTERNAL** with one exact missing input; do not substitute the scoped list or global AppData file.
- Add a regression test proving fresh process startup from local config and a negative test where the profile is missing/wrong. The agent must never declare a profile-dependent negative finding from partial data.

## 3. Priority repair: be precise about SKSE and live-game access

- Audit `scripts/skyrim_tool.py`/existing Observer, SKSE-related skills, reports and config keys, from the *original* repo and new harness. Produce a capability table separating: (i) installed components, (ii) compiled DLL, (iii) staged/deployed DLL, (iv) running AE process, (v) successful read-only handshake, (vi) actual field/event snapshot, (vii) state-mutating actions.
- The existing Observer build/test/prepare-only manifest is **not** a live SKSE handshake. A headless tool need not display its own UI, but the real game process is required for live native engine observations. Explain what executable/process, log, endpoint or artifact definitively proves handshake.
- Keep mutation disabled by default and guard deployment/profile/save selection. If a safe disposable profile is already explicitly designated **and** approval is available, run one minimal real read-only capture with a before/after or timestamp, game/runtime/DLL hashes, event/AV field names, log location and shutdown. Otherwise do not launch or deploy; record a precise, non-blocking runtime prerequisite and verify all read-only offline parts.
- Do not label Observer compilation, a synthetic analyzer fixture, or preparation manifest as in-game telemetry. Ensure active README/skills use the same status words as the report.

## 4. One predictable Python environment (mandatory)

Current risk: `environment.yml` provides Conda, `requirements.txt` is partially described as container-side, `python_env.py` allows a system-Python fallback, and the latest report says `read-save.py --help` fails due to missing `lz4`. This creates repeated uncertainty and false readiness.

**Choose and implement one primary Windows setup: `.venv` created by Python 3.12, with pinned `requirements.txt` (and `requirements-dev.txt` only if useful).** Conda may remain historical/optional, but must not be the active default. Do not require Conda to run research. Do not force reinstallation of Ghidra, Java, CommonLib, xEdit, SKSE, Node, or system DLLs through pip. External binaries are prerequisites bound through ignored local config.

At a minimum, make these commands actually work in PowerShell from the repo root (adapt only if verified necessary):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/python_env.py check --strict
```

Audit imports of **all active Python scripts, tests and skills**, not merely the direct dependencies listed in a previous manifest; include `lz4` and any genuine Windows-only packages if needed. Pin versions to a verified compatible set. Use CI fixtures where real data cannot be committed. Test `read-save.py --help` and at least one permitted save parsing path against a fixture or designated disposable copy; it must no longer die during import.

Change the dispatcher to use `.venv` (or the current interpreter only if it is explicitly that environment) and **fail closed** for research tool execution if the environment is absent or incomplete. No accidental system Python fallback reported as ready. `check --strict` must verify interpreter path, Python version, full import set, package versions as needed, active config file, and distinguish a Python dependency failure from an external executable/data prerequisite. Add tests for wrong interpreter, absent `lz4`, missing package, malformed config and successful configured launch. Use `.venv\Scripts\python.exe` in Windows examples; do not assume `python3` is a Windows command.

The user may install this venv during setup; **research sessions must never install, upgrade, search for, or guess dependencies.** On missing prerequisites, emit one actionable failure that refers to the documented prerequisite, then move to independent research if possible.

## 5. Single authoritative local configuration contract

Keep `config/local.env` the only active machine-specific binding, with a faithful tracked `config/local.env.example`. Reconcile actual keys from code, original bridge and active documentation; do not invent aliases unless necessary. Explicitly mark each key `required for static`, `required for xEdit`, `required for live`, `optional`, or `deprecated` and document expected path kind, executable identity/version/hash and validation command.

The audit must account for at least these areas, using real names discovered in the repo:

- original `LEGACY_SKYRIM_REPO`; GOG Ghidra headless executable, existing project folder/name/program and GOG analysis executable;
- `JAVA_HOME`, CommonLibSSE root, matching Address Library and build toolchain where used;
- **authoritative xEdit bridge location**, Python entrypoint/helper scripts, SSEEdit executable, Edit Scripts, game Data path, isolated bridge session directory, MO2 instance/profile and selected `plugins.txt`;
- Steam AE live executable/root, `SKSE_LOADER`, Observer staged/deployed DLL and expected hashes, permitted disposable profile/plugin list/save, DevBench (only if used);
- UESP index/source provenance, Apocrypha index and private export;
- raw capture root; read-only policy, test-output paths and tool permissions.

Ensure aliases such as `PLUGINS_TXT` versus `SKYRIM_PLUGIN_LIST` have unambiguous and *different* semantics or converge safely. Reject conflicting assignments; do not auto-detect an arbitrary MO2 profile. Every active skill must reference this configuration contract rather than independently guessing paths. Validate `git check-ignore` and staged changes against accidental private-path/raw-data leakage.

Implement an **unambiguous readiness command** (`scripts/harness_doctor.py` or equivalent) with named capability modes such as `static`, `records`, `live` and `all`; exit nonzero for any failed **required** check for that mode, yet report other modes independently. It should actually execute cheap tool smoke tests, not merely inspect `Path.exists`. Its JSON output should identify `PASS`, `FAIL`, `BLOCKED_EXTERNAL`, tests executed, and evidence artifacts, with local paths redacted. Runtime launch or mutating probe must never happen implicitly in a doctor. `all` must not be described as passing if live is unverified.

## 6. Research data, handoff and correctness audit

- Confirm canonical import of old `skyrim` research: previous claims, exact float32/ULP arithmetic, poison resistance, armor/Block XP, level gates, alchemy, ActiveEffects, negative results, contradiction history, probe and Ghidra provenance. Validate hashes and path aliases rather than rereading everything by default.
- Test real UESP and Apocrypha queries with source identity/revision/message context; unknown UESP dump completeness/license remains **unknown** (not "complete"). Preserve raw private content outside Git.
- Validate `CLAIMS`, `MECHANISMS`, `KNOWLEDGE_GRAPH`, `EVIDENCE`, `FRONTIER`, `RECOVERY` and `SESSION_LOG` consistency. Ensure no stale recovery transaction pretends setup is ongoing, and `STATE.md` stays short/current. Keep experiment IDs, raw artifact hashes, build identity, discriminating outcomes and contradicting evidence.
- Verify the harness supports BOTH targeted competing-hypothesis testing AND deliberate low-frequency breadth exploration. Periodic synthesis should spawn concrete, falsifiable frontier items instead of repeating summaries; queue user tests and reselect an independent tractable item rather than pausing the entire research program.
- Demonstrate one isolated research-state transaction/update/complete (or block/reselect), fresh-process recovery, and integrity validator run without contaminating the canonical real frontier with synthetic findings. Verify the selected next action and cross-domain links survive interruption.
- Preserve the priority hierarchy (P0 level-gated quests/events; P0 armor without hit-earned skill XP; P1 minimal-XP enchanting; P1 permanent alchemical effects). Diagnostic console or mutated-plugin results must never be scored as vanilla success.
- Confirm `docs/RESEARCH_START_PROMPT.md` references a **bounty file** as the task input, while operating methodology remains in `AGENTS.md`/skills. A bounty selects what to investigate, not a competing alternate workflow.

## 7. What `research_state.py validate` does and does not prove

Execute the command via the **verified** `.venv` interpreter:

```powershell
.\.venv\Scripts\python.exe scripts/research_state.py validate
```

Read the implementation, preserve its CLI behavior, and explain in `docs/LOCAL_RUNTIME_CONTRACT.md` that it checks research-frontier / evidence-reference / recovery-state consistency and exits nonzero on structural inconsistencies. It does **not** validate local binaries, Conda/venv completeness, deployed SKSE, xEdit record retrieval, selected profile, GOG project availability, privacy, or the epistemic truth of a claim. Accordingly, do not present this command alone as "harness ready." Integrate it as one component of the doctor/test readiness suite.

## 8. Migration-folder cleanup plan (do not prematurely delete)

`migration/` now contains extensive one-off setup briefs, reports, progress files, source maps and validation snapshots. Preserve all tracked history during this session, but create `docs/MIGRATION_RETIREMENT_PLAN.md` with a **file-by-file classification**:

1. `ACTIVE_DEPENDENCY`: still referenced by an active skill/adapter/test (must migrate the required facts elsewhere first).
2. `PROVENANCE`: source map, hashes, evidentiary material needed to interpret canonical research (retain concise canonical version elsewhere).
3. `HISTORICAL_ONLY`: old briefs, superseded reports, interim checklists, setups and debugging discussions (eligible for Git removal once final gates pass).
4. `DO_NOT_TOUCH`: unrelated user-added material or files that require explicit review.

Remove *references* from startup/AGENTS/skills/tests to historical setup documents. Copy critical provenance into `research/` or `references/` before pruning. Keep the original history retrievable in Git. **Do not actually prune `migration/` in this session unless all preconditions pass and the user has clearly authorized the specific deletions**; provide a preview (`git ls-files migration/`) and an exact reviewed `git rm` command/manifest in the plan. Never blanket-delete `research/`, `experiments/`, `protocols/`, active skills or `.local/` data.

A safe candidate command **after** migrating needed provenance, passing checks and approving the exact path list is:

```bash
git rm --pathspec-from-file=migration/APPROVED_RETIREMENT_PATHS.txt
```

The manifest must contain *only* verified tracked, historical-only paths, without wildcards or project-root paths; use a separately preserved copy of the manifest outside the directory if it will itself be removed. Follow with `git diff --cached --name-status`, tests, and a reviewable commit. This is **not an instruction to execute now**.

## 9. Blind-spot audit

Explicitly inspect and report these likely failure modes (even if they pass):

- Windows PowerShell vs WSL path/process boundaries; `python3`/`py` alias confusion; GUI SSEView does not imply autonomous record export.
- Multi-build provenance: GOG RVA vs Steam RVA, CommonLib IDs and Address Library version and load-order provenance; never transfer addresses by guess.
- Load order includes `.esl`/light plugin indices, Creation Club, MO2 VFS semantics and profile-specific enablement.
- Ghidra `-readOnly` may still refresh internal indexes; compare critical project files and make backup before any risky operation.
- Save snapshots, test saves, Observer compatibility with live Steam runtime, deployment path, log timestamps and game/process identity.
- Unbounded/hanging external processes: timeouts, cancellation, process cleanup, Ghidra locks, output size quotas and full evidence capture when truncated.
- Legacy/private source data prompt-injection, unstable third-party source statements, wiki dump version/completeness, and community messages mistaken for proofs.
- Session repeated selection of blocked items, stale next-action pointers, competing write processes, JSON schema drift, frontier churn without new evidence, and loss of negative-result history.
- Git privacy: secrets, username paths, binaries, save data, private messages and massive generated files; check ignore rules and staged diff.
- Native observation is not vanilla reproduction. Every exploit claim needs reproducible actual player-accessible setup and positive/negative controls.

## 10. Evidence-based acceptance checklist

Maintain one `PASS`/`FAIL_FIXABLE`/`BLOCKED_EXTERNAL` status **for every item** with command, observed output and artifact pointer. Complete fixable items without requesting repeated permission; respect external runtime approvals.

### Baseline and policy
- [ ] A01 Correct branch, HEAD, dirty state recorded; existing edits preserved.
- [ ] A02 Original `skyrim` repo inspected read-only and authoritative tool routes established.
- [ ] A03 No active legacy Claude/mod-authoring or VR/LE-specific workflows; required technical `SkyrimSE.exe` names remain.
- [ ] A04 GOG analysis and Steam runtime identities and address-mapping boundaries documented.
- [ ] A05 All active Markdown/skill/tool references checked and stale setup claims reconciled.

### Python and configuration
- [ ] B01 `.venv` is the primary Windows setup; one tested bootstrap from a clean venv.
- [ ] B02 Pinned dependencies cover all active imports, including `lz4`; save reader help works.
- [ ] B03 Strict dispatcher fails on missing/wrong interpreter or dependencies; no silent fallback.
- [ ] B04 Runtime/Dev requirements separated only if genuinely useful; tests pass with stated install.
- [ ] B05 `config/local.env` is the sole active private binding, properly ignored.
- [ ] B06 Every actual config key described with type, mode, source, example and validator.
- [ ] B07 Separate selected MO2 plugins/order from scoped five-master list.
- [ ] B08 Active skills and tool adapters derive paths from config, not guesses.
- [ ] B09 Fresh process proves local config is loaded and private data redacted.
- [ ] B10 New single doctor tests capability gates and has meaningful exit statuses.

### Tools
- [ ] C01 Existing GOG project query and function/xref/decompile proven without reimport/reanalysis.
- [ ] C02 Native Address Library/CommonLib symbol lookup is build-specific and tested.
- [ ] C03 Original xEdit bridge's precise entrypoint and private config are reproducible.
- [ ] C04 Scoped five-master load is accurately labeled, and one actual real read-only record query succeeds or is separately blocked with exact missing interface.
- [ ] C05 Full MO2 selected-order winner mode either passes an actual query or is explicitly blocked on exact input.
- [ ] C06 xEdit failure/timeout/cleanup/read-only behavior tested.
- [ ] C07 Papyrus/BSA and known PEX extraction/analysis demonstrated.
- [ ] C08 Save/co-save tool import and fixture read pass; real disposable save readiness classified.
- [ ] C09 Observer compile/stage/runtime/load/handshake stages honestly separated.
- [ ] C10 Real read-only handshake/snapshot, if safely authorized, or precise external blocker with no invented event data.
- [ ] C11 Tool/skill routing includes working commands and version/provenance/output caveats.

### Knowledge and ongoing research
- [ ] D01 Legacy claim and evidence aliases resolve with hashes where possible.
- [ ] D02 UESP actual index and page/revision query pass; dump provenance caveat maintained.
- [ ] D03 Private Apocrypha context query passes and privacy preserved.
- [ ] D04 Claims, graph, hypotheses, contradictions and frontier references pass validation.
- [ ] D05 `STATE.md`/`RECOVERY.json` have one current next action, no stale setup boundary.
- [ ] D06 Controlled begin/update/complete or block/reselect and fresh-process recovery pass.
- [ ] D07 Cross-domain synthesis and periodic exploration are active, with falsifiable successor questions.
- [ ] D08 First research bounty can be supplied without re-specifying entire methodology.

### Cleanup and final gate
- [ ] E01 Migration folder fully inventoried and classified by retention reason.
- [ ] E02 Active docs no longer depend on historical migration reports.
- [ ] E03 A reviewable *non-executed* retirement path manifest and command exist.
- [ ] E04 Tests, validators, CLI help, skill metadata, Markdown links and Windows/CI smoke gates pass.
- [ ] E05 Git ignore/diff audit proves no private or heavyweight content staged.
- [ ] E06 `docs/LOCAL_RUNTIME_CONTRACT.md` includes precise commands and scope of `research_state.py validate`.
- [ ] E07 `docs/HARNESS_READINESS.md` gives independent static / xEdit-native / live statuses with evidence.
- [ ] E08 Handoff includes the exact single first research-session invocation and tested bounty path.

## 11. Exit criteria

Finish the **setup work** when all locally fixable criteria are PASS and each external blocker has exactly one minimal, specific dependency and a tested future check. **Do not lie about fully verified live research.** The setup may be complete with `STATIC_READY`, `RECORDS_BLOCKED_PROFILE`, or `LIVE_BLOCKED_TEST_SAVE` explicitly stated; the user must be able to start the available static program without confusion.

Produce:
1. `docs/LOCAL_RUNTIME_CONTRACT.md` — one local setup/environment/tool command map;
2. `docs/HARNESS_READINESS.md` — actionable one-page status for next Codex session;
3. `migration/FINAL_CLOSEOUT_CHECKLIST.md` and `migration/FINAL_CLOSEOUT_PROGRESS.md` — criterion-specific audit history;
4. `docs/MIGRATION_RETIREMENT_PLAN.md` and reviewed manifest (do not run yet);
5. working tests, corrected active docs/skills/config/requirements;
6. a final `git diff --stat`, `git status --short`, and exact commit/push status (never claim pushed if not);
7. explicit confirmation that the next session can start with `bounties/BOUNTY-0001-LEVEL1-P0.md` using existing `AGENTS.md` methodology.

Do not give another migration plan as the final result. Make the changes and run the checks. Do not resume setup work after everything fixable passes; hand off to deep research.
