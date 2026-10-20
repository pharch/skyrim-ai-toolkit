# Results — refcounted-field producer and receiver

EV-0329 confirms PlayerCharacter teardown releases +0x9A0 and +0x9A8 through refcount-final vtable slot +0x8. FUN_1407445d0 stores into those offsets and releases replaced values through the same slot. Its two direct callers pass DAT_143188918; the global is zero in the binary image and its runtime class is unresolved.

The FUN_140744180 path from FUN_140738380 dispatches through primary PlayerCharacter slots +0x378 and +0x3F0, mapped to accessors for +0x8F8 and +0x8F0. This supports PlayerCharacter receiver attribution for that path. FUN_140215660 passes a value from FUN_140216b40 to the setter; that producer uses a generic resource routine and dynamic +0xB8/+0xE8 calls on the loaded object. The resulting object's concrete class and final +0x8 callback are still unknown.

Q64-H1/H2 remain proposed. No mapped descendant reaches AV11/AV12 skill progress in this evidence, but unresolved dynamic targets preclude a negative conclusion [EV-0329], [EV-0328], [EV-0327], [EV-0325], [EV-0319], [EV-0324], [EV-0260].
