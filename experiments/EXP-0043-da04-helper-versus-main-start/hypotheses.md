# Competing models

- **H1 — helper-only level gate:** DA04 SMQN DA04SeptimusFindPlayerNode checks GetLevel >= 15 to select only DA04SeptimusSendForPlayerQuest. A separate ordinary book, dialogue, or Elder Knowledge route can start main QUST DA04 below level 15 and reach early stages; a later pause/courier condition is separate from startup.
- **H2 — ordinary start/progression remains gated:** despite the helper child, book/Elder Knowledge/dialogue routes either depend on that helper or meet a separate level predicate before starting main DA04 or advancing its early objectives.

The discriminant is the serialized relationship between the node/helper, main and concurrent QUSTs, book/dialogue references, stage fragments, conditions, and any captured script properties. UESP revision 3564369 can guide the record search but cannot determine what runs in game. Neither model is a live result until a clean level-one transition is observed.

## Static-source outcome

- **H1 supported within the inspected Skyrim.esm path:** the node's child is the courier helper; main DA04 has `Start Game Enabled`; the `RuminationsBook` alias is bound to a fixed REFR and carries `DA04RuminationsScript`; reading it sets DA04 stage 1, whose mapped fragment sets stage 5. No GetLevel predicate appears on the captured main QUST or this book-to-stage route.
- **H2 falsified for initial start and the stage-1/5 book route:** at least one serialized ordinary route is independent of the level-15 helper. This does not decide later progression gates or all dialogue/Creation Club/plugin paths.
- **Live low-level access remains a separate model:** the source candidate predicts an ordinary level-one start if the fixed book is reachable and the captured records win. A clean level-one runtime comparison is still required.
