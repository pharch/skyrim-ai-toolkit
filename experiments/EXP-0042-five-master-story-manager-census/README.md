# EXP-0042 — Five-master Story Manager level-gate census

## Objective

Find official-master Story Manager `GetLevel` conditions beyond the already mapped DA14, Dawnguard Durak, and Ebony Warrior paths, resolve their serialized operands and child quests, and identify candidates whose ordinary entry paths merit level-one testing.

## Scope

The inputs are direct-parser captures of every `SMEN` and `SMQN` record physically present in Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm. Same-FormID records will be compared in official load order. This does not itself create a native xEdit winning-record export, a profile winner, a script/native dispatch census, or a live result.

## Procedure

See [protocol](protocol.md), [hypotheses](hypothesis.md), and [predicted outcomes](predicted-outcomes.md). The analysis script consumes only the raw-parser result JSON preserved under ignored `.local/alignment/transactions/TX-20261016-0035/`.

## Status

The direct-parser census found 15 distinct function-index-80 (`GetLevel`) CTDAs across the five source files, including 12 nodes beyond the previously mapped DA14, Durak, and Ebony Warrior gates. Threshold globals and child QUST records are mapped in [results](results.md). This is a source-file census and same-FormID comparison, not an xEdit winning-field or live-gate result. One Dawnguard SMEN query initially hit a bridge staging/config error; the serial retry returned the expected record.
