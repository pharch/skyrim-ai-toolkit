# Expected discriminants

1. Confirm the exact vtable slot-0 target for the factory-created hkpConstraintInstance.
2. Map callback-array and member-reference writers for offsets +0x40/+0x48 and +0x18/+0x28/+0x30.
3. Follow producer-backed callback slot +0x18 or member slot 0 targets to Actor::UseSkill and inspect the ActorValue argument.
4. Treat an unresolved callback, member class, or finalizer as inconclusive.
