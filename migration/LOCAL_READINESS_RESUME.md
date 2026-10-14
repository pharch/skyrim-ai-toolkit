# Local Research Readiness Resume

```yaml
phase: Final local verification and external handoff
current_criterion: All 74 criteria classified; 64 PASS, 10 BLOCKED_EXTERNAL, 0 pending
last_successful_test: Full stdlib unittest suite passed 139 tests (EV-0145); Ghidra attestation suite passed 9 tests (EV-0140); research, transaction, overlay, compileall, Markdown audit passed after final checkpoint synchronization (EV-0150; prior passes EV-0147/EV-0149), and staged pre-push checks passed (EV-0148 plus final rerun)
current_tool_or_target: Steam AE SkyrimSE.exe ProductVersion 1.6.1170.0; no live game session; Ghidra session 40253 terminated with incomplete analysis
actual_blocker_if_any: Selected MO2 profile/load order is unknown; WSL Windows process bridge fails before Ghidra; Observer DLL/live SKSE handshake and real save/ReSaver are unavailable; UESP dump provenance and Windows/remote CI are unavailable; separate Codex-context recovery was rejected by review.
next_exact_action: Commit the reviewed local changes without pushing. For continued research, hand off the ten external dependencies. After WSL interop is restored, run `python3 scripts/python_env.py run tools/ghidra_probe.py --project-dir .local/readiness/ghidra/project_AE_SkyrimSE_1_6_1170_longanalysis --project-name AE_SkyrimSE_1_6_1170_longanalysis --timeout 300` and preserve the raw result. Set PLUGINS_TXT to the selected MO2 profile's explicit plugins.txt, then rerun `python3 scripts/python_env.py run tools/ae_preflight.py`. Provide a copied disposable .ess/co-save pair and source provenance before real save analysis. No active native session remains.
working_tree_and_commit: branch glitch-hunting-setup; audited starting HEAD e13ae4b253a6f5fd66f0f8abc3e49e6f9b29a6cc. Preserve the pre-existing deletion of migration/RESEARCH_READINESS_MISSION.md and untracked migration/LOCAL_RESEARCH_READINESS_MISSION.md.
```

## First deep research session

Open the interactive local Codex session in this checkout and use [`docs/RESEARCH_START_PROMPT.md`](../docs/RESEARCH_START_PROMPT.md). Start by reading `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`, `research/FRONTIER.json`, and `protocols/TOOL_ROUTING.md`. Continue investigating after every result; a checkpoint is not a stop condition.
