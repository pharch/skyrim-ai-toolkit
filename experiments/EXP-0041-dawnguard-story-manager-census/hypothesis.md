# EXP-0041 hypothesis

## H1 — Durak helper is the only level-conditioned Story Manager node in Dawnguard.esm

The level-10 predicate on `DLC1VQ00Node` selects the Durak messenger helper. Other Story Manager nodes in the Dawnguard.esm file are event-, quest-stage-, time-, or global-conditioned without another `GetLevel` selector.

## H2 — Additional level-conditioned Dawnguard quest or encounter nodes exist

At least one other SMEN/SMQN record in Dawnguard.esm has a `GetLevel` threshold and selects a quest or encounter path distinct from the Durak helper.

## Discriminant

Enumerate every SMEN/SMQN record physically present in Dawnguard.esm, decode every CTDA function index 80, and resolve every global operand and child reference. H1 predicts one matching CTDA; H2 predicts at least two.
