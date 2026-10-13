# Bounded Codex continuation and recovery

The harness supports durable, serial research cycles; it cannot promise a
continuous week of execution. The supervisor is foreground, opt-in, quota- and
timeout-bounded, and must remain offline. It does not launch a game, call
DevBench, mutate saves, or enable an MCP server.

## Before any unattended run

1. Finish the repository finalization checklist and pass
   `python scripts/setup_research.py check`.
2. Review the exact Codex command/configuration and confirm the trusted checkout
   is outside the game install. Keep the only shared Codex config at
   `.codex/config.toml`; do not configure live MCP servers.
3. Confirm `research/FRONTIER.json`, `research/EVIDENCE.json`, `STATE.md`, and
   `research/SESSION_LOG.md` are valid and committed or backed up.
4. Check the Codex CLI identity/version, OS sleep/update behavior, rate limits,
   log disk space, and process supervision. Do not loosen sandbox/approval
   settings to make a run continue.
5. Keep the run offline. Live observations require a separate supervised,
   authorized session and a disposable save.

## Dry run and bounded execution

```sh
python scripts/research_supervisor.py
python scripts/research_supervisor.py --execute --hours 168 --round-minutes 45
# Graceful stop between cycles:
touch .stop-research
```

The default is dry-run. Execution requires `codex` on `PATH`, valid repository
preflight, no existing lock, and explicit `--execute`. Each cycle records JSON
metadata, stdout JSONL, stderr, input hashes, changed durable files, exit code,
frontier IDs, and validation outcome under `research/supervisor-logs/`.
Success requires both a zero process exit and a valid durable core-state
change; an exit code alone is not evidence of progress.

## Recovery after interruption

At cycle start, `research/RECOVERY.json` is atomically set to `running`. A
normal result records the cycle's status and exact artifact base. If the
supervisor is killed, the next invocation detects the stale `running` marker,
sets status to `interrupted`, and adds a recovery entry to the session log.
Before resuming:

1. Inspect the old metadata, stdout, stderr, exit code, and repository diff.
2. Compare the durable file hashes and `STATE.md` checkpoint with the frontier.
3. Decide whether a partial change is valid; do not assume Codex finished.
4. Resolve stale `.research-supervisor.lock` only after confirming no process is
   active; the tool intentionally will not remove it automatically.
5. Continue from the explicit next action in `STATE.md` and
   `research/RECOVERY.json`.

Timeouts kill the Codex process group where supported, write exit code 124, and
count toward the bounded failure limit. Malformed research data is a failed
cycle and remains available for review; it is never silently repaired or
accepted.

## Review cadence and limits

Review run metadata and state diffs after each cycle. Every five meaningful
investigations, synthesize shared mechanisms and update the graph. A human
reviewer should check false claims, repetition, source access, and session
drift before extending the budget. Do not interpret a supervisor process that
is alive as a Codex session that is making valid progress.
