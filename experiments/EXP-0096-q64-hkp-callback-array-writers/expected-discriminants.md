# Expected discriminants

1. Find a producer-backed write to the exact constraint's +0x40 callback pointer/+0x48 count or a concrete registration call.
2. Resolve the callback entry class and slot +0x10 target from its exact producer.
3. Resolve member classes at constraint +0x18/+0x28/+0x30 from their constructors or exact writers.
4. Follow concrete targets to Actor::UseSkill and inspect the AV11/AV12 argument. A global offset match without receiver identity is inconclusive.
