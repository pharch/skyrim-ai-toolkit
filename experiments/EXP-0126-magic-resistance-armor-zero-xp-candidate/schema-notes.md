# Schema notes

- The exact ARMO record returned by the direct TES4 parser is Skyrim.esm `0002AC61` (`DA05SaviorsHide`). The parser preserves BOD2 and DNAM as raw bytes; this note does not infer the values' gameplay meaning from the EditorID.
- The ARMO EITM raw bytes decode little-endian as FormID `001097B7`. The linked ENCH record and each EFID/EFIT pair must be queried before assigning resistance semantics.
- Keep direct TES4 parsing distinct from the native xEdit five-master scope and from any active-profile winner. UESP item categories are secondary evidence only.
- For native code, EV-0217/EV-0218/EV-0222 provide the current type and field interpretations for Light/Heavy eligibility, HitData and AV11/AV12 in GOG AE 1.6.1179.0. Recheck exact current build identity and preserve the caller/producer boundary.

## Decoded records — 2026-10-18

- The saved decode output is `.local/alignment/transactions/TX-20261018-0011/saviors-hide-records-decoded.json`. It reads BOD2's second `u32` as armor type `0` (Light Armor) and DNAM as signed `2600`; EITM resolves to `001097B7` [EV-0415].
- ENCH `001097B7` has two EFID/EFIT pairs: MGEF `00109637` / magnitude `15.0`, and MGEF `000FF15E` / magnitude `50.0`; both area and duration fields are zero in the captured EFIT rows. The corresponding MGEF DATA fields decode to archetype `34` and primary ActorValues `44` and `40`; neither capture contains CTDA rows [EV-0416]. Interpretations use the retained TES5Edit dev-4.1.6 schema notes and are not a live effect measurement.
- DA05 QUST `0002A49A` VMAD binds the `SaviorsHide` property to FormID `0002AC61` and `Fragment_20` to stage 100. The separately retained PEX capture supplies the `AddItem` call [EV-0415], [EV-0386].
- Exact plugin records are from the base official Skyrim.esm source and the direct TES4 parser. They do not establish a profile winner, reward execution, clean level-one availability, or effective Steam resistance.
