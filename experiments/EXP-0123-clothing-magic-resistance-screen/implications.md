# Implications

- **Supported candidate:** a Clothing ARMO can supply Resist Magic AV44, while the GOG Actor `CheckResistance` path reads target resistance ActorValues and the incoming effect's configured ResistValue. This is a separate protection mechanism from the physical cached armor-factor field and from the Heavy/Light armor hit-XP selector [EV-0222], [EV-0261], [EV-0398–EV-0402].
- **Not established:** level-one item access, Steam 1.6.1170.0 behavior, measured damage reduction, qualifying hits, numeric Heavy/Light AVSK, delayed or redirected skill progress, or a vanilla exploit. The necklace is jewelry with zero physical DNAM rating; do not generalize this to physical armor.
- **Cross-domain graph:** no shared quest state, quest-start call, HitData route, or serialization field links this resistance path to OBJ-1. Keep the Q71/Q72 runtime discriminators separate; no causal edge is justified.
- **Next useful work:** continue OBJ-1 static source investigation while the exact clean Steam save/order/Observer test is unavailable. Keep an equipped-versus-unequipped resistance comparison and raw AVSK measurement queued under EV-0260.
