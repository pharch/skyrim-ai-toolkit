# Expected discriminants

1. Identify writers and concrete type for the ThirdPersonState member at +0xA0.
2. Resolve its slot+0x8 target and bounded descendants.
3. Determine whether the member/callback is reachable from a ProcessTrapHit teardown site.
4. Preserve unknowns until the path and any ActorValue argument are concrete.
