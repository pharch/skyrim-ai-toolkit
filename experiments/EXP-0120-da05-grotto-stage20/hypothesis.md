# Competing models

- **H1, ordinary downstream route:** main DA05 stage 50 starts the Grotto helper at stage 10; its forced Hunter alias and INFO are available only after that route. The helper stage-20 fragment then kills the aliased hunter and requests main DA05 stage 60.
- **H2, independent helper route:** a player-reachable vanilla source starts the helper or fills alias 57 before main DA05 stage 50. The INFO can then set helper stage 20 and reach the main stage-60 request from an earlier state.
- **H3, guarded fresh-state transition:** even if the INFO callback runs, Steam AE may not start or fully initialize stopped main DA05 when the helper fragment requests stage 60.

The mapped source establishes the owner quest, stage receivers, and ordinary main-to-helper route. It does not establish dialogue availability, alias fill, callback execution, or Steam `Quest.SetStage` behavior. No raw reference alone proves a call executes.
