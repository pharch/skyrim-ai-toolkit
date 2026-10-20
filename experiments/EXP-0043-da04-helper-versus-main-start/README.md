# EXP-0043 — DA04 helper gate versus main-quest entry

## Objective

Determine whether the DA04 level-15 Story Manager node gates only the Septimus send-player helper or also blocks ordinary starts/progression of main quest DA04 below level 15.

## Scope

This investigation compares Skyrim.esm source records for the DA04 Story Manager node, main/helper QUSTs, the Elder Knowledge quest, the Ruminations book, and linked dialogue/stage records. Direct-parser captures are source-file observations, not native xEdit winners or live behavior. The local UESP DA04 page at revision 3564369 is a secondary route lead.

## Procedure and hypotheses

See hypotheses.md, predicted-outcomes.md, and protocol.md. Raw outputs and hashes belong under ignored .local/alignment/transactions/TX-20261016-0036/.

## Status

Static source pass complete under EV-0301. Skyrim.esm serializes main QUST DA04 with the `Start Game Enabled` bit, maps its `RuminationsBook` alias to REFR `00032787` (base BOOK `00032785`), and attaches `DA04RuminationsScript` to that alias. Its `OnRead` calls owning-quest `SetStage(1)`; DA04 stage 1 maps to `Fragment_18`, which sets stage 5. The >=15 Story Manager node instead selects the distinct Septimus courier helper. This supports a low-level ordinary entry candidate and falsifies an all-entry level-15 gate in the inspected source path. It is not a level-one runtime result: profile overrides, actual quest/alias state, and physical access/read behavior remain unverified.
