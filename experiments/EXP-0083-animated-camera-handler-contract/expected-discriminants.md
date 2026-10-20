# Expected discriminants

1. Resolve the object returned by the PlayerCharacter flag-zero context getter.
2. Map its exact slot +0x150 implementation and returned object vtable.
3. Identify the returned object's slot +0x8 finalizer.
4. Compare concrete targets against the five omitted cleanup sites and the full eight-site ProcessTrapHit chain.
