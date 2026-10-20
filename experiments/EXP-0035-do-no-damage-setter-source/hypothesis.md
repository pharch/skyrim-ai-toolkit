# Hypotheses

## H1 — Direct hit-resolution setter

The direct caller for the only observed nonzero `doNoDamage` setter value is ordinary hit/damage construction, and parameter slot 7 carries a hit-specific cancellation bit.

**Prediction:** The setter caller is in the HitData resolver/caller chain or its parameter source is directly sourced from an ordinary incoming/outgoing hit structure.

## H2 — Separate action-data callback

The setter value is read from an action-data parameter in a process-level-gated callback, without a direct connection to HitData construction.

**Prediction:** The caller constructs or processes action-data objects, gates on AI process level, and reads the setter bit from a generic parameter slot; no direct HitData resolver edge appears in the bounded call graph.
