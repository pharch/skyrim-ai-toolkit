# Competing models

## H1 — LEVL loads a nondefault event ID and blocks stopped SetStage

The GOG QUST loader writes serialized `ENAM=LEVL` to the nondefault runtime field at `quest+0xE0`. When ready bit 0 is clear, the registered SetStage callback rejects that initial state before startup. A natural stage callback cannot pass this guard through SetStage alone.

**Predicted discriminant:** a build-attested QUST loader/field mapping links serialized `ENAM=LEVL` to the runtime event-ID field, and the callback's entry condition rejects that state when ready bit 0 is clear.

## H2 — LEVL quests can enter the accepted startup path

When ready bit 0 is set, it independently satisfies the initial SetStage entry predicate even though `ENAM=LEVL` loads to a nondefault event ID. Passing this guard alone does not show that later initialization accepts the quest or that a natural callback is available.

**Predicted discriminant:** the source-to-runtime field trace or an exact read-only Steam observer shows the guard accepts a stopped LEVL quest and startup precedes stage application while numeric level remains unchanged.

## H3 — Cross-build field mapping is insufficient

The GOG field map and source records do not establish how the installed Steam runtime loads `ENAM`, `+0xE0`, or readiness bits; only a matched Steam observer or Steam-native trace can decide the event-scope interaction.

**Predicted discriminant:** native loader semantics or runtime values differ by build, or the available static evidence cannot connect serialized event type to the tested quest fields.
