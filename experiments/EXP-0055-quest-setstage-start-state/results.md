# Results

## Starting evidence

EV-0310 records main DA02's level-30 Story Manager node, Start Game Enabled clear, fixed book references disabled below the threshold, and `DA02BookScript.OnRead` calling `DA02.SetStage(1)` while DA02 is below stage 1. EV-0301 maps the DA04 Ruminations book callback to `SetStage(1)` and reports a public Papyrus Index description that SetStage waits for quest startup if needed. That description is a secondary lead; neither source investigation resolved native stopped-quest behavior or a Steam level-one transition.

## Registered binding and prior wrapper correction

EV-0313 records the GOG `SetStage` literal at RVA `0x17D43A8`, its unique data reference, the callback candidate `FUN_14034de90`, and a peer `GetStage` row whose callback `FUN_14034dc70` routes to a `GetStage >>` diagnostic and stage-value helper. Their method-name and candidate-callback slots have the same `0x30` spacing; the data row has no indexed code xrefs, so the mapping is strongly supported by layout and peer semantics.

The same GOG project query directly registers `FUN_140a48aa0` as `Quest.SetCurrentStageID` and `FUN_140a48c50` as `Quest.Start`. This corrects the earlier EV-0272 inference that `FUN_140a48aa0` was `Quest.SetStage`; its event-ID/flag guard belongs to SetCurrentStageID.

## Native transition

The registered SetStage callback requires `(quest+0xDC bit 0 set) OR (quest+0xE0 == -1)`, then calls GOG `TESQuest::EnsureQuestStarted` with start-now mode. When the internal guard accepts a stopped-quest state, it can call `FUN_1403ccd90` and `BGSStoryTeller::BeginStartUpQuest`. That path resets current stage and stage flags, processes quest reference entries through a `QueuedPromoteQuestTask`, marks a readiness bit, and queues the quest in a manager array. The callback then looks up the requested stage; the stage writer can raise current stage, call the stage fragment, and dispatch a stage event. No explicit player `GetLevel` comparison appears in the inspected binding/guard path.

This supports conditional startup-before-stage behavior for the GOG callback and falsifies a universal running-quest-only model. Event-ID/ready-bit failures can still block entry. The trace does not establish exact `TESQuest` running state, complete alias fill, journal/dialogue availability, or useful access.

## Limits

DA02's QUST is level-gated at 30, Start Game Enabled is clear, and serialized `ENAM=LEVL`; its fixed book references are disabled below 30 and its ordinary leveled-list minimum is 24 [EV-0310]. EV-0289 carries a CommonLib lead relating serialized event type to runtime quest `+0xE0`, but exact GOG/Steam loading and DA02 runtime flag values remain unverified. The natural book callback, exact Steam order, clean level-one save, observer, alias state, journal/dialogue access, and progression remain open. No level-one bypass or vanilla reproduction is claimed.
