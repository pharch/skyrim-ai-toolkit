---
name: skyrim-cross-domain-synthesis
description: Periodically synthesize Skyrim reverse-engineering findings across quests, combat XP, ActiveEffects, enchanting and serialization to discover shared engine primitives and new level-one exploit candidates.
---

# Skyrim AE cross-domain synthesis

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

After five meaningful investigation results, a major contradiction, or surprising behavior:

1. Review recently changed claims, mechanisms, observations and raw evidence.
2. Search for shared native calls, conditions, event dispatch, perk entry points, ActorValues, magic effect lifetimes, floating point operations, reference identity, or save/changeform pathways.
3. For each proposed edge, distinguish verified dependency from analogy; attach source IDs.
4. Ask which newly established branch/control point may serve OBJ-1 or OBJ-2 even if discovered in alchemy or enchanting.
5. Generate frontier entries with exact falsifiable predictions and feasible tests, not vague subjects.
6. Rebalance the frontier while preserving negative findings and the P0 priority hierarchy.
7. Update `research/KNOWLEDGE_GRAPH.md`, `ROADMAP.md` and short `STATE.md`.

Do not promote a shared name or a coincident state transition into a causal
edge. For each proposed connection, state the observable that could disprove
it and keep edition/build provenance attached to both endpoints. Mark an edge
as an analogy until a shared call path or discriminating experiment supports
causality.

## Validation and provenance

- Read source IDs from `research/EVIDENCE.json` and inspect linked claim,
  mechanism, and experiment records. After edits, run
  `python3 scripts/python_env.py run scripts/validate_research.py` and
  `python3 scripts/python_env.py run scripts/research_state.py validate`.
- Put the proposed edge, its two source IDs, the causal/analogy status, and a
  falsifying observation into `research/KNOWLEDGE_GRAPH.md`, `CLAIMS.md`, and
  `FRONTIER.json`; summarize the change in `STATE.md` and `SESSION_LOG.md`.
- If a source, native call edge, or compatible build is missing, record the
  exact gap and keep the connection unsupported. Validation failure is not
  permission to promote an analogy.
