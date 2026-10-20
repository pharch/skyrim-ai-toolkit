# Implications

The PlayerCamera+0x128 owner member is no longer untyped: its producer installs bhkRigidBody. That destructor's body+0x28 child array is still dynamic.
