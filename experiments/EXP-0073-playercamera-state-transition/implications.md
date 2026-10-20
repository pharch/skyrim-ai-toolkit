# Implications

The PlayerCamera+0x28 path is stateful rather than a single statically fixed callback. The ThirdPersonState target is one constructor-selected candidate; PlayerCamera can route other state objects through the same transition helper. Keep every unresolved descendant open and do not generalize the bounded callback body to all teardown paths or to zero armor XP.
