# EXP-0019 results

## Direct observations

- DA07StartNode `SMQN:00094D8F` points to `DA07intro` `QUST:00094D89`. Its raw condition contains function index 80, comparison 20.0, and PlayerRef; EV-0019's corrected decoder identifies the node predicate as GetLevel >=20. This static record is not a live gate observation.
- DA07intro's `Pamphlet` alias has ALCO `00094D8B`, base `BOOK:DA07MythicDawnMuseumPamphlet`, and is bound to `DA07PamphletScript`. QF VMAD maps Fragment_0 to stage 0, and the PEX adds the alias reference to WICourier there.
- `DA07PamphletScript` extends ReferenceAlias and calls owning-quest `SetStage(5)` only after player equip or a container change into the player, when stage 5 is not done.
- The base BOOK has no VMAD. The two INFO TIF PEX scripts remove a copy from the player and add it to the speaker; they contain no SetStage call. The exact raw FormID scan found no placed REFR NAME for the base BOOK in the five official masters.
- Direct observation and provenance are retained in EV-0265. The local UESP pages are revisions 3507117 and 1768959. `Skyrim - Misc.bsa` is SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`.

## Decision

H1 is falsified for the standalone pamphlet-alias mechanism in this bounded official-file/PEX screen. H2 is supported at the record/script level: the stage-5 callback belongs to a quest-created alias and the screened base-book/dialogue path does not create that alias or invoke its callback. This does not exclude another script or native writer starting DA07intro.

The complete five-master screen found an independent `DA07IntroTrigger` that requests stage 7 on the same intro quest. That path is recorded separately in EV-0266 and Q-0019. Neither path has a live level-one result; EV-0260 records missing save/profile/Observer prerequisites.

## Cross-domain note

There is no supported causal edge from the DA07 alias/quest path to the OBJ-2 HitData/armor skill route. No shared form, ActorValue, native call, or serialization mechanism was identified. The quest question remains P0, and armor lines M-0017/M-0018 remain independent.
