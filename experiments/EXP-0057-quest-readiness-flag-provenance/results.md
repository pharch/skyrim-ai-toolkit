# Results

EV-0316 resolves the GOG load-time source of `TESQuest+0xDC.0`. The QUST virtual parser `FUN_1403c7a50` reads the first U16 of `DNAM` into `+0xDC`; the versioned TES5Edit schema identifies that U16 as QUST General.Flags and names bit 0 `Start Game Enabled`. Exact official-source records set the bit for DA04 (`DNAM` starts `11 01`) and clear it for DA02, DA06, and DA09 (`DNAM` starts `00 01`) [EV-0316], with source/master context in [EV-0301], [EV-0306], [EV-0308], and [EV-0310].

The GOG constructor and scoped helper OR `0x0100` into `+0xDC` but do not set bit 0 in the inspected bodies. TESQuest vtable slot 19 maps to `FUN_1403c8420`, which conditionally clears bit 0. Thus serialized flags determine the inspected initial field value, while later code can mutate it. The method's dispatch timing, semantic name, exact target-quest call path, and Steam behavior remain unresolved [EV-0316].

Under the separate GOG SetStage predicate, bit 0 is one side of an OR with `+0xE0 == -1` [EV-0313], and `ENAM=LEVL` maps to `+0xE0` for DA02/DA06/DA09 [EV-0314]. This is a static guard-input map. No stopped quest, alias fill, useful access, Steam runtime, or level-one transition is established.
