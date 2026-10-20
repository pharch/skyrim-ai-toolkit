# Competing models

- Q64-H1: relevant teardown descendants do not award AV11/AV12 skill progress.
- Q64-H2: a relevant descendant reaches that sink with AV11/AV12.
- Scene model A: PlayerCharacter +0x730 is an NiAVObject-compatible child attached to the cell scene, with +0x30 as parent and NiNode add/remove methods.
- Scene model B: the same offsets are implemented by a different dynamic parent interface or subclass target.

EV-0334 supports the structural child/parent relationship, but the runtime parent table and child finalizer remain unknown. None of the Q64 hypotheses is decided.
