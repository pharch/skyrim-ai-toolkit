# Results

FUN_1406b9df0 calls FUN_1407c9980, whose flag-1 traversal reaches FUN_140e95df0. That writer can append bhkFixedConstraint or bhkMalleableConstraint children to a recognized rigid body. The mapped attach, cleanup, and destruction callbacks manipulate physics state and references; no AV11/AV12 sink appears in this bounded chain [EV-0355].
