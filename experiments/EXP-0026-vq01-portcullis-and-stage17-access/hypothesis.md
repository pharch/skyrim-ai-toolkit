# Hypothesis — EXP-0026

## Parent question

Q-0021 asks whether VQ01's Crypt02 stage-17 trigger REFR `0200FB21` can be reached and used at numeric level 1 before the VQ00/VQ01 stage-10 setup.

## Competing models

- **H1 — player-only crossing:** a vanilla collision route crosses the quest-dependent rubble and reaches the trigger before VQ01 stage 10; the trigger may then start or advance VQ01.
- **H2 — ordinary route setup:** ordinary access follows Awakening and its lever/rubble setup; the installed records and generic gate script do not themselves establish a player-only crossing.
- **H3 — trigger semantics separate:** reaching the stage-17 reference may still fail to produce a running quest, useful progression or filled aliases when VQ01 is stopped.

## Gate-script discriminants

The portcullis reference's parent, raw XESP bytes, attached script and linked collision keyword distinguish an explicit quest transition from a physical gate action. An exact read-only initial-state capture is still needed to distinguish a disabled child from an activatable child. Keep record enable state separate from physical reachability through the rubble and from trigger callback/quest results.
