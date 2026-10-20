# Expected discriminants — EXP-0028

- **Restored logical ActiveEffect:** after save/load, source/base-effect/target and logical usUniqueID match; elapsed time, duration, magnitude and flags reconstruct coherently; the entry remains active with no intervening remove/apply event.
- **Replacement or alternate source:** the old entry disappears or changes identity, a new application is observed, or the displayed value comes from a passive ability/enchantment rather than a current ActiveEffect.
- **Control:** an untreated save has no candidate entry; a deliberate-reapplication control exposes the observer's signature for a known new application.

EV-0279 supports only base-field serialization in GOG. These outcomes remain untested until the exact runtime and read-only ActiveEffect observations are available.
