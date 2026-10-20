# Results

FUN_140b48150 writes four float components through +0x4c as part of 16-byte vectors. Captured callers pass its separately allocated 0xe0-byte object to hkpConstraintInstance construction at +0x18. This candidate does not populate the callback array. See EV-0372.
