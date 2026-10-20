# Competing models

## H1 — Accepted SetStage conditionally initiates startup (supported in GOG)

When Papyrus calls the registered `Quest.SetStage` callback on a stopped quest whose event-ID/ready-bit and internal state guards accept the call, native code can call `TESQuest::EnsureQuestStarted` in start-now mode and reach `BGSStoryTeller::BeginStartUpQuest` before applying the requested stage. The callback has no explicit `GetLevel` comparison in the inspected path.

**Observed discriminant:** the registered SetStage candidate callback reaches EnsureQuestStarted and a conditional startup manager path before stage lookup/write [EV-0313]. This is GOG static behavior, not a Steam bypass result.

## H2 — Event-ID and quest-state guards can reject a stopped request (supported as a conditional limit)

The registered callback requires either quest `+0xDC` bit 0 or event ID `-1`; EnsureQuestStarted then applies additional flag predicates. A stopped event-scoped quest may therefore be rejected outside its event context, even though other accepted stopped-quest states can enter startup.

**Observed discriminant:** the callback and EnsureQuestStarted guards precede stage application [EV-0313]. EV-0314 maps DA02's serialized `ENAM=LEVL` to the GOG `+0xE0` field tested by the initial guard; DA02's exact ready bit and installed Steam behavior remain unresolved.

## H3 — Stage/startup bookkeeping does not establish functional access (unresolved)

The native path writes stage state and performs reference-promotion and manager work, but the trace does not establish the user-visible running flag, complete alias fill, journal/dialogue availability, or physical progression. Stage advancement and functional access remain separate observations.

**Predicted discriminant:** a read-only Steam observer should capture running state, current stage, alias fill, journal/dialogue, and usable progression separately after a naturally available callback.

