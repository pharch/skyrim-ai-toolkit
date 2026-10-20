# EXP-0018 results

## Direct observations

- DA14Start VMAD maps stage 30 to `Fragment_5`, stage 50 to `Fragment_6`, and stage 70 to `Fragment_2` (EV-0264).
- `QF_DA14Start` Fragment_5 and Fragment_6 call `Start()` on the first and second Sam drinking SCEN properties respectively. Fragment_2 calls `DA14.SetStage(5)` and `self.Stop()` (EV-0264).
- The two scene scripts reference DA14Start alias 6; their Fragment_0 methods call `GetOwningQuest().SetStage(40)` and `GetOwningQuest().SetStage(60)`. No explicit DA14/DA14Start `Start()` call appears in those scene PEX bodies (EV-0264).
- The cross-master scalar VMAD scan found portal/update references that check DA14 stage 200, plus a Dragonborn QUST property `DA14Gleda` bound to DA14 alias 3. The latter's script PEX body is unavailable in the tested source route (EV-0264).

## Assessment and boundary

The resolved scene sequence is downstream of DA14Start running and does not itself show a start bypass. The Dragonborn alias link leaves a possible caller unresolved; it cannot be classified as a Start/SetStage route. No level-one transition, level preservation, active-profile winner, or gameplay outcome was observed. Q-0002 remains unresolved; EV-0260 records the missing live prerequisites.

## Next discriminant

Recover and inspect `DLC2DialogueRavenRockQuestScript` from an identified supported source, then determine whether it starts/sets DA14 or merely consumes the alias. Keep the level-one control/transition test separate and wait for a verified target profile, disposable save, and read-only observer before any live measurement.
