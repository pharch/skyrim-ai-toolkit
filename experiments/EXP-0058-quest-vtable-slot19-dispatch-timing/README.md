# TESQuest slot-19 readiness-bit dispatch timing

**Frontier:** Q-0057, OBJ-1. **Status:** completed as a bounded GOG static load-finalization trace; first natural callback order remains inferred.

EV-0316 maps TESQuest vtable slot 19 to `FUN_1403c8420`; that method can clear `TESQuest+0xDC.0` after the QUST parser copies serialized `Start Game Enabled`. EV-0318 resolves the GOG file-load path: the record buffer reaches TESQuest slot 6 (`FUN_1403c7a50`), the parsed quest is registered in the FormType-indexed manager, and a pass after the per-file loop includes QUST type `0x4D` and dispatches slot 19. This falsifies the model that slot 19 runs only during later quest lifecycle transitions.

The captures do not directly place the first natural `Quest.SetStage` callback relative to this load-manager return. That ordering remains a load-order inference; Steam AE 1.6.1170.0 behavior, target-quest callback reachability, useful access, and level-one progression remain open. No OBJ-2 causal edge is supported.
