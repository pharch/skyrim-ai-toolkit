# Results

FUN_140cee0a0 copies a pointer and increments a header counter at offset -0x10. FUN_1408e6500 passes that copied value to slot+0x150 on the PlayerCharacter slot+0x378 result. The direct callback wrapper has no code callers from which to recover its string value. NiNode recursively searches children with the same opaque argument, making it compatible but not identified [EV-0343], [EV-0336].
