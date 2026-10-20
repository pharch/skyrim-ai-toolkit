# Predicted outcomes

| Observation | H1: attacker-side cancellation | H2: armor-linked protection |
|---|---|---|
| Process flag | `AIProcess.middleHigh.doNoDamage` gates the path | A worn-armor/receiver-protection value gates the path |
| Actor predicate | Actor `IsInCombat` and AIProcess `ignoringCombat` determine whether clear occurs | Combat-state check is secondary to an armor/AV39 predicate |
| HitData effect | One 8-byte store clears both `totalDamage` and `physicalDamage` | Damage fields are reduced in a way tied to armor while protection remains attributable |
| Receiver skill path | Zero points are rejected, but the hit is a no-damage/cancel state | A qualifying incoming hit retains measurable protection while armor XP is suppressed |
| Current result | Supported statically; natural writer still open | No direct evidence; protection/XP control not established |
