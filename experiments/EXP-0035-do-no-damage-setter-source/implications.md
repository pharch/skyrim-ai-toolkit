# Implications

The only observed nonzero `doNoDamage` setter path is not directly called by the GOG hit resolver. It is reached from a process-level-gated action-data callback and reads an unnamed bit from parameter slot 7. This narrows the mechanism, but the callback may still be dispatched for an attack-related action; the current evidence does not establish its gameplay reachability.

The whole-hit clear remains a cancellation/no-damage path and cannot establish functional armor protection. Keep protection and zero-XP outcomes open pending a natural qualifying hit and exact Steam measurement. No causal edge to OBJ-1 is supported. Q-0028 should resolve the parameter schema or the callback table owner if a tested read-only route exists.
