# EXP-0020 results

## Direct observations

- REFR `000B1403` (`DA07IntroTrigger`) is in CELL `00008E96` (`DawnstarExterior04`) under the Skyrim.esm exterior-cell groups. Its direct REFR capture lists no XESP enable-parent field; the record's flags are zero.
- ACTI `0009C8DF` attaches `defaultSetStageOnEnter`. Serialized properties point `myQuest` at DA07intro, set `stage=7`, configure `TriggerActor1=Madena` and `TriggerActor2=Silus`, require all targets in the trigger, and request disable after triggering.
- Parent `defaultOnEnter` compares entering actor bases against configured references and calls TriggerMe when the target count satisfies the all-target condition. The specialized TriggerMe calls `myQuest.SetStage(7)` before the parent disable behavior.
- DA07intro QF maps stage 7 to Fragment_6; that fragment calls `DA07IntroScene.Start()`.
- DA07intro alias 0 is Silus (`NPC_000240CC`) and alias 2 is Madena (`NPC_0001361D`); both are unique-actor alias assignments without alias CTDA conditions. Under the TES5Edit SCEN schema, `SCEN:00094D8A` has owner quest DA07intro and actor IDs 2 and 0, matching those aliases. No SCEN CTDA was present in the raw record. If the scene completes, its Fragment_4 calls owning-quest `SetStage(10)`.
- The Papyrus Index transcription of the Quest.SetStage API says the call waits for quest startup when it must start the quest. Its linked Creation Kit Wiki page returned HTTP 403. This is secondary documentation, not proof of Steam engine behavior.
- EV-0266 records the exact file hashes and parser/extraction routes. The native xEdit REFR query failed before SSEView under WSL Windows interop; direct-parser output is not a native xEdit export.

## Assessment

The placed, level-unconditioned script path is a substantive pre-gate candidate because the actor pair and reference are in DawnstarExterior04, and the requested stage starts a scene whose actor IDs match the Silus/Madena aliases. A completed scene has a stage-10 follow-on. It is not yet evidence that the actors naturally co-enter the trigger at level 1 or that the exact Steam runtime starts/completes the scene from a stopped quest. H1, H2, and H3 therefore remain open; no vanilla reproduction has occurred.

## Next discriminant

Use a clean level-one natural-play candidate/control pair with exact target order. Observe normal Silus/Madena movement through the mapped trigger without moving actors, then capture DA07StartNode, DA07intro running/stage state, alias fill, scene start/completion, and player level through read-only state observation. EV-0260 records that the current save/profile/Observer prerequisites are absent. If the available read-only tool cannot expose the required quest state, preserve that exact gap and continue independent P0 work.

## Cross-domain assessment

No causal edge links this quest trigger to incoming HitData, armor mitigation, or armor/Block skill credit. The records/scripts share no identified AV, native routine, or serialization primitive with M-0017/M-0018.

## Added static actor-readiness screen (EV-0267)

The exact five-master placement screen found Silus `ACHR 000240CE` initially disabled in `DawnstarSilussHouse` and Madena `ACHR 0001A6C3` in `DawnstarTheWhiteHall`, with no second placed actor reference for either base. DA07intro stage 0 is the known writer that enables/moves Silus to his marker and moves Madena to hers. This disfavours ordinary pre-gate actor co-entry from the screened initial state; it does not rule out another start/enable writer, a profile override, or a player glitch. No co-entry or live transition was observed.

The independent Museum-trigger route is now tracked in Q-0020 / EXP-0021. It may start DA07intro through a separate scene path if a player-accessible house-entry glitch exists, so EV-0267 is not a global negative for DA07 pre-gate initiation.

## Current bounded result

The static actor-placement branch is locally complete. Keep the clean level-one ordinary-travel control as an unresolved runtime discriminator if the Museum route does not account for the actor readiness state. EV-0260 records the missing profile, save, and read-only Observer prerequisites.
