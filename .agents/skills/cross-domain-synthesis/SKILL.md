---
name: skyrim-cross-domain-synthesis
description: Periodically synthesize Skyrim reverse-engineering findings across quests, combat XP, ActiveEffects, enchanting and serialization to discover shared engine primitives and new level-one exploit candidates.
---

# Synthesis pass

After five meaningful investigation results, a major contradiction, or surprising behavior:

1. Review recently changed claims, mechanisms, observations and raw evidence.
2. Search for shared native calls, conditions, event dispatch, perk entry points, ActorValues, magic effect lifetimes, floating point operations, reference identity, or save/changeform pathways.
3. For each proposed edge, distinguish verified dependency from analogy; attach source IDs.
4. Ask which newly established branch/control point may serve OBJ-1 or OBJ-2 even if discovered in alchemy or enchanting.
5. Generate frontier entries with exact falsifiable predictions and feasible tests, not vague subjects.
6. Rebalance the frontier while preserving negative findings and the P0 priority hierarchy.
7. Update `research/KNOWLEDGE_GRAPH.md`, `ROADMAP.md` and short `STATE.md`.
