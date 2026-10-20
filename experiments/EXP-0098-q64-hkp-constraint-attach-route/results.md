# Results

The ProcessTrapHit-created hkpConstraintInstance reaches FUN_140e860d0 through wrapper +0x148. Immediate attachment calls FUN_140b3a710/FUN_140b43a20/FUN_140b678a0. The attach function copies selected endpoint +0x130 island pointer to constraint +0x10, inserts a 0x40-byte record into endpoint +0x100/+0x108, and maintains constraint +0x60 as the record back-pointer. Add-callback notification follows [EV-0360, EV-0364].

Island initialization, serialization, insertion and merge use a consistent hkpSimulationIsland/EntityPtrs/+0x130 layout. This corrects the prior owner-field description; live membership and callback population remain unobserved. Broad writer scans remain output-capped [EV-0363, EV-0364].
