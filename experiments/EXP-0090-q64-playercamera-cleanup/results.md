# Results

FUN_1408e3f50 stores PlayerCamera in DAT_1430febf8 and installs the table at RVA 0x18F0628. Slot 0 is FUN_1408e8b50, which calls FUN_1408e4070 before optional 0x168-byte deallocation [EV-0352]. The destructor has five unresolved indirect sites; its 13-entry array callback is generic refcount release. The TESCamera +0x28 base member and array entries start null. No object-specific non-null producer was recovered.
