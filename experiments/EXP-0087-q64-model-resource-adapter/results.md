# Results

FUN_140216b40 loads a generic mesh resource and adapts it through FUN_140d19980, which returns slot +0xB8 and calls slot +0xE8. Named members are found by FUN_140d27eb0 in a count/pointer sorted array. The output can feed the candidate PlayerCharacter +0x9A0/+0x9A8 setter, but its exact vtable remains data-selected [EV-0349], [EV-0333].
