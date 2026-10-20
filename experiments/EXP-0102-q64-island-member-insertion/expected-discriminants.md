# Expected discriminants

1. Attach reads endpoint +0x130 into constraint +0x10.
2. EntityPtrs serializer traverses island +0x60/+0x68 and each endpoint's +0x100/+0x108 records.
3. Insertion writes endpoint +0x130 to island and appends endpoint to EntityPtrs.
4. Merge moves endpoints and repairs endpoint +0x130 plus constraint +0x10.
5. Matching offsets alone leave live ProcessTrapHit membership unobserved.
