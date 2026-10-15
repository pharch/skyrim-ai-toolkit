# Historical alignment note

This file preserves a migration-era configuration sketch. It is not the active
tool contract. Use `docs/LOCAL_RUNTIME_CONTRACT.md`; the current Ghidra binding
is `GHIDRA_PROJECT_REP_PATH` in ignored `config/local.env` and must point to an
existing `.rep` directory with its adjacent `.gpr` file.

# Final local alignment mission — Skyrim AE glitch-hunting harness

> **Run once in an interactive Codex session at the root of `pharch/skyrim-ai-toolkit`, on the `glitch-hunting-setup` branch.** This is the final environment-alignment and functional-validation task **before** deep research. Do the actual work and tests; do not merely report recommendations. Once the checks pass, stop the setup mission and hand off a precise ready-to-run research entrypoint.
>
> **This document supersedes conflicting assumptions in previous setup missions about which Skyrim executable to analyze, whether to create a new Ghidra project, and whether the public repository must provision software.** It does *not* supersede the project's scientific/evidence standards or safeguards for game data and saves.

## 0 — Three authoritative corrections

These are user decisions, not hypotheses to reopen.

**A. GOG executable is the canonical static-analysis binary.** Use the **previously analyzed GOG Skyrim executable** already present in the legacy research environment for Ghidra. The GOG build was deliberately selected because its Ghidra auto-analysis performs better. Do **not** reselect the Steam executable simply because a previous setup report successfully identified Steam AE 1.6.1170. Locate the exact GOG file and verify its identity/hash and relationship to the Ghidra project's imported program. Do not guess the GOG runtime version; discover and record it.

**B. Reuse the existing Ghidra project.** The original `skyrim` research workspace already contains an established Ghidra project, tooling, paths, scripts, and accrued manual/automatic analysis. Point the new harness at **that same project**. Do **not** create a replacement project, re-import Skyrim, repeat wholesale auto-analysis, or overwrite its program database. Preserve function names, labels, types, bookmarks, annotations, scripts, and prior work. A fresh read-only query against that existing project is the required proof of integration.

**C. GitHub stores the portable harness, not the user's installed environment.** Ghidra, CommonLibSSE-NG, SSEEdit, SKSE, game binaries, active game installations, local projects, save data, private Apocrypha archives, and local UESP data already exist on the user's Windows PC or are provided by the user. **Do not copy them into this Git repository. Do not reinstall, rebuild, rediscover through generic internet recipes, or publish them as part of setup merely to satisfy a checklist.** The repo should contain agent instructions, skills, source code/wrappers, experiment and research bookkeeping, portable path/config templates, tests, and *non-private* documented findings. A reproducible local **binding procedure** is required; a reproducible install of all third-party tools is not.

### Important: distinguish three identities

Maintain separate labels and paths for:

1. **`analysis_binary`**: existing **GOG** executable used by the canonical Ghidra project.
2. **`analysis_project`**: the **existing local Ghidra project** containing that binary and previously accrued analysis.
3. **`runtime_target`**: the actual Skyrim AE game instance used for record/load-order checks and eventual SKSE experiments. This might be a Steam installation; do **not** assume it is identical to the GOG analysis build.

All are within the research scope of **Skyrim AE**. A different store/distribution is not permission to introduce VR, LE, or unsupported pre-AE targets.

**Critical inference rule:** GOG native addresses, binary function signatures and offsets must **never** be transferred to another distribution/build merely because names or high-level mechanics seem similar. For runtime-specific claims, identify the runtime build, establish independent mappings (e.g., signatures, address-library IDs when applicable, call graph, code pattern, behavioral tests), and label confidence. A GOG result is evidence about the GOG analysis build; its generalization to a distinct running build is a separately testable claim.

---

## 1 — Scope and behavioral contract

Your role is **alignment agent**, not the week-long research agent.

You must:

- Inspect the **actual current checkout**, its latest reports and existing wrappers; do not assume findings from older audits are still true.
- Inspect the existing legacy research workspace at `%USERPROFILE%\Documents\GitHub\skyrim` **read-only** (or use a pre-existing user-configured legacy path if that is the actual checkout). Treat its previously tested paths and Ghidra/project access patterns as more authoritative than newly invented ones.
- Extract and reuse working paths, wrappers, native tooling contracts, research source aliases and project identities. Migrate the *integration conventions* and relevant instructions, not the installations.
- Repair the new toolkit's bindings, skills, router, preflight, CI expectations and startup instructions to embody the three corrections above.
- Test a representative operation through each already-installed essential interface and record results precisely.
- Finish all independent tasks despite local blockers; produce a truthful readiness report and a one-command/single-prompt research handoff.

You may edit files **inside the new toolkit checkout** and create **Git-ignored** local configuration and diagnostic output. You may inspect the old `skyrim` checkout, installed tools, Ghidra projects, and game files **without modifying them**. Do not alter the original project, program database, analysis settings, source checkout, game files, original saves, or user-wide environment without specific necessity and permission. Do not launch invasive gameplay mutation as a setup test.

**No re-platforming:** retain functioning scripts regardless of whether implemented in Python, Node, Java, PowerShell, C++, Ghidra scripting, or another working language. Prefer a small adapter/launcher over rewriting a tested implementation. Do not install or rebuild CommonLibSSE-NG or Ghidra just because the harness cannot find them; repair its local path resolution instead.

**No false continuity claims:** running commands and updating checkpoint files proves the *ability to recover state*, not guaranteed continuous Codex execution for a week. Avoid time-based supervisors as the required primary interface; the user starts an interactive Codex session.

---

## 2 — Mandatory work products

Keep these paths, or adapt to existing equivalent names where doing so avoids duplication:

```
config/local.example.env                # checked-in keys and descriptions, no machine paths
config/local.env                        # gitignored, real local bindings, never committed
protocols/TOOL_ROUTING.md               # tool decision tree, no implicit Steam Ghidra preference
.agents/skills/...                      # runnable research skills, correct local contracts
docs/LOCAL_TOOL_BINDINGS.md             # portable setup/discovery, GOG/Steam distinction
docs/RESEARCH_START_PROMPT.md            # genuinely continuous research session start
migration/FINAL_ALIGNMENT_CHECKLIST.md  # individual criteria with test evidence
migration/FINAL_ALIGNMENT_REPORT.md     # tested capabilities, limitations, readiness
migration/FINAL_ALIGNMENT_RESUME.md     # precise next action if interrupted
migration/FINAL_ALIGNMENT_CHANGES.md    # changes made; old claim -> corrected claim
```

Use existing configuration conventions if present; do not create a competing second environment registry. The exact key spellings below are suggested semantic fields, not an instruction to duplicate keys already in active use:

```
# Do not commit the filled-in file.
LEGACY_SKYRIM_REPO=
GHIDRA_INSTALL_DIR=
GHIDRA_HEADLESS_EXE=
GHIDRA_PROJECT_DIR=
GHIDRA_PROJECT_NAME=
GHIDRA_PROJECT_PROGRAM=               # project folder/name, not blindly 'SkyrimSE.exe'
GHIDRA_ANALYSIS_EXE_GOG=              # optional raw path, if the original binary is retained
COMMONLIBSSE_ROOT=
SSEEDIT_EXE=
SKYRIM_AE_RUNTIME_EXE=
MO2_PROFILE_DIR=
SKSE_PROBE_ROOT=
UESP_INDEX_PATH=
APOCRYPHA_INDEX_PATH=
```

If the legacy repo uses an MCP endpoint or a custom Ghidra headless harness instead of the raw `analyzeHeadless` CLI, **reuse that working interface** and document how the settings map to it. Do not force a CLI rewrite.

The local registry must be **single source of truth**. Don't maintain one path in a skill, a different one in a Python default, and a third in a PowerShell script.

**Privacy:** user-specific absolute paths and private corpus contents must be confined to the ignored configuration and logs outside tracked content. A bootstrap instruction may refer to `%USERPROFILE%\Documents\GitHub\skyrim`; generated canonical documentation should use config variables and portable placeholders.

---

## 3 — Execution phases

### Phase A — Inspect and establish a baseline

1. Confirm branch, current commit, dirty status, existing locally uncommitted research, and `.gitignore` behavior. Do not reset or delete user changes.
2. Read `AGENTS.md`, `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`, tool routing, existing skills, recent readiness reports, capability matrix, and all current relevant configuration.
3. Search all tracked files (especially `.md`, `.toml`, `.json`, `.py`, `.ps1`, `.js`, `.yml`) for incorrect assumptions: `Steam` as the *Ghidra* canonical binary, auto-generated Ghidra projects, compulsory full auto-analysis, software installation as a repo setup step, source/asset copies, hard-coded user paths, and Python-only tool limitations.
4. Distinguish **legitimate historical notes** about previous Steam smoke tests from **active instructions** that incorrectly choose Steam. Keep history accurate; correct current state and defaults.
5. Record the baseline and turn the checklist at the end of this file into a durable per-item ledger before major edits.

### Phase B — Discover and bind the existing GOG Ghidra workspace

1. Inspect the legacy `skyrim` checkout for path manifests, executable paths, `.gpr` projects, scripts, API/tool server definitions, Ghidra plugins, headless entrypoints, function mappings, and prior troubleshooting. Do not assume the project itself resides under the Git repo; follow its documented path.
2. Identify exactly **which Ghidra project and program** the old research used; confirm it contains established analysis (real functions, annotations, decompilation and ideally a known mapped function). Record their identities without copying or committing project data.
3. Identify the **GOG** executable and derive its actual file version, distribution and SHA-256 if possible. Confirm the chosen Ghidra program is the already-imported GOG target using project metadata, existing manifests, import path, checksums or other defensible evidence. Do not equate program name alone with matching binary identity; if ambiguous, report ambiguity and investigate without re-importing.
4. Configure the new harness to query that project **in place**. Prefer the legacy working tool contract. Where using Ghidra's `analyzeHeadless`, query the existing project with `-process <existing-program> -noanalysis -readOnly` and a narrowly scoped **read-only** script. Do not use `-import`, `-overwrite`, `-deleteProject`, or omit `-noanalysis` in a smoke test. Protect against concurrent project locks and resolve them non-destructively.
5. Run at least one representative **function lookup**, **xref/caller lookup**, and **decompilation or disassembly** query in the established project. Save output under a Git-ignored diagnostic directory or as a small, non-sensitive evidence excerpt with metadata.
6. Ensure the old project's function annotations and mappings can be searched and cited in future research. Map original research references to their new evidence aliases; do not invent replacements.
7. Fix scripts, skills and preflight routines that currently create new projects or prefer the Steam binary. Add tests proving the GOG project is selected, and that no implicit analysis/import is triggered.
8. Document what the `GOG` analysis binary does **not** establish about the local runtime build. Include a clear workflow for cross-build validation when a claim requires runtime verification.

### Phase C — Bind other already-installed local research tools

Discover **tested, existing paths** from legacy configuration and current local environment. Verify *actual operations*, not mere file existence:

- **CommonLibSSE-NG / Address Library / symbols**: locate existing headers, generated binaries or build output and related mapping notes; verify targeted code/symbol lookup against the appropriate build identity. Do not run a fresh full build unless absolutely required for a representative controlled probe test, and never install as the default action.
- **SSEEdit/xEdit**: locate the user's existing executable/wrappers and active local MO2 profile when relevant; verify read-only record inspection. If effective winner/override analysis is blocked by an unavailable or inconsistent active load order, give an exact blocker and keep independent tasks moving. Don't fabricate an active plugin list.
- **Papyrus / BSA**: reuse working disassembly/decompilation and archive-extraction methods from the legacy repo; verify a known file extraction/read.
- **Save / co-save / ReSaver**: locate the working tool; verify a controlled read-only parse of a suitable copy, if available. Do not require a Python replacement for a working Java implementation.
- **SKSE / Observer / DevBench / runtime probes**: locate existing plugins and probe workflow, document the distinction between **built**, **installed**, **loaded**, **handshaking**, **read-only observation**, and **mutating action**. Perform a *live* read-only handshake only if a compatible AE process and a safe test environment already exist; do not launch or modify gameplay just to claim it passed.
- **UESP and Apocrypha**: resolve the already-indexed local corpora and query one relevant known entry each. Preserve the private corpus, hashes, attribution, and retrieval capability. Do not re-download or rebuild a working corpus without evidence of corruption or incompleteness.

Update tools, routing, skills, and local preflight so the correct configured path is always selected; fail clearly on missing or mismatched files. The preflight must not require that all of the above be committed, bundled or installed by the public repository.

### Phase D — Fix the repository's separation of concerns

The **tracked Git repo** should provide:

- Codex research policies, validated skills, query wrappers and adapters;
- Portable configuration **templates** and `--help`, doctor/preflight routines;
- Research frontier, claims/evidence schemas, curated observations, hypotheses and cross-system model;
- Tests and small redistributable synthetic fixtures;
- Documentation that assumes the user supplies local installs/data.

The **ignored local environment** should hold:

- Executable locations, Ghidra project path/name/program identity, load-order/profile paths;
- Machine-local tool launches, personal exports, full indexes, large/raw outputs and diagnostic logs;
- Game executables, runtime installations, builds/compilation artifacts and original saves.

Search for Git-tracked violations. Add targeted ignore rules and remove accidentally tracked private/binary files from the Git index **without deleting local originals** (e.g. `git rm --cached` only when warranted). Do **not** remove project research conclusions just because they mention the existence of a private source; keep public metadata and provenance aliases.

Replace overly broad installation instructions with a short **local binding guide**. Existing users should be able to clone the harness, copy the env template, bind their installed tools, run the doctor, and start Codex. Installation instructions may be offered as external references, but are neither a dependency of the repo clone nor a setup agent's responsibility.

### Phase E — Make agent cognition match the real environment

1. Audit every active `AGENTS.md`, skill, prompt, tool router, readme, README fragment, and research start guide for incorrect environment assumptions. Do not do a cosmetic blanket search-and-replace of the word "Steam": the runtime may actually be Steam, and previous tests really used Steam. Correct **meaning**, defaults and provenance.
2. Ensure the Ghidra research skill teaches the agent to **query the existing GOG project**, reuse historical mappings, and explicitly test cross-build generalizations. No instructions to import/rebuild the Skyrim binary as the default path.
3. Ensure every tool skill specifies preconditions, actual command entrypoint, example query, evidence capture, build identity, limitations and error recovery, while deferring paths to the local registry.
4. Ensure static GOG reverse engineering is available when the live runtime and/or MO2 are absent; don't make the deep native research lane wait on an unrelated runtime blocker.
5. Confirm existing glitch-hunting knowledge, numeric boundary work, quest-gating ideas and armor-XP hypotheses remain discoverable from the new canonical docs, with links to original local source aliases. Do not redo knowledge migration unless links are broken.
6. Confirm each investigation has a discriminating question/model, source evidence, confidence, negative results, causal-model update, cross-domain synthesis and next frontier decision.
7. Ensure the interactive Codex starter specifies **continuous frontier reselection** after local completion, periodic global synthesis, limited breadth exploration, compact checkpointing and an actual restart/recovery protocol. A checkpoint must **never** be interpreted as a reason to stop while independent useful work exists.
8. Keep the goal hierarchy: (P0) bypass level gates, (P0) functional armor without armor skill XP, then low-XP enchanting and permanent potion/poison effects.

### Phase F — Validate and finalize

Run and preserve results for:

- Local configuration resolution and privacy/sensitive-path scans.
- A real **GOG project** query (lookup + xrefs + decompilation/disassembly) in **read-only/no-analysis** mode.
- A negative test where Steam runtime paths are present but **Ghidra still selects GOG**.
- A negative test that missing GOG project config gives a clear error rather than silently creating a new project.
- A negative test that Ghidra project path is treated as external and never staged for Git.
- An actual read-only query through each available essential local tool.
- All portable unit/CI tests, validation of skill metadata and tool commands, and research-frontier/evidence integrity.
- A short transaction/checkpoint recovery exercise: mark a sample investigation in progress, write a scratch evidence record, resume from a **fresh Codex session if feasible** or a separately launched minimal process, and confirm the next action is recovered without a recap. Use disposable synthetic records; do not contaminate production claims.
- A final consistency pass across `STATE.md`, frontier, capability matrix, tool router, setup report, and research start prompt. Compact stale setup history out of working memory without deleting historical evidence.

If one real external integration can't be tested (e.g., Skyrim not running), mark that *specific* capability `BLOCKED_EXTERNAL` with the exact future test; this must not prevent declaring the independently verified **static GOG research lane** ready.

At completion, write an explicit three-gate verdict:

- **GATE 1 — GOG native static research:** `READY` only if the existing GOG Ghidra project has passed real query checks and the agent can cite its outputs.
- **GATE 2 — Quest/record/native cross-checks:** `READY` only if the local record/load-order tools perform a real appropriate query, with a verified runtime/build identity where applicable. Otherwise `PARTIAL` with exact missing capability.
- **GATE 3 — Autonomous live AE experiments:** `READY` only if a real safe game handshake and observational capture have been verified; otherwise `NOT_VERIFIED`, which is acceptable for commencing static research.

Report the precise first command and initial Codex prompt to begin deep research. **Do not initiate an open-ended deep research session as part of this final setup task.**

---

## 4 — Acceptance checklist (turn into a persisted per-item ledger)

Use `PASS`, `FAIL_FIXABLE`, `BLOCKED_EXTERNAL`, or `NOT_APPLICABLE` with criterion-specific evidence (command, path alias, output, test, result). A checked box without evidence is not PASS.

### A. Baseline / legacy recovery

- [ ] A01 — Correct branch and commit identified; user changes preserved.
- [ ] A02 — Current setup reports and all active tool bindings inventoried.
- [ ] A03 — Original `skyrim` checkout inspected read-only; working Ghidra/tool workflow located.
- [ ] A04 — Legacy source/provenance aliases resolve or have precise repair notes.
- [ ] A05 — No older readiness assertion is accepted without matching current evidence.

### B. GOG Ghidra binding (release-critical)

- [ ] B01 — Existing Ghidra project location/name/program unambiguously identified.
- [ ] B02 — Existing GOG analysis executable located; version and SHA-256 recorded privately.
- [ ] B03 — Project program verified as intended GOG target with defensible evidence.
- [ ] B04 — Existing analysis, functions and annotations preserved; no new project imported.
- [ ] B05 — Read-only/no-autoanalysis function lookup succeeds on existing project.
- [ ] B06 — Real xref/callers query succeeds against the existing project.
- [ ] B07 — Real decompilation or disassembly query succeeds against the existing project.
- [ ] B08 — No Steam-preferred Ghidra fallback remains in active code/config/prompts.
- [ ] B09 — Tests prevent accidental project creation, import, overwrite and default full analysis.
- [ ] B10 — Binary-build provenance accompanies native evidence; cross-build transfer is not assumed.
- [ ] B11 — Local binding used by tools, skills and doctor is consistent and single-sourced.

### C. Existing local tools

- [ ] C01 — CommonLib/Address Library references resolve and version requirements are documented.
- [ ] C02 — xEdit/SSEEdit read-only record query works; winning-record limitation is explicit if blocked.
- [ ] C03 — Papyrus+BSA known-input inspection works.
- [ ] C04 — Read-only save/co-save/ReSaver analysis works or exact external blocker is recorded.
- [ ] C05 — SKSE probes and other runtime tools are discovered without copying installations.
- [ ] C06 — Live handshake state is truthfully verified or precisely marked NOT_VERIFIED.
- [ ] C07 — UESP index retrieves a real article with revision/source reference.
- [ ] C08 — Apocrypha index retrieves a real message/context with stable provenance.
- [ ] C09 — Tool registry names actual commands, build identities and restrictions.

### D. Repository hygiene / portable harness

- [ ] D01 — Public Git stores harness code/skills/docs/tests rather than Ghidra projects and game/tool installations.
- [ ] D02 — Config template is portable and safe; actual local binding is Git-ignored.
- [ ] D03 — Machine-specific absolute paths are absent from tracked active configs/docs (aside from non-secret historical source quotes where necessary).
- [ ] D04 — Private exports, binaries, save data, projects and diagnostic logs are not tracked.
- [ ] D05 — No automatic third-party installers/builds are required to launch the harness.
- [ ] D06 — No default tool operation silently imports or auto-analyzes a fresh executable.
- [ ] D07 — Clone → bind → doctor → interactive Codex startup is documented and tested locally.
- [ ] D08 — Portable CI can pass without Ghidra/game executable; optional local tests explicitly use external installs.

### E. Skills / accumulated research / autonomous loop

- [ ] E01 — All active docs and skills consistently describe AE glitch-research, not asset or gameplay content authoring.
- [ ] E02 — Ghidra skill uses the existing GOG project and protects it from mutation.
- [ ] E03 — Skills for Ghidra, CommonLib, xEdit, Papyrus, SKSE, UESP, Apocrypha and experiments use tested entrypoints.
- [ ] E04 — Prior glitch research and original condensed foundations remain referenced and searchable.
- [ ] E05 — Source citations/claims distinguish GOG analysis from another runtime build.
- [ ] E06 — Competing hypotheses and discriminating experimental predictions are part of the normal workflow.
- [ ] E07 — Negative evidence, contradictions and uncertainty update durable records rather than disappear.
- [ ] E08 — Frontier regeneration, cross-system synthesis and some deliberate breadth exploration are explicit.
- [ ] E09 — Research-state checkpoint/recovery is validated with an actual exercise.
- [ ] E10 — Session start does not end by default after a single completed investigation.
- [ ] E11 — `STATE.md`, frontier, recovery state and capability matrix agree on what is currently usable.

### F. Final evidence and handoff

- [ ] F01 — All relevant portable tests/validators run and their outcomes preserved.
- [ ] F02 — The checklist contains criterion-specific evidence, not copied generic PASS text.
- [ ] F03 — GOG static-research gate explicitly assessed against real tool evidence.
- [ ] F04 — Record/native cross-check and live-game gates assessed separately and honestly.
- [ ] F05 — Final report identifies all external blockers and exact unblock commands.
- [ ] F06 — A precise interactive Codex research start prompt is present and executable.
- [ ] F07 — No unreviewed changes to legacy repo, original Ghidra project, install, live saves or private archives.
- [ ] F08 — Work committed only when safe; `git status` audited for any inadvertent private artifact inclusion.

---

## 5 — Recovery and stopping rule for this setup mission

Do not stop because you finished an intermediate phase, a preflight failed, the active Skyrim process is unavailable, or an interesting research question emerged. Update the ledger, move to another independent checklist item, and continue. You are allowed to end this setup assignment when:

1. Every criterion has a defensible status and evidence;
2. Every locally fixable defect has been repaired and retested;
3. The three readiness gates are assessed honestly;
4. Current operating docs are coherent; and
5. A research session can start without any further Ghidra installation/project-creation steps.

If system limits interrupt the session, persist the exact next action in `migration/FINAL_ALIGNMENT_RESUME.md` so a fresh Codex session can continue. Do not claim to be running after the session ends.

**Final message format:** Summarize what changed, the tested GOG project identity (without publishing sensitive absolute paths), major tool smoke-test outcomes, remaining external blockers, the three readiness gate results, and the exact Codex starting instruction for the first deep P0 investigation.
