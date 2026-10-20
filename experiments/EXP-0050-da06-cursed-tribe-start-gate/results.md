# Results — EXP-0050

## Source result

Skyrim.esm `SMQN 000A0E73` selects main DA06 QUST `0003B681` at `GetLevel >= 9` through GLOB `000A0E71` [EV-0300], [EV-0308]. DA06 has `ENAM=LEVL` and Start Game Enabled clear. The group-aware join covers 76 DA06-owned DIAL topics and 98 INFO children, with 25 bound main-quest TIF scripts; no captured DA06 TIF calls `DA06.Start()` [EV-0308].

The giant-assault trigger is not a quest-start callback. Its placed REFR `0010F6A3` is in Largashbur Exterior04, and its script only changes faction hostility when the player enters while DA06 is not running. The fixed giant reference is XESP-parented to initially-disabled `DA06EnableParent`; the stage-0 QF fragment enables that marker after quest startup. Atub is the main quest's Unique Actor alias and is placed in the Largashbur longhouse. Atub INFO `0008E660` has only a `GetIsAliasRef(alias 0)` condition, and its TIF requests stage 50 without a dialogue stage or level condition. Whether the alias/topic is available while main DA06 is stopped remains unresolved [EV-0308].

The fixed Orc and Atub death callbacks can request DA06 failure stage 255 after player-caused kills below stage 200; four Orc scripts increment the quest counter and register `OnUpdate`, and two kills request stage 255. These are potential failure-state writes, not a demonstrated pre-level-9 start or useful progression. Pre-ritual/cave/hammer scripts require stages 60/80/120, while the grove trigger only changes Yamarz's marker/package. The fixed start-scene trigger's captured `OnTrigger` body is empty [EV-0308].

This narrows the static model: no successful pre-level-9 start or progression was demonstrated within the prepared official masters and captured base-Misc PEX set. However, an Atub stage-50 request and several stage-255 failure requests exist, so their execution against a stopped event-scoped quest remains the key discriminator. EV-0272 is GOG 1.6.1179.0 evidence only; it cannot establish installed Steam 1.6.1170.0 behavior. The native xEdit attempt failed before enumeration due WSL `UtilBindVsockAnyPort`, so these are prepared source-file findings, not profile winners or runtime observations.

## Limits and next discriminator

- Run a clean level-one Steam 1.6.1170.0 test with the complete disposable order and a read-only observer for DA06 running/stage/alias state; enter Largashbur and test ordinary Atub dialogue without forcing state. Compare a level-nine control.
- In a separate disposable run, observe the natural Orc/Atub death failure callbacks without console, stage, level or script intervention.
- No active-profile winner, exact stopped-quest SetStage result, level-one quest progression or vanilla reproduction was established.
- No causal edge to OBJ-2 armor/XP is supported.
