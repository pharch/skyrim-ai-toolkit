# Expected discriminants

1. Determine which branch of PlayerCharacter slot+0x378 supplies the receiver.
2. Establish the receiver's concrete vtable and slot+0x150 implementation.
3. Resolve the returned object's concrete vtable and slot+0x8 finalizer.
4. Link the exact receiver/finalizer path to a specific one of the eight ProcessTrapHit teardown sites.
