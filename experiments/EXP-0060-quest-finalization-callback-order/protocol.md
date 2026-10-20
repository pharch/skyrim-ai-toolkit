# Protocol

1. Read EV-0313's callback-registration result and EV-0318's QUST parser/finalization chain before collecting evidence. State H1, H2, and their discriminants first.
2. Query only the existing GOG project through the strict dispatcher in read-only, auto-analysis-disabled mode. Preserve the requested RVA, hash, metadata, direct calls, indirect sites, and caller decompilation.
3. Inspect `FUN_1401be290`, its caller, and the main `FUN_1401b9510` path. Classify only direct calls and data references with sufficient provenance.
4. Stop if no concrete event/callback route links the load paths to registered `Quest.SetStage`; record the missing dispatch/runtime discriminator instead of inferring order from absence.
5. Keep raw output below ignored `.local/`; cite EV-0313/0318 as prior context and register fresh query hashes in EV-0320.
6. Do not use forced stages, altered plugins, injected scripts, or environment-specific RVAs as evidence for natural Steam behavior.
