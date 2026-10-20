# Expected discriminants

1. Resolve the object returned by PlayerCharacter slot+0x378 for this call context.
2. Map that object's concrete slot+0x150 implementation.
3. Compare the exact vtable and result class against the NiNode candidate.
4. Keep the returned object's slot+0x8 finalizer and ProcessTrapHit reachability separate until matched.
