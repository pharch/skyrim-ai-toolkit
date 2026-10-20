# Hypothesis — EXP-0028

## Competing models

- **H1 — restored logical effect:** one ActiveEffect is serialized and reconstructed across save/load. Its source/base-effect/target and usUniqueID stay consistent, elapsed time and duration follow the saved state, and no removal or reapplication explains the display.
- **H2 — replacement or another source:** the displayed magnitude persists because a new ActiveEffect is applied, the old entry is replaced, or a permanent ability/enchantment supplies the same displayed value. The active-list identity or event history changes at a transition.

## Static premise and limit

EV-0279's fresh GOG 1.6.1179.0 query shows that the base SaveGame/LoadGame routines write/read the timer, magnitude, flags, reference fields, and 16-bit usUniqueID. This makes those fields useful discriminants. It does not establish that a live alchemy effect survives, that elapsed time advances during wait/travel, or that Steam 1.6.1170 uses the same implementation.
