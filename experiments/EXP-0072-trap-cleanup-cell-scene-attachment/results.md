# Results

EV-0334 maps a cell-transition attach/detach pattern for PlayerCharacter +0x730. The cell-add path selects a child scene node and calls its +0x1A8 method with the field object; the NiNode candidate implementation stores child+0x30 as parent. The cell-removal path reads child+0x30 and calls slot+0x1C0 with the child. NiNode table entries map these methods to add-child FUN_140d1eb20 and remove-child FUN_140d1ed30; the remove helper delegates to child-array removal FUN_140d1ed80.

This supports an NiAVObject-compatible child/parent structural inference but does not observe the actual parent table or child class. The child final slot+0x8 destructor remains dynamic, so Q64-H1/H2 are unchanged [EV-0334], [EV-0327], [EV-0331].
