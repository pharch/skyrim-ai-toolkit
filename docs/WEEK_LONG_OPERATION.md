# Seven-day Local Research Run: Practical Operation

A week-long autonomous investigation requires **two separate things**: (1) a durable research system that can survive context resets and (2) a runtime supervisor that re-invokes Codex after each normal turn/CLI exit. Repeating "never stop" in AGENTS.md is not a runtime guarantee. `/goal` supports persistent continuation in compatible interactive Codex builds, but still has budgets, stop conditions, and access limits. The optional `scripts/research_supervisor.py` performs bounded serial CLI re-invocations so no single session must last seven days.

## Prior to running

- Pin both upstream commit and current fork commit; record `codex --version` and tool versions.
- Ensure repo is outside Skyrim installation; validate path routing and independent permissions.
- Set up a separate, disposable game profile/save. Back up saves externally. Ensure live MCP tools are **not configured** until safe read-only gateway has passed evaluation.
- Install prerequisites for retained tools; validate one positive and one negative fixture. Confirm correct game build and MO2/stock load order.
- Import and index authorized Apocrypha log locally; verify UESP access/permissions. Read-only source lookup should not depend on live game.
- Create initial claims and frontier; check `STATE.md` has specific next tasks. Run preflight `python scripts/validate_overlay.py`.
- Commit baseline. Inspect sandbox/approval and the tool whitelist; in unattended mode approval prompts cannot be answered. Do not broaden privileges to make a stuck agent continue.
- Set OS sleep/updates/network and Codex quota expectations consciously; the supervisor cannot bypass service limits.

## Interactive research mode (best for setup/testing)

```bash
npm install -g @openai/codex@latest
codex --version
codex
```

Then paste this **optional** persistent interactive Goal (requires a compatible build):

```text
/goal Expand the evidence-backed causal model of vanilla Skyrim with priority on
(1) reproducible level-one access to level-gated quests/encounters and
(2) no-armor-skill-XP incoming hits while worn armor still works.
Use NORTH_STAR.md and the FRONTIER as the verification surface. When a branch
fails, log it and advance another. Keep objective and cross-system synthesis
running. Record every evidence artifact and resumable checkpoint. Stop for
user authorization of live mutations, protected files, or a genuine global
blocker, not a locally exhausted branch.
```

Goals can stop on budget or hard blockers. Do not assume this alone guarantees a week.

## Unattended offline-first mode (opt-in)

```bash
python scripts/research_supervisor.py                 # inspect dry run
python scripts/research_supervisor.py --execute --hours 168 --round-minutes 45
# To request graceful termination between cycles, create .stop-research
```

The supervisor calls **fresh** Codex CLI sessions in sequence using a stored repo-state handoff, logs stdout JSONL, stderr and exit code, and stops after bounded repeated failures. It does not quietly elevate permissions, access your live save, create mod files inside game directory, or retry failed live actions. CLI/API availability, quotas, network/sleep and local process lifetime can prevent a continuous run.

## Cadence

- Every investigation: record evidence/provenance, contradiction/claim updates, frontier changes, and the next action.
- Every ~5 meaningful investigations: cross-system synthesis and priority rebalance.
- After any surprise/invalid probe: audit instrument, game version, totals and denominator before updating the game model.
- Daily (operator review): audit `research/supervisor-logs/` and `research/SESSION_LOG.md`, negative results and dubious certainty; optionally authorize a new live experiment batch.
- After run: consolidate state into a clean synthesis and use a separate reviewer agent to challenge unsupported claims.

## Human-in-the-loop live experimentation

Until an independent MCP gate exists, keep the week-long run offline/read-only and perform in-game tests in separately authorized supervised windows. Later a restricted, audited gateway can automatically execute only tagged, reversible experiments on disposable saves, with a watchdog, rollback and immutable before/after captures.
