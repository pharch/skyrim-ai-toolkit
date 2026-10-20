# Results

FUN_1407373e0 passes DAT_1430febf8 to FUN_1408e7230, which stores a constructed bhkRigidBody at PlayerCamera+0x128. The installed table slot +8 is FUN_140d28f40, which dispatches the slot-0 destructor FUN_1402f2d10 -> FUN_140e92c60. The destructor releases a body+0x28 child array through unresolved slot+8 targets [EV-0353].
