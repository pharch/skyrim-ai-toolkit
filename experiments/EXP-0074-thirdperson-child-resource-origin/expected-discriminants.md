# Expected discriminants

1. Recover the actual receiver class/vtable for PlayerCharacter slot+0x378 flag 0 in FUN_1408e6500.
2. Map that receiver's slot+0x150 and compare with the conditional NiNode method FUN_140d1f3c0.
3. Identify the returned +0xA0 member's exact vtable and slot+0x8 finalizer.
4. Screen resolved descendants against Actor::UseSkill AV11/AV12.
