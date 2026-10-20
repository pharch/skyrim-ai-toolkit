# Expected discriminants

1. Identify the destination object for every matching +0x40/+0x48 store.
2. Map constructor argument four to instance +0x18.
3. Confirm the ProcessTrapHit factory reaches the exact constructor caller.
4. Resolve wrapper slots +0x128/+0x188 before inferring callback lifetime.
