# Hypothesis — EXP-0025

## Question

Does the VQ01 Book alias provide an ordinary pre-gate bootstrap, or is its callback owned by the main quest and its forced book reference downstream of VQ01 stage-10 setup? Separately, can the stage-17 trigger reference in Crypt02 be reached and used before that setup?

## Competing models

- **H1, book bootstrap:** the base book or an already-filled alias can call `SetStage(17)` before VQ00 starts.
- **H2, quest-owned book path:** the callback belongs to VQ01's main-quest alias; the placed reference is enabled by VQ01 stage 10 and pickup also checks stage 15. Runtime alias-fill timing is a separate unknown.
- **H3, independent stage-17 trigger:** a player-only route reaches the Crypt02 trigger before VQ01 stage 10 and its script progresses the stopped quest.
- **H4, downstream or ineffective trigger:** access requires the VQ01 setup chain, or the trigger's script/start semantics do not produce useful progression.

## Predicted discriminants

The QUST owner, alias/reference mapping, serialized Papyrus properties, stage fragment, XESP parent and cell placement discriminate H1 from H2 at the static layer. The trigger REFR's script properties and the entrance/door enable chain bound H3/H4, but only a clean level-one candidate/control can establish physical reachability, runtime script execution, VQ01 state changes and useful progression. See EV-0260 for missing runtime prerequisites.
