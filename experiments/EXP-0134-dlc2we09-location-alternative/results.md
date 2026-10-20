# Results

## Direct source findings

- The `DLC2WE09` QUST rows and identity-checked GOG condition evaluator support the bounded expression `GetRandomPercent <= DLC2WE09Chance AND GetStage(MQ105) >= 160 AND GetStage(DLC2MQ06) < 550 AND (GetLevel >= 25 OR GetInCurrentLoc(DLC2SolstheimLocation))`. The location record is `DLC2SolstheimLocation` (`04016E2A`) [EV-0657], [EV-0665]–[EV-0669]. The `DLC2MQ06` comparison is a stage ceiling, not a completion prerequisite.
- The official SCPT parent and `DLC2WEPriorityQuests` / `DLC2WENode` records have the captured event/keyword conditions and no extra level row [EV-0661], [EV-0662], [EV-0664], [EV-0686]. The separate `WETriggerScript` source and placement/property screen show the trigger submits the DLC2 event keyword; the bounded route has no explicit player-level read [EV-0389], [EV-0390].
- `DLC2DRRGjalundPassageWindhelmTopic` (`0203A135`) declares six INFO children. Associating the next six INFO records by DIAL `TIFC` count and serialized file order yields function indices 72/74/58/543 and 74/72 across the group; none is function 80 (`GetLevel`). This association is direct-parser source-order inference, not an xEdit native group export or live-dialogue result [EV-0686].
- Revision-pinned UESP describes paid passage before the cultists are encountered and a different refusal/dialogue-check route after they have been encountered [EV-0687]. The page does not claim that the player is level one or that `DLC2WE09` starts.

## Hypothesis result

Q85-H1 is supported as a conditional static model. The location branch can satisfy the final level/location alternative when the earlier chance and stage conditions are true. Q85-H2 is falsified only within the screened official event selector, trigger, and source-ordered ferry-topic records. Q85-H3 remains unresolved because the source does not show when the QUST list is evaluated or whether the exact Steam level-one event starts naturally.

No `vanilla_candidate` reproduction is claimed. Stage `MQ105 >= 160` reachability while preserving player level 1, the chance-global value, event timing, winning profile, alias fill, and natural QUST startup remain untested. The native xEdit query attempt for an INFO did not produce an accepted native record export; this experiment does not rely on that attempt.

## Causal model and next action

Add M-0202 for the conditional trigger-to-QUST route and retain an explicit no-edge to M-0200/M-0017: these records and event callbacks identify no shared native call, ActorValue, equipment, HitData, ActiveEffect, serialization, or armor-XP primitive. Keep the harder runtime distinction in EV-0260.

Next investigate whether Skyrim's Player Level used by `GetLevel` stays unchanged while skill experience awaits a level-up choice, or changes automatically when a threshold is crossed. Static source/code work can test the competing models; a clean Steam save trace remains the decisive exact-build check.
