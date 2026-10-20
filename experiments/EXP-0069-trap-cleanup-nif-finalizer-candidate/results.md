# Results — conditional NiNode path

EV-0331 maps the NiNode parser registration and constructor vtable, then maps vtable slot +0x8 through FUN_140d28f40 to primary destructor FUN_140d20350. That destructor final-releases each child object through its virtual slot +0x8 and delegates to FUN_140d1d8f0. The NiAVObject cleanup includes an unresolved slot +0x128 call on an object at offset +0x40.

No direct Actor skill-progress call appears in the inspected bodies. However, the first-person skeleton resource's exact NIF root, subtree, child finalizers, and slot +0x128 target are unknown. This is a conditional class candidate only; it does not resolve Q64-H1/H2 [EV-0331], [EV-0328], [EV-0327], [EV-0324].
