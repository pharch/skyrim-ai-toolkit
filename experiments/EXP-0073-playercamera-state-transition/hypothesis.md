# Competing models

- State model A: PlayerCamera+0x28 is the active camera-state pointer; slot+0x10 is a state transition-out hook and its target depends on the selected state.
- State model B: +0x28 is a generic object callback with no state-array ownership.
- Q64-H1: no cleanup descendant reaches AV11/AV12 skill progress.
- Q64-H2: at least one cleanup descendant reaches AV11/AV12.

EV-0335 supports State model A for the mapped setter and index-9 ThirdPersonState. It does not identify the state selected at teardown or decide Q64-H1/H2.
