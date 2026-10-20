# Results

## Direct player-level gates

The hash-identified Skyrim.esm QUST records show two CTDAs on First Lessons
(`0001F251 MG01`) and eleven on Under Saarthal (`0001F252 MG02`); neither has a
function-index-80 `GetLevel` condition. EV-0321's complete official-five-master
census independently has zero `GetLevel` rows for either QUST and no malformed
CTDA lengths [EV-0407]. The exact Skyrim.esm hash is
`2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107`.

The group-ancestry join followed every DIAL whose QNAM points to MG01/MG02 to
its INFO children [EV-0409]: 96/69 DIAL topics and 159/103 INFO children. No
DIAL or linked INFO has a `GetLevel` CTDA. The complete five-master Story
Manager level-node map selects no MG01/MG02 child [EV-0300]. The observed
dialogue conditions include stages, aliases, items, spells, perks, race/sex,
locations and `GetVMQuestVariable`; that variable's INFO operand remains
unresolved. Condition names are grounded in the pinned TES5Edit schema in
[schema notes](schema-notes.md).

The four exact PEX files for TIF `00107E3D`, its helper quest script, `QF_MG01`
and `QF_MG02` were byte-matched to streams in the configured `Skyrim - Misc.bsa`
(17,713,449 bytes, SHA-256
`ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`, BSA
header version 105). Each PEX parsed fully as version 3.2, no loose
`Data/Scripts` copy was present, and no disassembled method call is named
`GetLevel` [EV-0413]. This is a bounded base-archive source check, not a full
profile winner query.

## Door and key handoff

CELL `000CAB92 WinterholdCollegeArchMageQuarters` has 477 REFR children. The
paired Hall of the Elements door references are quarter-side `000CC821` and
Hall-side `000CC81C`; the Arcanaeum pair is `00109680`/`0010967F`. The Hall and
Arcanaeum endpoints store XLOC lock byte 255 and key FormID `000C5140`; two
additional `WinterholdLDoorMinUse` references use the same key. The selected
DOOR base records contain no VMAD or CTDA fields [EV-0410]. A complete
five-master raw reference screen finds the key on those four door records, in
QA container `000C2CDB`, and as a property of INFO `00107E3D` [EV-0411].

INFO `00107E3D` is a child of DIAL `00107E36
DialogueWinterholdCollegeTolfdirPostForcegreetTopic`, owned by helper QUST
`0003618F DialogueWinterholdCollege`. Its conditions include
`GetStage(MG02 0001F258) == 200`, a `GetVMQuestVariable` comparison of zero with
an unresolved second operand, and `GetIsID(Tolfdir)` [EV-0412]. Its attached
`TIF__00107E3D` `Fragment_0` calls `Game.GetPlayer().AddItem` for one
ArchMageRobes and one CollegeArchMageKey, then sets the owning quest's
`TolfdirPostQuestFG` property to 1 [EV-0413]. The source record/PEX path
therefore identifies a stage-conditioned key grant; the precise relationship
between the unresolved INFO variable operand and that property is not claimed.

The captured `QF_MG01` `Fragment_18` calls `Start` on MG02 and
MGCollegeLectures. A captured `QF_MG02` fragment completes objective 65,
displays objective 70, and calls `Lock` on its `ArchMageDoor1` and
`ArchMageDoor2` properties [EV-0413]. Fragment-to-stage and property-to-REFR
bindings remain unresolved. This adds source-level quest/door state to the
College progression model; it does not show how a clean level-one run behaves.

## Bounded conclusion and next discriminator

Within the exact QUST, linked dialogue, door and four PEX sources, the College
route is controlled by quest stage and key/door state, with no direct
player-level CTDA or `GetLevel` method call [CL-L237], [CL-L238]. The records
and scripts narrow the route; they do not prove level-one quest completion,
room entry, lawful use of the owned boots, or a vanilla bypass. The exact
`GetVMQuestVariable` operand, some fragment/door bindings, hazards, full active
profile, and live access remain open [EV-0260]. No causal edge to armor XP or
magic resistance is supported.

