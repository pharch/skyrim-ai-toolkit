# Implications

PlayerCamera state callbacks are class-specific; the FirstPerson, ThirdPerson, AutoVanity, and Bleedout bodies cannot be collapsed into one cleanup mechanism. A no-direct-sink result for a callback does not exclude its finalizer or an unexamined state.
