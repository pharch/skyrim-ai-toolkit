# LEVL quest event type versus the registered SetStage guard

This investigation asks whether level-gated main quests serialized with `ENAM=LEVL` can pass the GOG `Quest.SetStage` event-ID/ready-bit guard while stopped and outside their Story Manager event. EV-0310 identifies DA02 as a concrete level-30 LEVL case; EV-0306 and EV-0308 identify DA09 and DA06 LEVL cases. EV-0313 supplies the registered GOG callback and its `quest+0xE0` guard.

EV-0314 resolves the serialized `ENAM` to GOG runtime `+0xE0` mapping through the TESQuest constructor/vtable and QUST parser path. For DA02, DA09, and DA06 source records, `ENAM=LEVL` is nondefault relative to the constructor's `-1`. The registered SetStage predicate rejects that field when ready bit 0 is clear, while a set bit can independently pass the initial OR guard. The installed Steam state, callback reachability, later startup, alias fill, and functional access remain unobserved.

This investigation continues the unresolved field mapping from Q-0053. Competing models and discriminants are in `hypothesis.md` and `predicted-outcomes.md`; query scope and the exact Steam observer need are in `protocol.md`.
