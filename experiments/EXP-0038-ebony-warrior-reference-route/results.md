# EXP-0038 results

## Direct observations

- `Dragonborn.esm` SHA-256 is `5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b`. Its direct ACHR scan returned 1,309 records and one NPC-base match: ACHR `02030CC9` (`DLC2EbonyWarriorRef`) uses NPC_ `020285C3`.
- The ACHR raw header flags are `00000800`; its subrecords include `NAME=020285C3`, `XLCN=02035BF3`, and placement `DATA`, with no XESP subrecord. TES5Edit `wbDefinitionsTES5.pas` maps ACHR header bit 11 to Initially Disabled and defines XESP as Enable Parent. The parser does not return the parent CELL group.
- QUST `0202C49E` alias `EbonyWarrior` uses ALUA `020285C3`, which TES5Edit defines as a Unique Actor fill. EV-0288 records that its stage-10 fragment enables and moves the alias reference to CityCenter.
- PERK `0203D291` (`DLC2EbonyWarriorPickPocketMod`) has a CTDA containing NPC base `020285C3`; EV-0288 records that stage 10 adds this perk to the player. This is a quest consequence, not another actor placement.
- One strict-dispatcher raw-subrecord scan walked all record entries in each official master file and searched for the little-endian bytes of `0202C49E`, `02030CC9`, and `020285C3`:

| Source | File SHA-256 | Records scanned | Subrecords scanned | Matching records |
|---|---|---:|---:|---:|
| Skyrim.esm | `2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107` | 869,688 | 4,131,336 | 0 |
| Update.esm | `c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9` | 16,388 | 219,863 | 0 |
| Dawnguard.esm | `1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4` | 95,719 | 513,471 | 0 |
| HearthFires.esm | `ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97` | 18,037 | 114,331 | 0 |
| Dragonborn.esm | `5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b` | 178,716 | 812,305 | 20 |

- Dragonborn.esm produced 25 matching subrecords across 20 records. The hits are confined to the target QUST alias/VMAD; its SMQN child link; six DIAL and three INFO records; four quest-bound PACK records; the stage-granted PERK; three location-reference fields in LCTN `02035BF3`; and linked DLBR/DLVW records. The exact raw matches and counts are retained in `TX-20261016-0026/*-all-formid-hits.raw.jsonl`.
- The QUST-only screen across all five official masters found the NPC base and placed-reference bytes only in Dragonborn.esm QUST `0202C49E`, where the base occurs in its ALUA alias field. No other QUST record contained either byte sequence.

## Interpretation

The installed official files serialize one placed Ebony Warrior actor, and it begins with the Initially Disabled record flag. That same NPC base fills the gated quest's Unique Actor alias; the documented stage-10 fragment enables and moves the alias reference. The screen therefore supports the gated alias path and finds no independent static actor placement or direct record-configured start route in the five official masters.

## Limits

This is a bounded source-file result, not a winning-record/profile result. The direct parser does not include parent cell groups or resolve overrides. Raw byte coverage does not rule out dynamically constructed references, arbitrary PEX behavior in BSA archives, Creation Club/user plugins, or runtime code/state. No level-one transition, loaded disabled state, vanilla candidate, or reproduction was observed. The exact event-data location-slot direction from EV-0288 remains unresolved.

Raw outputs and hashes are below ignored `.local/alignment/transactions/TX-20261016-0026/`. `capture-files.sha256` is the private manifest; its hash and verification status are recorded in EV-0290.
