# Competing models

- **Q66-H1:** the mapped Fort dialogue callback's `Quest.SetStage(10)` conditionally starts stopped VQ01 before applying stage 10. Exact VQ01 source fields and the GOG constructor defaults satisfy the initial guards; a level-one natural path remains a candidate.
- **Q66-H2:** a remaining EnsureQuestStarted state check or required alias/reference preflight rejects VQ01 or prevents useful startup.

The static SetStage entry and constructor checks discriminate the initial guard. Only the exact runtime state transition plus required-alias/access observation can discriminate the full models for Steam AE.
