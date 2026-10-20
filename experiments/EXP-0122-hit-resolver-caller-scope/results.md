# Results

## Direct observations

- Read-only Ghidra query of GOG AE 1.6.1179.0 `FUN_1406bb690` found 32 outgoing direct-call edges and 7 indirect call sites. It calls `FUN_1406bcaa0` at two direct sites, `0x1406bba9a` and `0x1406bbaea`.
- `FUN_140659160` dispatches on the first 32-bit field of its input. Case `0xB` takes an Actor pointer from the event object and two byte fields, then calls `FUN_1406bb690(actor, byte_4, byte_6)`.
- `FUN_14065b800` invokes a callback vtable slot at `+0x8` when its global callback path is enabled. If that callback does not consume the event, it calls `FUN_140659160`. One captured caller constructs a different event tag (`0x38`); it does not identify the producer of case `0xB`.
- The incoming-caller query for `FUN_14065b800` reports 95 direct call sites and a stored caller count of 64; the output also contains 1 separately selected caller body and 32 incoming-caller bodies. EV-0423 re-parses and repeats the query: both captures contain the same 95 unique caller functions, with 33 decompiled bodies and 62 remaining. The 64 count is the query's `Function[64]` storage cap, not the complete direct-caller count. None of the 33 inspected bodies constructs a tag-0xB event object. This does not rule out a producer among the remaining callers [EV-0423].
- `FUN_1407ba3e0` has zero analyzed incoming direct-call edges. It invokes Actor virtual slot `0x99` with argument zero and continues only when the predicate returns false and a current-process target pointer matches the supplied actor pointer; it then calls `FUN_1406bb690` with the comparison result and byte value 1. A nearby data reference places this function in a pointer table, but the table owner and runtime event remain unidentified.
- The 16-qword table query at GOG RVA `0x18BAE08` places `FUN_1407ba3e0` at entry 1 and shows repeated three-entry groups containing function pointers and non-function data pointers. The queried data target at entry 2 (`0x141B39578`) has one DATA xref from the table, no function boundary, and no decoded type/owner in the bounded address context. This does not establish the callback-table owner.

## Assessment

H2 is supported only for the observed source scope: the recovered routes are a tagged callback case and a state/process-gated Actor callback. Neither route identifies the ordinary physical-hit producer, and the event tag's semantic owner is unresolved. H1 remains possible but unproven. This does not falsify indirect or additional ordinary-hit routes elsewhere in the program.

The result does not change the earlier mechanism candidate: EV-0261 places AV39/armor-factor mitigation before blocked-hit bookkeeping, while EV-0222 maps the receiver's blocked branch to AV9 and omits AV11/AV12. The missing edge is practical incoming-hit coverage and the matched Steam measurement of positive protection, a qualifying block, AV9/11/12 UseSkill calls, and raw AVSK deltas. EV-0260 records the missing profile/save/Observer prerequisites.

## Source identity and capture hashes

All queries used the configured existing GOG project with `-noanalysis -readOnly`, no import and no reanalysis. The GOG analysis executable ProductVersion is 1.6.1179.0 and SHA-256 is `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. This identity is separate from installed Steam AE 1.6.1170.0 (EV-0109).

- `gog-query-20261018T154552Z`: RVA `0x6BB690`, stdout SHA-256 `4338c42cfa52d4dd1c1ee4d9f9b33275d900a5ae22e48838383d885a570a6e9a`.
- `gog-query-20261018T154753Z`: RVA `0x659160`, stdout SHA-256 `1b725b13a3b66a7c31e4a3cf432e2ac3a0774923304ec308f7054acd71712878`.
- `gog-query-20261018T154922Z`: RVA `0x65B800`, stdout SHA-256 `2aae3a35ed55c5f3564b85dc6b5745c9eeb2b146a7f3de25836dffbd2fcf4890`.
- `gog-query-20261018T155135Z`: RVA `0x7BA3E0`, stdout SHA-256 `4920da0e33983d45ea40a101ddb32b8143a3331ab0038375afc011e348fb7880`.
- `gog-query-20261018T155745Z`: RVA `0x65B800`, up to 32 incoming callers; metadata reports 95 direct call sites, a 64-entry stored caller count, and 32 incoming caller decompilations in addition to the separately selected first caller; stdout SHA-256 `91678d35f4e216b1a4b6fccf71ac5dde7a857e988b3030b6ff6225f8eb3bbfc7`.
- `gog-query-20261018T202505Z`: fresh identity-checked repeat for EV-0423 with the current query-script hash; same 95 unique callers, 64 stored cap, and 33 total decompiled bodies; stdout SHA-256 `973db3d19f66b78f01b995e732fd8cb01fb41837784c3ec4fc6dd3ac123e77b8`.
- `gog-query-20261018T160134Z`: 16-qword table at RVA `0x18BAE08`; stdout SHA-256 `d67fc51056de135e1d3b31ff1454e84b3cf1aef46d578b7c7cd08c8b53fb5f9b`.
- `gog-query-20261018T160338Z`: address context at data RVA `0x1B39578`; stdout SHA-256 `cab8c32289e9968e479869ce084791a33dbdede23c72f97f00764cf964a9c1a1`.
