# TES5Edit condition-function schema notes

Source: `TES5Edit/TES5Edit`, branch `dev-4.1.6`,
[`Core/wbDefinitionsTES5.pas`](https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas).
The file defines the condition-function index/name and parameter-type table.
These names are schema labels for the captured CTDA function indices; they do
not resolve plugin-local operands, script-variable values, runtime truth, or
profile winners.

Observed indices in the MG01/MG02 DIAL/INFO screen are:

| Index | Schema name | Parameter type(s) | Source lines |
| ---: | --- | --- | --- |
| 1 | GetDistance | Reference | 2570 |
| 14 | GetActorValue | ActorValue | 2583 |
| 47 | GetItemCount | InventoryObject | 2614 |
| 50 | GetTalkedToPC | — | 2620 |
| 58 | GetStage | Quest | 2625 |
| 59 | GetStageDone | Quest, QuestStage | 2627 |
| 67 | GetInCell | Cell | 2642 |
| 71 | GetInFaction | Faction | 2650 |
| 72 | GetIsID | BaseObject | 2652 |
| 80 | GetLevel | — | 2663 |
| 130 | GetPCIsRace | Race | 2711 |
| 131 | GetPCIsSex | Sex | 2712 |
| 182 | GetEquipped | InventoryObject | 2769 |
| 249 | IsInDialogueWithPlayer | — | 2820 |
| 264 | HasSpell | EffectItem | 2837 |
| 359 | GetInCurrentLoc | Location | 2906 |
| 448 | HasPerk | Perk, Integer | 2983 |
| 566 | GetIsAliasRef | Alias | 3085 |
| 629 | GetVMQuestVariable | Quest, String | 3173 |
| 630 | GetVMScriptVariable | Reference, String | 3175 |

The CTDA decoder recognizes function index 80 as `GetLevel`; the separate
EV-0321 census screens that function index across the exact five official
masters and reports zero malformed CTDA lengths. The College dialogue pass
also checks DIAL and INFO CTDAs directly, including conditions whose values
remain quest-stage, alias, inventory, location, script-variable, or other
non-level predicates.

## Door references

The XLOC schema stores the lock level in byte 0 and key FormID in bytes 4–7;
XTEL stores a paired-door reference and destination transform. The local
TES5Edit `dev-4.1.6` source note is EV-0269; primary schema definitions are
[XLOC](https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas#L9490-L9506)
and [XTEL](https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas#L9413-L9419).
The values establish serialized lock/key and pair references, not the runtime
result of attempting to open or traverse a door.
