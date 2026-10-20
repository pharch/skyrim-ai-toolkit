# Expected discriminants

| Model | Source observation | Live discriminator |
|---|---|---|
| H1: ordinary helper route is downstream | Main DA05 stage 50 maps to a fragment that sets helper stage 10; helper Start Game Enabled is clear; INFO condition references helper alias 57. | Before main DA05 stage 50, a clean level-one control shows helper running/stage state, alias 57, and INFO availability. Ordinary DA05 initiation then changes those fields. |
| H2: helper can start independently | A player-reachable source starts helper QUST or fills alias 57 without main DA05 stage 50. The callback then sets helper stage 20; its fragment kills the alias actor and requests main DA05 stage 60. | A natural interaction from a clean level-one save before main DA05 stage 50 exposes INFO `00095585`, changes helper state, and produces the mapped main stage-60 transition while level remains 1. |
| H3: fresh-state SetStage is guarded | The source path requests main DA05 stage 60, but Steam startup/readiness/alias conditions may reject or incompletely process that request. | If the callback runs, a read-only capture distinguishes main DA05 running state, current/completed stages, aliases, helper stage, hunter state, and player level before and after. |

Console stage forcing or injected scripts can diagnose state transitions but cannot validate a vanilla candidate.
