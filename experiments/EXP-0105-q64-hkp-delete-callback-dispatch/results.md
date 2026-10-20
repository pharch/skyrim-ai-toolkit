# Results

The hkpConstraintInstance destructor calls FUN_140b674a0, which iterates non-null entries from +0x40/+0x48 and invokes each entry vtable slot +0x18 with the instance before compacting nulls. The finalizer then frees the callback array. Entry class, writer and slot target remain unresolved [EV-0367].
