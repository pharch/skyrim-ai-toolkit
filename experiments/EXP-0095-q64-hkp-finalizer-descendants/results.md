# Results

The factory-created hkpConstraintInstance slot 0 resolves to FUN_140b36b20, which calls its member cleanup helper and TLS allocator. That helper can dispatch callbacks from the +0x40 array through slot +0x18 and releases three member references through the generic refcount helper. No direct Actor::UseSkill call appears, but callback/member types remain unresolved [EV-0357].
