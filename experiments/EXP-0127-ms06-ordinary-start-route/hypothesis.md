# Competing models

- **H1 — ordinary route starts MS06 below level 10:** The start-game-enabled MS06Start helper fills Falk's note or exposes dialogue/scene triggers that cause the main MS06 quest to start or progress at level 1, despite the SMQN `GetLevel >= 10` node.
- **H2 — helper reaches a guarded SetStage request:** The helper supplies a note or dialogue callback, but the stopped main MS06 quest has a serialized `LEVL` event field and lacks `Start Game Enabled`; the GOG registered `Quest.SetStage` entry predicate therefore rejects that request in the observed stopped-state inputs. This does not predict Steam behavior.
- **H3 — a separate ordinary writer starts the main quest:** Another dialogue, INFO callback, scene, placed reference, or attached script independently invokes `Start`, `SetStage`, or an equivalent transition that is not covered by the note path.

## Predicted discriminants

| Model | Source/native observation | Runtime discriminator |
|---|---|---|
| H1 | A player-accessible helper path reaches main MS06 and the target-build startup guard accepts it; any stage or alias dependency is explicit. | Clean level-1 note/dialogue interaction changes MS06 running/stage and relevant aliases with level preserved; no-trigger control does not. |
| H2 | The direct writer is found, but the main QUST fields fail the inspected GOG initial guard; no independent source writer is found in the bounded official-five census. | On verified Steam, note interaction leaves MS06 stopped until a separate eligible event; this must be observed. |
| H3 | A distinct source-backed caller to main MS06 or its startup helper is identified, with conditions and callback receiver resolved. | Natural clean level-1 execution of that caller starts the target quest/encounter and reproduces. |

