# Predicted observations

| Observation | H1: helper-only gate | H2: ordinary entry still gated |
|---|---|---|
| DA04 Story Manager child | Selects DA04SeptimusSendForPlayerQuest, a distinct helper | Same helper child, but another dependency also gates main DA04 |
| Main DA04 start fields and linked writers | Ordinary book/dialogue/Elder Knowledge record or script route can start DA04 independently, with no serialized >=15 condition found on that route | All identified ordinary entry routes depend on the gated helper or carry a separate level-dependent condition |
| DA04 early stage/progression fields | Early objectives can be recorded before the level-15 continuation pause; the later gate is separate | Start or early objective transition is serialized as level-gated, or no ordinary writer is found in the bounded screen |
| UESP revision 3564369 | May describe book/concurrent-quest startup and a later level-15 pause; this is a search lead | Same text is insufficient to prove the engine start path; source records may place a separate gate |

No static outcome proves a vanilla level-one run. Runtime acceptance still requires a clean level-one save, numeric level preservation, quest-running/stage observation, an ordinary no-trigger control, and repetition.

## Observed outcome

The DA04 QUST VMAD maps `Alias_RuminationsBook` to alias ID 19 and binds `DA04RuminationsScript` to that same alias. ALST alias 19 has `ALFR` reference `00032787`; that REFR's `NAME` points to BOOK `00032785`. The alias script's `OnRead` calls `GetOwningQuest().SetStage(1)`. The QUST VMAD maps stage 1 to `QF_DA04_0002D512.Fragment_18`, whose PEX sets `ReadCrazyBook` and calls `SetStage(5)`. Main DA04's DNAM flags are `0x0111`, including `Start Game Enabled`; the explicit >=15 node's child is the separate letter-delivery helper. This supports H1 and falsifies H2 for this early book route at the serialized-source level. Later progression and a clean level-one game run remain untested.
