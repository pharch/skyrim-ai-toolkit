# Competing models

- H1: PlayerCharacter slot+0x378 flag 0 returns a NiAVObject/NiNode-compatible root; slot+0x150 selects a child stored at ThirdPersonState+0xA0.
- H2: the returned object is another interface implementation sharing slot+0x150; NiNode is only a structural comparator.
- Q64-H1: no resolved descendant reaches AV11/AV12 skill progress.
- Q64-H2: a resolved descendant reaches that sink.

The code path supports a named-object/child-resource candidate, but no dynamic vtable or child finalizer is selected.
