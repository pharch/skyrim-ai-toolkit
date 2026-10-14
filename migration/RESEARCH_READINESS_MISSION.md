# Mission: Final Local Readiness Audit and Repair of the Skyrim AE Glitch-Research Harness

> **Give this entire file to your local Codex agent.** Place it at `migration/LOCAL_RESEARCH_READINESS_MISSION.md` in the `pharch/skyrim-ai-toolkit` checkout, open Codex in the repository root, and ask it to execute this file end-to-end. This is a **setup/verification mission**, not the indefinite research mission itself.
>
> **Target:** Skyrim **Anniversary Edition (AE)** only. The literal executable `SkyrimSE.exe`, directory `Skyrim Special Edition`, SSEEdit, `GM_SSE`, and `CommonLibSSE-NG` may be correct technical interface names for AE; they do **not** imply support for pre-AE SE runtimes. Record and pin the exact local executable version and distribution before making any runtime-specific claim.

## 0. Non-negotiable outcome

Transform the **current checked-out repository and tested local machine** into a usable, self-contained *research harness* that can support a first deep autonomous investigation into Skyrim AE exploit mechanisms.

Your objective is **not** to write another optimistic setup report. You must personally inspect the files, invoke the actual tools, exercise their real capabilities, repair deficient components, validate research-state persistence, and leave an evidence-backed readiness verdict.

The preceding source-level audit identified potential regressions and omissions. Treat each as a **hypothesis to check against the current repository**, not as an immutable description of the current branch:

- A Python-only tool policy may have sidelined working Node/xEditLib and Java/ReSaver functionality.
- Record inspection may parse isolated plugins but not compute **winning overrides for the active AE load order**.
- Headless Ghidra may be detected but unusable because Java/project/runtime configuration is missing.
- CommonLibSSE-NG may exist as source without a validated build, navigation, or ABI/version mapping.
- SKSE tooling may be synthetic-only rather than capable of a real read-only handshake with the AE process.
- Papyrus, BSA and structured save inspection may have lost capabilities during cleanup.
- UESP and Apocrypha retrieval may function while completeness, provenance, or privacy are underspecified.
- Historical knowledge may be indexed but partially inaccessible from new canonical claims or source aliases.
- The research starter may end after one investigation instead of selecting the next frontier item.
- `RECOVERY.json` / `STATE.md` / session log and frontier may disagree on what is active.
- Independent resumed-session behavior may be untested.

**Implement corrections, not just recommendations.** Preserve already-working capabilities and documents. Do not perform another unnecessary repo-wide reorganization.

### The research goals the harness must serve

1. **P0-A:** Find reproducible vanilla-compatible routes for a level-1 character to trigger normally level-locked quests, encounters, events, and other content.
2. **P0-B:** Allow functional armor to be worn without gaining Heavy/Light Armor skill XP from incoming hits.
3. **P1-A:** Craft powerful enchantments without enough skill XP to cross specified thresholds, especially 15→16 and 20→21.
4. **P1-B:** Cause normally temporary potion/poison effects to persist indefinitely.

P0 questions must drive research prioritization. The harness must nevertheless support broad engine exploration, cross-system synthesis, and testing of unexpected mechanistic connections.

## 1. Operating rules — read before acting

### Work to completion, not to a convenient summary

- Work through the **entire** checklist below. A completed phase is a handoff **within** this mission, not permission to stop.
- If one tool cannot be accessed, record the exact blocker and proceed to other independent tools and checks.
- Do not ask for confirmation for ordinary repository edits, dependency discovery, documented tool configuration, read-only analyses, or safe local smoke tests.
- Install or repair ordinary user-space development prerequisites if appropriate and permitted by the environment. Record package, version, source, command and any PATH changes. Avoid privileged/system-wide modifications unless separately authorized.
- Never convert a failed tool test into a PASS by weakening a test, making a mock impersonate a real binary, or writing a success-shaped log.
- Do not mark a capability PASS for a path-existence check alone. A usable capability requires a **representative actual operation**.
- Prefer existing tested wrappers from `C:\Users\matth\Documents\GitHub\skyrim` or the upstream toolkit over new implementations. Python orchestration is welcome; a **Python-only implementation restriction is not**.
- Preserve all useful technical knowledge, numeric examples, experiments, negative findings and provenance. Do not overwrite history to make reports look tidy.
- No user-facing result that is true only after manually forcing a quest, ActorValue, stage, item or spell in debug mode may be presented as a vanilla exploit.

### Protect the actual game and private data

- **Read-only by default** for game installation, original data files, binary projects, original saves, load order and exports. Do not alter a live installation, real profile, working save, or archival source as part of setup.
- For state-mutating runtime tests, use a deliberately disposable save/profile, snapshot preconditions, capture before/after state, and distinguish debug intervention from genuine vanilla reproduction. If this cannot be safely arranged without user interaction, mark the *runtime state-mutating* test BLOCKED_EXTERNAL and continue.
- Never commit local absolute Windows paths, usernames, tokens, private Discord message bodies, UESP dump binaries, copyright-restricted game binaries, save files, or Ghidra project databases to the public repository. Use a Git-ignored local configuration and portable example templates.
- Do not start unattended gameplay or destructive runtime probes as an installation test.
- Distinguish an absent permission/credential/tool/game process from a software defect. Blocked external tests must have exact reproduction instructions, not vague TODOs.

### Acceptance evidence and truthful status

Use one of these statuses per criterion: `PASS`, `FAIL_FIXABLE`, `BLOCKED_EXTERNAL`, `NOT_APPLICABLE` (with justification). `DOCUMENTED` is **not** `PASS` for a required operational check.

For each criterion record:

```
ID | status | checked_at | command_or_operation | observed_output_or_artifact |
source_or_test_reference | change_or_commit | remaining_limitations
```

`BLOCKED_EXTERNAL` is legitimate only if there is a real environmental dependency that cannot safely be satisfied without user action, with an exact procedure for later verification. A PASS must reference criterion-specific evidence; do not repeat the same generic “tests passed” sentence for 80 rows.

## 2. Working documents and resume contract

Immediately create/update these **inside this repository**:

```
migration/LOCAL_READINESS_CHECKLIST.md       # all IDs below, one row per criterion
migration/LOCAL_READINESS_REPORT.md          # capabilities, actual tests and result
migration/LOCAL_READINESS_BLOCKERS.md        # externally blocked operations with next commands
migration/LOCAL_READINESS_RESUME.md          # one unambiguous next task after interruption
migration/LOCAL_READINESS_CHANGES.md         # meaningful fixes and provenance
```

Keep the checkpoint compact and accurate at all times:

```
phase:
current_criterion:
last_successful_test:
current_tool_or_target:
actual_blocker_if_any:
next_exact_action:
working_tree_and_commit:
```

Before any context compaction, tool timeout, session exit or expected context limit, update the checklist, RESUME file and relevant active state. A later session must be able to continue from disk **without reexplaining the project**. Never claim background execution after this session has ended; resume using the same interactive session while it remains available.

**If an existing `LOCAL_SETUP_CHECKLIST.md` or `FINALIZATION_CHECKLIST.md` exists, reconcile with it; don't simply copy its PASS statuses.**

## 3. Execution plan

### Phase A — Pin the environment and inspect actual capability

1. Confirm correct repository and branch; inspect Git status, HEAD, relevant existing reports/briefs, and current `AGENTS.md`.
2. Determine the exact Skyrim AE executable version, distribution, installation path and game profile, with safe detection that **does not silently switch to VR, LE, or pre-AE SE**.
3. Inspect local executable paths and configuration in **the original read-only research repository**:
   `C:\Users\matth\Documents\GitHub\skyrim`.
4. Read the old repository's operational Markdown, scripts and recorded tool-invocation commands; collect known-working paths for Ghidra binaries/projects, Java/JDK, xEdit, SSEEdit, xEditLib, BSA, Papyrus, SKSE, CommonLibSSE, DevBench, ReSaver, MO2, UESP and Apocrypha indexes.
5. Preserve machine-specific resolved paths in an ignored local file (e.g. `config/local-paths.toml`), with checked-in redacted/example configuration. Document path precedence and validation.
6. Create a **capability matrix** with `tool → upstream/original interface → installed binary → actual supported operations → test → limitations → research skill`, marking real/binary-backed vs synthetic/mock tests.
7. Never assume a tool must be rewritten in Python. Restore or wrap proven Node/Java/PowerShell/native implementations when they do the job correctly.

### Phase B — Audit every active Markdown file, skill and instruction boundary

1. Enumerate **all tracked Markdown** files, including hidden skill trees and `.github`, excluding only explicitly marked provenance archives from *active-instruction* scanning; inspect archive contents for knowledge retention separately.
2. Search active documentation for mod-production goals, asset/animation/texture authoring, Claude-specific commands/hooks, VR/LE support, pre-AE SE fallback logic, `setup.sh` assumptions, old 45-minute supervisor-first instructions and incompatible startup prompts. Review each hit contextually.
3. Preserve legitimate technical names (`SkyrimSE.exe`, SSEEdit, CommonLibSSE-NG, `GM_SSE`) and references to *experimental instrumentation plugins*. Remove **instructional goals and actual compatibility paths** irrelevant to AE glitch research—not every occurrence of “mod,” which may be an engine term.
4. For each `SKILL.md`, verify skill-discovery path, frontmatter, trigger description, relevant tools, exact working commands, expected artifacts, observational vs state-mutating modes, game-version assumptions, failure diagnosis, and evidence logging.
5. Remove duplicate, conflicting or discoverable legacy instruction trees once their useful operational details have been preserved. `AGENTS.md`, README, skills, research protocols, onboarding, tool registry and research-start prompt must agree.
6. Update installation documentation to use the correct branch, show actual Windows preflight and explain read-only safety and local ignored config.
7. Implement/refresh a repository-wide Markdown/skill audit check that CI can run, with a narrowly justified allowlist for provenance archives and necessary technical terms.

### Phase C — Restore and demonstrate **real** research tools

#### C1. AE load order and record interrogation (critical for quest gates)

- Resolve the actual MO2/active profile and effective load order (including managed profile locations rather than guessing `plugins.txt`).
- Prove winning-override resolution across **two conflicting records in a test fixture**, plus one real read-only query from the AE load order. Record plugin origin, FormID/EditorID, overrides, winning record, relevant conditions/aliases/scripts and provenance.
- Re-enable a real xEdit/xEditLib implementation or a proven equivalent. Standalone per-file Python record parsing is **insufficient** as the only interface.
- If Node/xEditLib previously worked, retain/wrap it. Do not degrade functional analyses to an inferior one-language implementation for aesthetic consistency.
- Demonstrate inspection of a quest-gate-related record with a cited output artifact, while avoiding unwarranted assumptions about unknown quest internals.

#### C2. Ghidra headless and native mapping (critical for XP and event gates)

- Validate the selected Java/JDK runtime, actual Ghidra `analyzeHeadless` launcher, Ghidra project storage, project availability and imported binary identity.
- Prove a **real** bounded headless operation: import or open the correct AE binary/project; list functions; resolve one function/symbol/address; retrieve decompilation or at least disassembly; enumerate an xref/call graph edge; export a stable artifact.
- Map addresses against the actual local AE executable distribution/version. Never transfer old GOG or pre-AE offsets uncritically.
- Recover existing scripts and function maps from original `skyrim` repo and preserve what is validated. If a specific decompiler step fails, capture the exact failure and try an existing documented script or supported Ghidra workflow.

#### C3. CommonLibSSE-NG and SKSE native tooling

- Identify the actual CommonLibSSE-NG source and release/commit, dependencies, toolchain and AE version compatibility. Run a build, a compile-only smoke target, or another *real validated interface* demonstrating function/ABI navigation; document which level was achieved.
- Confirm real SKSE and Address Library/runtime version compatibility rather than assuming a source checkout proves runtime capability.
- Distinguish **headless agent control of an instrumented running Skyrim** from the impossible assumption that SKSE itself runs a complete headless game engine.
- Validate at least one real **read-only** bridge/probe transaction with an actual running AE process if safely available: target identity, handshake, observation, event/state capture, protocol version, and log provenance. If a user must launch/select a disposable test save, stage everything else and record a precise blocked test.
- Do not claim quest manipulation, AV mutation, or permanent game-state changes as successfully tested until an isolated experiment has genuinely exercised them.

#### C4. Structured save, Papyrus, BSA and diagnosis

- Restore read-only **structured ReSaver/changeform/co-save inspection** if Java/ReSaver exists; synthetic file inspection isn't equivalent. Exercise with a suitable permitted save fixture and cite exact findings.
- Demonstrate BSA asset/resource extraction **only when it serves scripts, game records or mechanics analysis**; no visual asset-creation workflow is needed.
- Demonstrate Papyrus `.pex` decompilation or symbol/call analysis using installed tooling; verify extracted script's origin and test artifact.
- Validate existing crash/log/Papyrus triage against at least one meaningful fixture.
- Keep useful backend implementations in their native languages with portable wrappers; ensure the tool registry reports clearly whether an operation is read-only or write-capable.

### Phase D — Grounding and imported research knowledge

#### D1. Previous Skyrim research

- Enumerate all relevant Markdown in `C:\Users\matth\Documents\GitHub\skyrim`, including condensed foundational files. Confirm the current new repo's migration source map and hashes resolve against originals.
- Spot-check the **full derivation**, not just the summary, for numeric precision/ULP shifting, poison resistance scaling, quest gate candidates, armor XP, alchemy/potion classification, enchanting XP and permanent-effect hypotheses.
- Audit imported known-negative results, counterexamples, corrected claims, native function paths, probe outputs and experiment preconditions; preserve differences between old GOG findings and new local AE runtime.
- Ensure each important imported source is either represented by a canonical mechanism/claim/frontier link or deliberately recorded as not relevant with a reason. Fix broken alias links; never fabricate a source.

#### D2. UESP

- Confirm provenance of the official snapshot: original URL or archived source, snapshot date, metadata, hashes, relevant reuse/license requirements and actual namespace coverage.
- Run **real** exact-title, full-text and article-context retrieval for Skyrim quests, combat/armor, Alchemy, and enchanting. Confirm that the index actually contains `Skyrim:` titles, not only the empty MediaWiki main namespace.
- Provide citation-stable title, namespace, revision, source link, retrieved content and snapshot identity. MediaWiki wikitext/templates must not be naively stripped in a way that corrupts mechanics.
- If licensing or acquisition provenance cannot be reconstructed, state the precise limitation while retaining honest local retrieval. Never call the corpus complete without a supported completeness metric.

#### D3. Apocrypha Discord export

- Validate that the local private archive index can search by phrase and retrieve original message IDs, timestamps, author/source, channel/thread context and surrounding discussion.
- Prevent Discord/private content and its local paths from being committed to public Git. Quotes are historical reports, not automatically verified mechanics.
- Cross-check at least one imported claim against both Apocrypha context and another evidence type, documenting agreement/contradiction.

### Phase E — Research transaction integrity and scientific method

Audit and **exercise** the entire pipeline:

```
Observation / question
    ↓
Competing mechanistic hypotheses (or explicit exploratory probe objective)
    ↓
Discriminating predicted outputs / negative controls
    ↓
Tool invocation + captured raw evidence + environment identity
    ↓
Interpretation with confidence status + provenance
    ↓
Claims/mechanisms/glitches/contradictions updated
    ↓
Cross-system synthesis + new predictions
    ↓
Frontier updates and next tractable investigation
    ↓
Durable checkpoint → repeat
```

- Audit `STATE.md`, `ROADMAP.md`, `research/FRONTIER.json`, evidence register, claims, mechanisms, knowledge graph, contradictions, experiments, `SESSION_LOG.md`, `RECOVERY.json` and all skills/protocols governing them.
- Define transaction lifecycle: `queued → in_progress → completed | falsified | blocked`, with single owner/current item, exact evidence references and idempotent restart behavior.
- Reconcile orphaned/duplicate frontier entries and stale recovery pointers. Invalid cross-references and non-existent sources must fail validation.
- Make evidence append-only in effect (retain raw artifacts and superseded interpretations) and require source-specific confidence distinctions: runtime measurement, native static, record data, UESP, Discord, hypothesis.
- Block unsupported promotion from a community assertion to `CONFIRMED`.
- Ensure experiments specify version, load order, preconditions, controls, predicted differences, actual values (including float32 representation where needed), result and limits.
- Distinguish **hypothesis-testing mode** (two or more explicit rival models and discriminants) from **exploratory mode** (mapping an unexamined region, observation inventory, successor hypotheses). Neither mode should be reduced to a vague “investigate X” note.
- Require periodic **global synthesis** and **breadth exploration** across unfamiliar engine regions, not only repeated pursuit of a single mechanism. Give P0 objectives most research time but prevent permanent tunnel vision.
- Tool failures, negative evidence and blocked user experiments must produce useful frontier updates, not silence or a full-program stop.

### Phase F — Demonstrate actual autonomous continuity (critical)

This is **not** a request to run a week of research during setup. It is a short real validation of the control loop.

1. Run a bounded **three-investigation pilot** grounded in at least one P0 objective. Prefer three distinct but linked questions that exercise at least two real evidence backends. Avoid elaborate new game-state mutations just to meet a test requirement.
2. Each investigation must record a real question, plan, evidence/tool output, result, new or updated claim, frontier update and next candidate. Demonstrate at least one rejected/blocked line that causes *automatic reselection*.
3. Run a global synthesis after the pilot: derive a *testable* cross-domain prediction or explain with evidence why no such prediction was supported. Also log one deliberate breadth-expansion candidate outside the immediate local branch.
4. Verify that the research launcher/instructions continue after completing an investigation. **Writing a checkpoint is not a stopping condition.** Do not have the final prompt say “investigate one item and stop.”
5. Validate crash/interruption recovery using a partial transaction and a fresh process. For the strongest proof, run a genuinely separate Codex context (e.g. short independent `codex exec` invocation if installed/authenticated) that reads only on-disk state and correctly resumes without a recap. This is a **test**, not the main research interface and not a 45-minute supervisor. If the separate agent context cannot be launched, complete the deterministic restart test and mark the true independent-context test `BLOCKED_EXTERNAL`.
6. Ensure the actual expected interface for ongoing research is an **interactive local Codex session**. If the installed Codex version exposes a supported persistent Goal feature, document and test the actual interface. Do **not** assume an unsupported `/goal` command exists; provide a plain initial message as the portable default.
7. Create/update `docs/RESEARCH_START_PROMPT.md` (or the repository's canonical equivalent) with a tested continuous-loop directive. It must explicitly say: *after each local result, update evidence, synthesize, reselect the next tractable frontier item, and keep investigating; summaries are checkpoints rather than completion.* Legitimate session end conditions are user intervention, a hard execution/budget limit or genuine global exhaustion/blocking.
8. Avoid claiming absolute 7-day uninterrupted service. Prove that the work is continuously actionable and can be correctly resumed after interruption.

### Phase G — Final integration and delivery

- Run all applicable Python, Node/Java/native fixture tests, skill validators, state validators, Markdown/reference audit and Windows AE preflight. Fix regressions and rerun.
- Update CI checks for platform-independent properties and include AE-only negative tests (e.g. fake VR or pre-AE installations must be rejected rather than silently selected). Do not require a real game install in GitHub Actions.
- Reconcile README/start guide/`AGENTS.md`/skill routing/tool registry/canonical research start prompt with actual tested behavior.
- Make a **single precise user-facing setup guide** for future local reinstalls and the first deep research session, including configuration, validation commands and remaining blockers.
- Protect the original `skyrim` repo (read-only) and preserve the raw sources. Verify public `git diff` does not contain secrets, private archive material, local paths or original game content.
- Commit coherent repository changes where permitted. Do not push destructive changes or touch other branches without authorization. If pushing is authorized by normal repo workflow, push to the intended setup branch and record commit SHA.
- Write final reports with objective readiness gates (below), not a “seems ready” statement.

## 4. Numbered acceptance checklist

Copy **every** checkbox into `migration/LOCAL_READINESS_CHECKLIST.md` and fill criterion-specific status and evidence. Do not remove blocked items to inflate the PASS percentage.

### A. Environment and source-of-truth (A01–A09)

- [ ] **A01** Correct Git repository, current branch, clean/understood working tree and HEAD recorded.
- [ ] **A02** Local AE runtime executable and its **exact** version/distribution identified.
- [ ] **A03** AE-only resolution rejects VR, LE and pre-AE installations; real `SkyrimSE.exe` naming remains supported.
- [ ] **A04** Active profile/load order identified, not guessed from a default directory.
- [ ] **A05** Original `skyrim` repo inventoried read-only, including tool config and knowledge documents.
- [ ] **A06** Known-tested executable/project/index paths reused and verified rather than reinvented.
- [ ] **A07** Local machine paths stored in ignored config and portable examples checked in.
- [ ] **A08** Tool capability matrix distinguishes real, synthetic, available, blocked and absent operations.
- [ ] **A09** Public Git excludes private data, original game binaries and machine-specific paths.

### B. Instruction and skill cleanliness (B01–B11)

- [ ] **B01** Every active tracked `.md` and discoverable skill audited; inventory/provenance logged.
- [ ] **B02** No active mod-production objective remains; technical instrumentation terminology preserved.
- [ ] **B03** No active VR/LE or pre-AE compatibility workflow, fallback or command remains.
- [ ] **B04** No conflicting active Claude hook/delegation/control path remains.
- [ ] **B05** No primary quickstart depends on upstream game-folder `setup.sh` or timed supervisor.
- [ ] **B06** Skill frontmatter/discovery paths pass the installed agent's supported format.
- [ ] **B07** Each retained skill specifies triggering task and real tool invocation.
- [ ] **B08** Each retained skill specifies evidence artifacts, failure modes and provenance.
- [ ] **B09** Tool registry, README, research-start prompt and `AGENTS.md` agree.
- [ ] **B10** Markdown/reference/legacy-language CI audit passes with justified exceptions.
- [ ] **B11** Installation instructions target the actual branch and describe safe local Windows use.

### C. Real tool capability (C01–C16)

- [ ] **C01** AE active plugin load order resolved with evidence.
- [ ] **C02** Two-record winning-override fixture passes and returns the correct winner.
- [ ] **C03** One **real** winning-override record query succeeds against AE files.
- [ ] **C04** Quest record interrogation exposes conditions/aliases/scripts and provenance as available.
- [ ] **C05** Ghidra launcher/JDK/project prerequisites are checked as executable, not just paths.
- [ ] **C06** Headless Ghidra operates on the correct AE binary/project identity.
- [ ] **C07** Ghidra proves actual function/symbol/address lookup plus an xref/call edge.
- [ ] **C08** Ghidra exports decompilation or documented disassembly evidence.
- [ ] **C09** Current AE runtime mapping is separated from historical binaries/offsets.
- [ ] **C10** CommonLibSSE-NG real compile/build/navigation test recorded with compatible version.
- [ ] **C11** SKSE/Address Library/runtime compatibility validated from real local versions.
- [ ] **C12** Real read-only AE SKSE/DevBench/runtime handshake succeeds, or is explicitly externally blocked.
- [ ] **C13** Structured ReSaver/save/changeform/co-save analysis demonstrated on permitted data.
- [ ] **C14** Papyrus decompilation/inspection demonstrated with actual script artifact.
- [ ] **C15** BSA/resource extraction and log triage demonstrated where relevant to engine analysis.
- [ ] **C16** No working Node/Java/native tool is retired solely to satisfy Python-only policy.

### D. Knowledge and grounding (D01–D13)

- [ ] **D01** All original condensed foundational glitch research documents enumerated and mapped.
- [ ] **D02** Source hashes and local aliases resolve; missing sources explicitly recorded.
- [ ] **D03** Shifting/float32/ULP findings retain exact equations, inputs and constraints.
- [ ] **D04** Poison resistance and effect-application model retains uncertainty and negative tests.
- [ ] **D05** Level-gated quest/encounter findings linked to mechanistic hypotheses and evidence.
- [ ] **D06** Armor skill XP hypotheses and competing damage/armor classification pathways preserved.
- [ ] **D07** Enchanting XP and permanent potion/poison hypotheses preserved with known limitations.
- [ ] **D08** Imported historical binary/runtime findings labeled by version/distribution.
- [ ] **D09** UESP export snapshot provenance, relevant license, hash and namespace coverage recorded.
- [ ] **D10** UESP offline exact title/full-text/article retrieval actually exercised on `Skyrim:` pages.
- [ ] **D11** UESP results preserve citation revision/source and no misleading claim of completeness.
- [ ] **D12** Apocrypha index lookup/context retrieval tested with private-data safeguards.
- [ ] **D13** One substantive historical claim triangulated across at least two source types.

### E. Scientific research state (E01–E13)

- [ ] **E01** Frontier parses, uses stable IDs and has meaningful P0 entries.
- [ ] **E02** `STATE.md`, frontier, RECOVERY and session log agree on active state.
- [ ] **E03** All linked evidence/claims/mechanisms/experiments resolve; no silent orphans.
- [ ] **E04** Evidence entries distinguish raw observation from interpretation and community claims.
- [ ] **E05** Contradictions, superseded claims and negative results are retained.
- [ ] **E06** Hypothesis-testing protocols include rival predictions and discriminating measurements.
- [ ] **E07** Exploratory investigations have observation inventory and successor-generation rules.
- [ ] **E08** Experiments capture environment, controls, actual values and limitations.
- [ ] **E09** Diagnostic intervention is never labeled as vanilla exploit reproduction.
- [ ] **E10** Research transaction begin/update/complete/block operations are validated.
- [ ] **E11** Duplicate/reselected item without new evidence is detectable and recoverable.
- [ ] **E12** Cross-system synthesis affects graph/claims/frontier rather than producing prose alone.
- [ ] **E13** Periodic breadth exploration prevents permanent local tunnel vision without displacing P0.

### F. Autonomy, pilot and release (F01–F12)

- [ ] **F01** Start prompt explicitly demands repeated frontier selection until user stop/hard limit/global blocker.
- [ ] **F02** One investigation can terminate normally without terminating the research program.
- [ ] **F03** A blocked/failed line is recorded, and an independent actionable item is selected.
- [ ] **F04** Three real pilot investigations have evidence/tool outputs and result transactions.
- [ ] **F05** Pilot synthesizes a falsifiable cross-system prediction or documents why unsupported.
- [ ] **F06** Pilot includes one deliberate breadth exploration candidate.
- [ ] **F07** Recovery from a partially completed transaction works in fresh process.
- [ ] **F08** Independent fresh Codex-context recovery succeeds, or precise external block recorded.
- [ ] **F09** Interactive Codex is primary interface; no forced 45-minute process kill cycle.
- [ ] **F10** Windows/local and CI-executable validation suites pass, with full logs.
- [ ] **F11** Final reports include per-criterion evidence, truthful runtime limits and precise next commands.
- [ ] **F12** No secrets/private archives/local identifying paths/game binaries unintentionally committed.

**Total: 74 acceptance criteria** (A 9 + B 11 + C 16 + D 13 + E 13 + F 12). Do not substitute legacy checklist totals for these IDs.

## 5. Suggested commands and test patterns (adapt to actual checkout)

From PowerShell in the **new toolkit repo**:

```powershell
# Baseline
Get-Location
git branch --show-current
git rev-parse HEAD
git status --short

# Enumerate active tracked Markdown, including dot-directories
git ls-files '*.md'

# Discover skill files (including hidden directories)
Get-ChildItem -Force -Recurse -File -Filter SKILL.md | Select-Object -ExpandProperty FullName

# Search for potentially stale active directions (review context, don't blind-delete)
git grep -n -i -E 'claude|skyrimvr|skyrim vr|vrik|higgs|port.to.vr|legendary edition|skyrim le|mod creation|build a mod|45.minute|supervisor' -- '*.md'

# Read-only original-repo survey
$original = 'C:\Users\matth\Documents\GitHub\skyrim'
Test-Path $original
Get-ChildItem -LiteralPath $original -Recurse -File -Filter '*.md' |
  Select-Object -ExpandProperty FullName

# Existing tests: discover and use actual supported entrypoints; examples only
python --version
node --version
java -version
# python -m pytest
# npm test
# python scripts/validate_overlay.py
# python scripts/validate_research_state.py
```

**Important:** shell command samples are diagnostic hints; verify script paths before running. If a test command in old docs doesn't exist, find the current equivalent and fix the docs. Avoid skipping a capability merely because these example names differ from the present tree.

Recommended test artifacts (Git-ignored if they contain proprietary/private or host-specific data):

```
local-research-output/
  preflight/
  xedit-winners/
  ghidra-query/
  commonlib-build/
  skse-handshake/
  saves-and-papyrus/
  uesp-and-apocrypha/
  pilot/
  recovery/
```

Store **sanitized summaries, test fixtures and stable evidence references** in Git; keep full local/raw outputs outside Git if licensing or privacy requires.

## 6. Readiness decision — distinguish three gates

Do not give a single ambiguous `READY` flag.

### Gate 1 — `STATIC_RESEARCH_READY`

Requires active instruction/skill checks, UESP and community retrieval, historical knowledge resolution, read-only record analysis, research-state integrity and working pilot. Tool-specific blocked items must still be listed. A missing **winning-record resolution** capability is a blocker for **quest-gate-heavy** research even if generic parsing works.

### Gate 2 — `NATIVE_RESEARCH_READY`

Requires Gate 1 plus correct AE Ghidra headless function/xref analysis, CommonLibSSE-NG version/build/navigation evidence, real load-order-aware record analysis and relevant script/save analysis. Game process need not be running for this gate.

### Gate 3 — `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY`

Requires Gate 2 plus safe actual runtime probe capability, validated disposable-test workflow when interventions are needed, successful repeated investigation/synthesis, and independently demonstrated recovery across agent contexts (or an explicit limitation that prevents certifying this gate).

The three statuses are separate. If Gate 3 fails only for an unavailable running game, document that precisely. **Do not claim week-long uninterrupted execution was proven**; the goal is that the harness produces meaningful research and survives interruptions.

## 7. Required final answer and handoff

After satisfying every feasible criterion, write and show:

1. Branch and commit hash actually audited.
2. Summary of changes (with links/paths).
3. Gate 1 / Gate 2 / Gate 3 verdicts and why.
4. Count of PASS / FAIL_FIXABLE / BLOCKED_EXTERNAL / NOT_APPLICABLE out of **74**, with precise evidence.
5. The **real operations performed** for xEdit winners, Ghidra functions/xrefs, CommonLib, SKSE, ReSaver, Papyrus, UESP and Apocrypha (or exact blockers).
6. Pilot results, synthesis product and independent-recovery result.
7. Verification that public Git remains free from host-specific paths and private data.
8. Any remaining **user-only actions** as minimal, executable instructions, in priority order.
9. The exact initial prompt/file to launch the first deep research session.

Only mark setup complete when every locally actionable required check has been performed, and remaining blocked items are genuinely external. If you still have actionable failing checks, **keep working** instead of ending with a roadmap.

**Begin now. Inspect the current repository, build the checklist, repair missing capabilities, run the probes, test continuity, and finalize the gates.**
