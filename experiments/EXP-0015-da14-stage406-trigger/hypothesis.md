# Competing models

## H1 — Pre-gate alternate trigger

An ordinary level-one route reaches `DA14Interior` before `DA14Start`; touching REFR `00000EC8` calls `DA14.SetStage(406)` and produces a real quest-state change that starts or advances DA14.

## H2 — Downstream interior trigger

The trigger is inside the quest interior and only follows a quest-controlled portal route. The observed Morvunskar destination door is initially disabled, while stage 406 is not defined in the inspected DA14 QUST records. A separate scripted/native entry path remains possible but is not established.

## Discriminant

Static evidence should resolve the trigger's containing cell, all XTEL entry/exit links, destination enable state, target quest and stage table. If H1 survives, a clean level-one test must observe a natural transition without console, injected script, or altered plugin. If H2 fits the records, search for independent ordinary `MoveTo`, `Enable`, or quest-start writers before selecting a runtime route.
