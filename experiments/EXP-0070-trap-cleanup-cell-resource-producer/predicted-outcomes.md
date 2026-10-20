# Predicted outcomes

- **Supports producer model A:** identify a concrete object behind cell-context+0x130 on the observed type-0x11 branch, then resolve slot+0x8 and find an AV11/AV12 skill sink.
- **Supports producer model B:** identify the type-2 or type-1 metadata return object's concrete vtable and resolve its finalizer without an AV11/AV12 sink.
- **Supports Q64-H1:** resolve every relevant cleanup descendant and show none reaches skill progress with AV11/AV12.
- **Supports Q64-H2:** a resolved cleanup descendant reaches Actor::UseSkill or the mapped skill-progress sink with an AV11/AV12 argument.
- **Inconclusive:** receiver class, selected metadata branch, returned object's vtable, or finalizer descendants remain dynamic.
