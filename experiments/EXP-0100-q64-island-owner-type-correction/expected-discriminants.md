# Expected discriminants

1. Resolve the exact owner pointer selected during hkpConstraintInstance attachment.
2. Tie that pointer to an entry in hkpSimulationIsland EntityPtrs (+0x60/+0x68).
3. Tie the exact constraint pointer to that entity's +0x100/+0x108 record.
4. Follow producer-backed callback/member targets to AV11/AV12; table shape alone is inconclusive.
