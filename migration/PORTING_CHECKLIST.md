> Historical porting checklist from an earlier audit. It is not an active execution plan; the current acceptance checklist is `LOCAL_SETUP_CHECKLIST.md`. Do not run any embedded Git removal commands.

# Upstream → Codex port implementation checklist

### P0: preserve and inventory

- [ ] Fork, branch, preserve commit hash, license and git history.
- [ ] Run upstream snapshot script and read `references/upstream/CLAUDE.md` and `KNOWLEDGEBASE.md` fully.
- [ ] Enumerate `.claude/skills`, `.claude/hooks`, tool wrappers, docs, tests, examples, `.config/` and dependencies with `git ls-files`.
- [ ] Review upstream `setup.sh` environment detection, MO2 layout, paths and all writes; do **not** run it from the research checkout.
- [ ] Run `prune_preview.py`; extract unique engine and tool knowledge before deleting asset-specific skills.

### P1: Codex runtime

- [ ] Replace `AGENTS.md`, preserve original in `references/upstream/`.
- [ ] Use `.codex/config.toml` in a trusted project; test Codex skill discovery from `.agents/skills/*/SKILL.md`.
- [ ] Port useful Claude skill content into Codex skills, not merely rename directories. Remove `paths:` metadata that clients don't honor; put explicit scope in descriptions.
- [ ] Preserve tool safety with separate checkout, workspace restrictions and supervised gateways. Do not assume Claude hooks port automatically. Add vetted Codex hooks only if their exact schemas are verified and tested, especially on Windows.
- [ ] `git rm` old Claude hooks/settings/instruction files once migrated.

### P2: tool verification

- [ ] Patch **actual** upstream wrappers to use explicit `GAME_ROOT`, load-order path and fixture paths instead of implicit `dirname($0)` if necessary.
- [ ] Respect MO2 load-order virtualization and xelib registry expectations; no silently empty loads.
- [ ] Test xeditlib/xelib, winner, ReSaver, cosave, Papyrus/crash triage, Champollion/Caprica, Spriggit, DevBench availability individually.
- [ ] Read `tests/` for regression gates and modify tests for retained tool set; do not delete all tests to make CI green.

### P3: source and legacy research import

- [ ] Try `uesp_lookup.py` against authorized API; if blocked use a permitted data source; validate licensing and attribution.
- [ ] Index authorized Apocrypha export with message IDs; keep data private/local and out of git.
- [ ] Import original research v2 notes, Ghidra workspace index, SKSE probe protocols and prior negative tests with path-level provenance.
- [ ] Populate mechanisms/claims/contradictions from verified materials rather than speculation.

### P4: live test lane

- [ ] Determine exact SE/AE/VR executable version and SKSE compatibility.
- [ ] Create disposable profile/save and separate diagnostic and vanilla-validation lanes.
- [ ] Verify DevBench can distinguish game alive from server alive.
- [ ] Compare tool responses to known game state, including coverage/denominator and proper actor identity.
- [ ] Define and enforce command allowlist + experiment manifests **outside the model**; do not attach arbitrary mutator MCP tools to unattended runs.
- [ ] Consider SkyLink MCP only after version and tool-schema review.

### P5: seven-day readiness

- [ ] Preflight validates structural files and a working example from each retained tool class.
- [ ] Run short offline Codex cycle, confirm state/frontier actually change and evidence is real.
- [ ] Run several serial supervisor cycles, including forced timeout/bad command/recovery; ensure logs and checkpointing work.
- [ ] Run 6-12 hour supervised pilot to detect context drift, repetitive searches, false claims and source access limits.
- [ ] Only then opt into week-long run with external process supervision, quotas, backups and daily review.
