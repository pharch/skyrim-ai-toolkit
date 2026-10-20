# QUST readiness flag provenance

**Frontier:** Q-0056, OBJ-1. **Status:** bounded static GOG/source component complete; later dispatch timing and Steam runtime remain open.

EV-0316 shows that GOG's TESQuest QUST parser writes the first U16 of serialized `DNAM.General.Flags` to `TESQuest+0xDC`. TES5Edit `dev-4.1.6` names bit 0 `Start Game Enabled`; DA04's source flag is set while DA02, DA06, and DA09 clear it. A separate virtual routine at TESQuest vtable slot 19 can clear bit 0 after loading, but its dispatch timing is unknown.

This is a load-time field map, not a level-one bypass or Steam result. Follow-up Q-0057 investigates when the slot-19 method runs and whether its mutation precedes any naturally reached `Quest.SetStage` callback.
