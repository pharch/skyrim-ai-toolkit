# Interactive research continuation and recovery

Start research in an interactive Codex session from the trusted repository
root. Durable repository state supports context changes and later restarts; it
does not promise uninterrupted execution or bypass platform session limits.
Do not schedule automatic fresh Codex threads or kill a useful analysis at a
fixed interval.

## Before a research session

1. Read `AGENTS.md`, `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`,
   `research/FRONTIER.json`, and `protocols/TOOL_ROUTING.md`.
2. Run `python3 scripts/python_env.py run scripts/setup_research.py check` and inspect the exact current
   checkpoint and working-tree changes.
3. Select one ready frontier item. Record its rival models, predicted
   discriminants, tool/source, and exact next action before collecting data.
4. Keep the work offline unless the Windows AE preflight and the relevant
   read-only tool prerequisites pass. Live-game work requires a separate,
   supervised protocol and a disposable save.

## Checkpoint before a boundary

Before a context change or ending a session, update `STATE.md`,
`research/FRONTIER.json`, and `research/SESSION_LOG.md` with:

- what was actually inspected and the source/build identity;
- raw evidence locations and hashes, plus the claim or hypothesis status;
- the exact next command or observation, with its prerequisites;
- blockers and an independent offline continuation route.

For a potentially interrupted investigation, keep its transaction resumable and
use `python3 scripts/python_env.py run scripts/research_state.py validate`
before resuming. If
`research/RECOVERY.json` says `running`, mark it interrupted with
`python3 scripts/python_env.py run scripts/research_state.py recover --root .`, inspect partial outputs
and the durable-state diff, and resume only from the recorded `next_action`.
Interruption is not evidence of completion.

The consolidated bootstrap diagnostic is the one exception: the runtime
contract permits `python3 scripts/harness_doctor.py all` to start with system
Python so it can report a missing or invalid repository `.venv`. Research
entrypoints and validators use the strict dispatcher after the pinned Python
3.12 environment passes.

## Periodic synthesis

After several meaningful investigations, inspect shared functions, ActorValues,
effects, event gates, inventory state, numeric operations, and serialization
edges in `research/KNOWLEDGE_GRAPH.md`. Add a successor only when its question
has a discriminating observation and an actionable source/tool route. Preserve
negative results and contradictions; do not close a question from missing or
incomplete output.

These procedures support durable work in an interactive session. They do not
establish a current Windows runtime or provide unattended access to live-game
mutators.
