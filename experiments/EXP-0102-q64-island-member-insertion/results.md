# Results

The exact ProcessTrapHit attach function reads endpoint +0x130 into hkpConstraintInstance +0x10. Separately it inserts a 0x40-byte record into endpoint +0x100/+0x108 and updates constraint +0x60 back-pointers [EV-0360, capture 20261018T084404Z].

The hkpSimulationIsland initializer sets up +0x60/+0x68; FUN_140b44470 appends endpoint pointers and writes endpoint +0x130 back-pointers; FUN_140b43f90 merges member arrays, rewrites moved endpoint +0x130 and updates member constraints +0x10 to the receiving island [EV-0362, EV-0364]. Exact live endpoint membership remains unobserved; the static owner model is strongly supported. Capped writer scans provide no negative [EV-0363]. No AV11/AV12 or live Steam hit/protection/raw-AVSK conclusion follows.
