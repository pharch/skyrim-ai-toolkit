# Competing models

## H1 — load finalization precedes the first natural SetStage callback

The load-manager path completes the QUST slot-19 sweep and returns before the engine naturally delivers a callback that invokes registered `Quest.SetStage` for a loaded quest.

**Predicted discriminant:** a build-attested caller chain places `FUN_1401bdf20` and its return before the first natural startup/event callback can reach the registered SetStage handler, with no earlier callback dispatch from per-file processing.

## H2 — a natural callback can arrive before finalization completes

A natural event/callback chain can synchronously invoke `Quest.SetStage` during record processing or before the post-file-load slot-19 sweep.

**Predicted discriminant:** a concrete pre-finalization call or class-resolved dispatch chain reaches the registered SetStage handler for a loaded quest. An untyped callback table, generic virtual site, or absent direct xref is inconclusive.

## Result boundary

The static captures identify the finalization order within two loader paths, but no class-identified callback chain joins either path to `Quest.SetStage`. Keep H1 and H2 proposed until a stronger dispatch trace or exact-runtime observer supplies the discriminant.
