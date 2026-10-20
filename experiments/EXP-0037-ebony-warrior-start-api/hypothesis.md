# EXP-0037 hypotheses

## H1 — Story Manager event scope guards ordinary start wrappers

The native paths inferred to implement Papyrus `Quest.Start` and `Quest.SetStage` reject a nondefault quest event ID outside the Story Manager context before calling the ordinary startup scheduler.

**Prediction:** the wrappers read the event ID, log the event-scoped rejection, and do not call `EnsureQuestStarted` on that branch. The serialized Ebony Warrior QUST is CLOC.

## H2 — An ordinary start API or direct base record bypasses event selection

An ordinary start/stage wrapper can schedule this event quest outside its event, or an installed vanilla quest/dialogue record directly calls it before the level gate.

**Prediction:** a wrapper call reaches `EnsureQuestStarted` with a nondefault event ID, or a five-master QUST/DIAL/INFO scan finds an external direct reference to QUST `0202C49E`.

## Assessment

H1 is supported for the inspected GOG wrapper branches, and H2 is not supported within the scanned direct-reference classes. The direct `Quest.Start` wrapper identity is inferred from its `Quest started` diagnostic and call shape. Linking the GOG runtime event-ID guard to the installed Steam CLOC record is also an inference; it is not Steam behavior evidence. Other record signatures, dynamically resolved forms, profile plugins, alias fill, and runtime state remain open ([EV-0289]).
