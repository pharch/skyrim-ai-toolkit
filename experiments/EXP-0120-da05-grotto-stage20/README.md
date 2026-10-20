# DA05 Grotto helper dialogue and stage-20 callback

This line tests whether the Grotto helper quest can expose INFO `00095585` before the main DA05 route reaches the Grotto. It distinguishes the helper quest (`QUST 000955CF`) from main DA05 (`QUST 0002A49A`) and keeps the INFO's owning-quest stage call separate from its `DA05` property reference.

The experiment combines the native five-master `DIAL`/`INFO`/`QUST` exports, exact source-record parsing, the recovered TIF/QF PEX fragments, an exact FormID-reference census, and the GOG `Quest.SetStage` mechanism map. The TIF sets the owning helper quest to stage 20; the helper's stage-20 fragment kills alias 57 and requests main DA05 stage 60. This is static source research only. It cannot establish a profile winner, runtime alias fill, dialogue availability, or a vanilla level-one interaction.

Raw captures remain under ignored `.local/alignment/transactions/TX-20261018-0005/`; evidence IDs and the capture manifest are in `research/EVIDENCE.json` and that private directory.
