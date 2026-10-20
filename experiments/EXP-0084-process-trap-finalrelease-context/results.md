# Results

The five formerly omitted sites in FUN_14072fd60 are refcount-final calls on fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730. Each calls dynamic slot +0x8 only when the old refcount is one. Combined with EV-0325/0327, all eight callsites now have field/interface context, while their concrete targets and descendants remain unresolved [EV-0346].
