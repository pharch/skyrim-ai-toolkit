# Results — bounded +0x9D0 producer trace

EV-0332 follows the candidate writer FUN_140766540 through FUN_1401a19c0 and FUN_1402b8cf0. The helper receives a nested object from a TES global at +0xC0 or +0x78. Its layout and ray-query use are consistent with TESObjectCELL, whose constructor clears +0x130. The helper has a type-0x11 branch that reads a nested pointer at +0x130; otherwise it returns a type-2 or type-1 resource metadata pointer.

Neither branch exposes the returned object's concrete vtable or final +0x8 implementation. FUN_1402e8580 in the setter computes a different ancestry-derived local and does not supply the value stored at +0x9D0. Q64-H1/H2 remain open [EV-0332], [EV-0328], [EV-0325], [EV-0329].
