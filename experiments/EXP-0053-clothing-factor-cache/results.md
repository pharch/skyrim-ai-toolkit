# Results

## GOG target and query coverage

The existing read-only GOG project matched `SkyrimSE.exe` ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Auto-analysis was disabled and no program import, project creation, or overwrite was attempted. The fresh Address Library probe matched the same executable and resolved `VTABLE::TESObjectARMO` at GOG RVA `0x179E0C0`; it anchors the class and build but does not name the field.

The complete `+0x274` scan covered 5,654,579 analyzed instructions. Its bounded decompilation traced `FUN_140728b70` (RVA `0x728B70`), which traverses the inventory collection using `FUN_1402318d0`, dispatches visitor slot `+8` to `FUN_14072a500` (RVA `0x72A500`), and stores the visitor accumulator at `this+0x274`. The visitor accepts ARMO form type byte `0x1A`, checks `ARMO+0x1BC != 2`, then computes and adds rating. The existing EV-0261 evidence connects PlayerCharacter vtable slot `0xE7`'s cached `+0x274` value to the GOG hit damage builder.

The complete `+0x1BC` scan also covered 5,654,579 instructions and reported 161 displacement accesses across 104 functions, including 38 stack-relative matches. It decompiled the relevant parser `FUN_140278170` (RVA `0x278170`). In its BOD2 case (little-endian signature `0x32444F42`), it reads the subrecord into `param_1+0x1B8` and byte-swaps the two adjacent 32-bit words when required. Thus serialized BOD2 byte offset 4 maps to runtime object offset `+0x1BC`.

EV-0309 preserves the pinned TES5Edit dev-4.1.6 schema: BOD2's Armor Type follows its first flags word at byte offset 4; values are Light `0`, Heavy `1`, Clothing `2`. Therefore the visitor's `+0x1BC != 2` guard excludes Clothing before adding the item rating to this cache. This supports H2 and falsifies H1 for the GOG cached-factor path. Positive-DNAM Clothing records remain valid record data, but they do not contribute through this writer.

## Limits and continuation

The displacement scan reports all matches but writer decompilation is bounded by the adapter's candidate-output limits; this result relies on the directly captured parser, cache writer, and visitor paths. The parser/visitor mapping is attested only for GOG 1.6.1179.0. It does not establish the same layout or behavior in Steam 1.6.1170.0, does not measure incoming damage, and does not demonstrate an armor AVSK delta. No exact Steam profile order or live observer is configured.

Next OBJ-2 investigation: determine whether a normal Light/Heavy armor item can retain its GOG cached protection through the physical-trap damage path while that path bypasses the normal AV11/AV12 receiver award. Require a matched Steam level-one hit/protection/AVSK test before claiming the bounty. No causal edge to OBJ-1 is supported.
