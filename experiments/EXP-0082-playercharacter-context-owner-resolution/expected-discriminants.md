# Expected discriminants

1. Identify the TLS +0x5F0 object and its owner comparison at +0x5F8, or the nested PC +0x68/+0x68 member.
2. Match the object present at FUN_1408E6500's slot +0x150 call to an exact vtable.
3. Identify the returned member's concrete class and slot +0x8 finalizer.
4. Compare that finalizer with the eight ProcessTrapHit teardown sites and screen resolved descendants for AV11/AV12.
