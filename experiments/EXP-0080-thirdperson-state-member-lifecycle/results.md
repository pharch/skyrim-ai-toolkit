# Results

ThirdPersonState initializes +0xA0 to null. FUN_1408e6500 obtains an object through PlayerCharacter slot+0x378, calls that object's slot+0x150, and stores the return through FUN_1408ea490. Lifecycle functions release the member through its slot+0x8 if the refcount reaches zero. The member's concrete vtable and connection to the eight ProcessTrapHit sites remain unresolved [EV-0342].
