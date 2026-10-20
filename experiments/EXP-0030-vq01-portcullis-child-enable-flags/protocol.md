# Protocol

## Build and evidence scope

- Installed Steam Skyrim AE identity: ProductVersion 1.6.1170.0 (EV-0109).
- Source scope: installed Dawnguard.esm only for the child/parent references; no active-profile order or winning override is claimed.
- Lane: offline static. No game, save, co-save, plugin, or archive was modified.

## Record and schema checks

1. Retrieve Dawnguard.esm REFR 02009742 and 02017772 with subrecords through the strict Python 3.12 dispatcher and direct read-only TES4 parser. Preserve the plugin hash and raw JSON hashes under ignored .local/.
2. Decode XESP parent and flag byte using TES5Edit dev-4.1.6 Core/wbDefinitionsTES5.pas. The field layout is a reference FormID, a U8 Flags field (bit 0 opposite-parent, bit 1 Pop In), and three unused bytes.
3. Select the REFR header flag variant using the child/parent base signature. Read the Initially Disabled bit separately from the Persistent bit; do not generalize flag names across base-type variants.
4. Compare the base-field result with EV-0277's script and route screen. Do not infer loaded state, physical collision, access, or quest progression from a schema decode.

## Interpretation

- H1 is supported if XESP bit 0 is clear and the Initially Disabled bit is clear on child and parent.
- H2 is supported if either XESP bit 0 or a child/parent Initially Disabled flag is set.
- Physical access remains a separate question requiring exact-order and clean-save route observation; EV-0260 records that the necessary profile/save/Observer lane is not configured.
