# Three-investigation continuity pilot

This pilot turns three distinct source-derived questions into independently resumable experiments. The source checkout remains a private local alias and was not written.

| Investigation | Objective | Current result | Resume artifact |
|---|---|---|---|
| EXP-0008 | OBJ-1 quest initiation | 109 source-reported level conditions; DA07 and Haknir alternate writers remain reachability hypotheses. | `experiments/EXP-0008-quest-gate-continuity/` |
| EXP-0009 | OBJ-2 armor hit XP | A blocked-hit branch reportedly skips AV11/12 but may award AV9. | `experiments/EXP-0009-armor-block-hit-routing/` |
| EXP-0010 | OBJ-2 WICast / Marked for Death | Candidate event/list/AV39 chain identified; actor, target, counter, and location remain unobserved. | `experiments/EXP-0010-wicast-marked-death-armor/` |

## Restart check

The durable packet links `STATE.md`, `research/FRONTIER.json`, `research/SESSION_LOG.md`, and each experiment's next action. The checkpoint recovery helper in `scripts/research_state.py` marks a running transaction interrupted and requires an explicit next action; a fixture test verifies this behavior without changing the real checkpoint. This validates the recovery code path; a fresh independent model-context restart has not been performed. No user test has been scheduled because executable identity and active load order remain unverified.

## First three actions after external prerequisites become available

1. Run `python3 scripts/python_env.py run tools/ae_preflight.py` against the configured executable and selected full AE profile; preserve ProductVersion, executable hash, and explicit plugins list.
2. Resolve the source-reported DA07/Haknir candidate writer with the Python plugin reader where possible; winning-override resolution remains blocked until a tested Python xEdit route exists. Keep any raw local output under ignored `.local/` and summarize the result or scoped negative in EXP-0008.
3. Verify the blocked receiver function against the matching build and prepare EXP-0009 controls; only then assess whether EXP-0010's WICast location is ordinarily reachable.
