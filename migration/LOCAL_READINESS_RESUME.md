# Local Research Readiness Resume

> Historical resume note for the prior setup mission. Continue from
> `migration/FINAL_ALIGNMENT_RESUME.md` for the current alignment pass.

```yaml
phase: Final local verification and external handoff
current_criterion: All 74 criteria classified; 67 PASS, 7 BLOCKED_EXTERNAL, 0 pending
last_successful_test: Native Ghidra lookup/xref/disassembly/decompilation query passed (EV-0152); sanitized independent Codex context resumed correctly (EV-0153); AE Observer Release DLL built and exports verified (EV-0154/EV-0155); final post-closeout stdlib unittest suite plus research, transaction, overlay and compileall validators passed (EV-0164); Markdown inventory, staged audit and cross-record checks are EV-0161–EV-0163
current_tool_or_target: Steam AE SkyrimSE.exe ProductVersion 1.6.1170.0; Ghidra query available; read-only Observer DLL built but not deployed; no live game session
actual_blocker_if_any: Selected MO2 profile/load order is unknown; no live AE+SKSE handshake or permitted real save/ReSaver input; UESP snapshot provenance and Windows/remote CI are unavailable.
next_exact_action: Set PLUGINS_TXT in ignored config/local.env to the selected MO2 profile's explicit plugins.txt and run `python3 scripts/python_env.py run tools/ae_preflight.py`. Only after it passes, run a real load-order-aware xEdit winner query. Then provide a copied disposable .ess/co-save pair with provenance before save analysis; for C12, stage only the read-only Observer in a disposable profile and manually start verified AE+SKSE for a handshake. The Ghidra query capability is verified; for OBJ-2, target an actual incoming-hit/skill-use routine rather than the generic sample near image entry. No active native process remains.
working_tree_and_commit: branch glitch-hunting-setup; starting HEAD e13ae4b253a6f5fd66f0f8abc3e49e6f9b29a6cc; final readiness audit and external handoff are complete; preserve the pre-existing deletion of migration/RESEARCH_READINESS_MISSION.md and untracked migration/LOCAL_RESEARCH_READINESS_MISSION.md; do not push.
```

## First deep research session

Open the interactive local Codex session in this checkout and use [`docs/RESEARCH_START_PROMPT.md`](../docs/RESEARCH_START_PROMPT.md). Start by reading `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`, `research/FRONTIER.json`, and `protocols/TOOL_ROUTING.md`. Continue investigating after every result; a checkpoint is not a stop condition.
