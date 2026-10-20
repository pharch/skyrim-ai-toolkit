# EXP-0020 protocol

## Competing models and predicted outcomes

- **H1 — ordinary pre-gate trigger:** Silus and Madena naturally enter the exterior trigger below level 20. The trigger's `SetStage(7)` waits for/starts DA07intro as needed, stage 7 starts its intro scene, and the player remains level 1.
- **H2 — trigger is not naturally reached before the helper:** the reference is disabled/unloaded or ordinary NPC schedules never place both actors in its trigger volume before the level-20 helper. A clean level-one route leaves DA07intro stopped with no stage-7 transition.
- **H3 — partial quest transition:** the trigger can issue `SetStage(7)` and start or stage DA07intro, but required aliases/scene participants fail to fill or the scene does not complete; journal stage/state change alone is not functional quest/encounter initiation.

Static discriminants are the placed reference's enable-parent/cell data, trigger-script actor filters and target-count logic, direct quest-stage writers, stage-7 fragment mapping, alias requirements, and scene participants. Runtime discriminants must separate trigger activation, quest running, stage completion, alias fill, scene start, and useful player access.

## Read-only static procedure

1. Use the verified Steam AE target identity only for installed-record provenance; keep the official five-master file scope distinct from a complete profile order.
2. Validate the raw FormID candidate through its REFR/ACTI/NPC_/QUST fields and decode cell-group context. Do not interpret a byte hit as a reference without its record/subrecord.
3. Inspect the attached trigger PEX and parent script. Confirm the exact actor bases, required-count condition, `SetStage` properties, and disable behavior.
4. Map stage 7 to its QF fragment and inspect its SCEN calls and relevant aliases. Treat Papyrus Index/Creation Kit documentation as API guidance, not as Steam execution evidence.
5. Record any missing PEX source, native xEdit launch failure, and unresolved alias/scene semantics rather than substituting an unverified negative.

## Future natural-play discriminator

After the exact executable and complete active order are verified, use a clean level-one save with no console state forcing, script injection, or altered plugin. Record a time-matched no-trigger baseline and player numeric level. Observe ordinary travel and NPC movement in DawnstarExterior04 without moving either NPC or activating a debug trigger. After the natural route, capture DA07StartNode, DA07/DA07intro running/stage state, pamphlet alias fill/reference, DA07IntroScene state, visible journal/dialogue outcome, and player level. Read-only state queries may be used after the ordinary route; never issue `SetStage`, `StartQuest`, `SetLevel`, or another mutator. Preserve before/after saves as copies and analyze only through the documented read-only save route. A journal entry alone does not prove alias fill or encounter initiation.

If no supported read-only method can distinguish running/stage/alias state on the exact build, report that specific measurement gap and preserve observable outcomes; do not relabel a script injection or console-forced state as a vanilla result.

## Controls and exclusions

The control is the same clean level-one state held for the same game-time interval away from the trigger. Keep the active order identical between control and candidate. Do not use staged quests, forced NPC positions, console-started scenes, altered scripts, or a modified profile as proof of a vanilla route. No save, plugin, archive, or game file is modified by this protocol.
