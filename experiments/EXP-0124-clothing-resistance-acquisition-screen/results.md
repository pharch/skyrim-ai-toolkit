# Results

## Exact five-master acquisition screen

EV-0403 scanned 1,178,548 records and 5,791,306 subrecords in the exact
Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm files
for all 34 Clothing resistance candidates from EV-0398. Its 182 raw byte hits
were grouped into 59 candidate record/subrecord groups; 42 were ACHR.XRGD byte
coincidences and are not semantic item links. The semantically inspected
records support two distinct source routes:

- **Fixed placement:** Skyrim.esm ARMO `0007C92E` ClothesMGBootsArchmage has
  Clothing type 2, `DNAM 0`, and EITM `000AD488` with Shock Resist AV42
  magnitude 40. Fixed REFR `00077D05` is placed in CELL `000CAB92`
  WinterholdCollegeArchMageQuarters, which has owner `00103372` [EV-0404].
  The local UESP snapshot says the quarters are locked until Under Saarthal and
  the boots are owned; First Lessons precedes Under Saarthal; its level 6 is
  described as suggested, not a proven minimum [EV-0406]. This is a fixed
  source, not a demonstrated level-one route. The source records screened so
  far do not establish entry, theft legality, or actual protection.
- **Random vendor list:** Lucan Valerius's Riverwood Trader faction points to
  merchant chest `00078C0C`; Update.esm's official-scope override retains
  four entries from `LItemEnchJewelryAll75` with a 25% chance-none. One
  level-1 branch reaches Resist Magic ring `0010DFC8` through three nested
  leveled lists [EV-0405]. The branch is possible, not guaranteed; the ring
  is Clothing type 2 with `DNAM 0`, not physical armor. No inventory roll,
  purchase, or live resistance measurement was observed.

The reference screen also found College outfit memberships and other QA,
high-level, or story-linked sources. Byte hits without a decoded semantic
item field were retained as candidates only. The exact captures and local
source hashes are in EV-0403–EV-0406; none resolves a profile-specific winner.

## Bounded conclusion

A fixed clothing-resistance item source exists in the official records, so the
claim that the screened candidates have no fixed source is falsified. Its
location is quest/ownership gated according to the secondary-source lead, and
physical level-one access remains unresolved. The Riverwood ring is a
non-deterministic alternative. Neither route is a physical armor-rating or
zero-armor-XP result. Continue with Q-0076 on the College route's explicit
level conditions and room access; preserve the clean Steam level-one and
protection/AVSK comparison under EV-0260.

## Targeted Q-0080 addendum — ARMO 000FC061

The level-8 Resist Magic necklace ARMO `000FC061` has an indirect NPC
inventory route in the exact official-master records. The direct
`LItemEnchNecklaceResistMagic` table (`0010106C`) contains the target at LVLO
levels 8, 9, 10, and 11. Its LVLF flags are `All Levels` and `Each`; the item
rows do not make it eligible below the request level. The parent chain reaches
that table through `LItemEnchNecklaceAll` and `LootCitizenNecklaceList`, then
through `LootCitizenNecklaceList25` (fixed 75% chance-none) from
`LootCitizenPocketsCommon`. The common pocket list itself has `Use All`, which
returns its listed children; it does not remove the nested necklace table's
level threshold. The five-master scan found 341 NPC records that directly
reference `LootCitizenPocketsCommon`, 79 that reference
`LootCitizenPocketsRich`, and Brelas as the one direct NPC reference to
`LootCitizenNecklaceList` [EV-0646], [EV-0647].

One useful candidate owner is Madesi (`Skyrim.esm:0001B072`): the NPC record
contains `LootCitizenPocketsCommon`, and its ACBS fields encode level 8 with
`PC Level Mult` off. The revision-pinned local UESP page identifies him as a
level-8 Riften merchant. This gives a concrete level-one test target, but does
not establish the level passed to his nested inventory lists or that the
random item is generated or obtainable in play [EV-0645], [EV-0648].

The competing models remain open. If the nested LVLI request uses the
level-one player's level (or an encounter-zone value no greater than 7), the
level-8 row is ineligible. If this NPC's default inventory request uses
Madesi's actor level, the target row is eligible at level 8, subject to the
chance and table selection. The UESP Leveled Lists page says a request usually
uses player level, possibly modified by encounter-zone level; it does not
resolve this particular NPC inventory call. A clean level-one trial that
checks Madesi's naturally generated inventory, with an appropriate higher-
level control, is the discriminating test. Console item grants are not a
valid acquisition result.

This is still only a magic-resistance clothing candidate. ARMO `000FC061` has
zero physical DNAM and modifies AV44 through its enchantment [EV-0398]. Its
resistance consumer `MagicTarget::CheckResistance` is a virtual function
separate from the mapped physical HitData AV11/AV12 selector; the fresh GOG
target query again has no direct caller references, so a callsite/receiver
scan remains open. No level-one damage reduction, physical armor protection,
Heavy/Light AVSK delta, or OBJ-1 quest/encounter transition is established
[EV-0400]–[EV-0402], [EV-0649].

## Q-0080 caller-context result — GOG static only

The first whole-program `+0x50` scan printed a capped general operand sample and was not used as a no-caller result. A follow-up scan completed over 5,654,579 GOG instructions, counted 17,530 `+0x50` memory operands, and emitted linear context for all 2,400 matched indirect callsites across 1,400 functions. General operand detail remained capped at 2,048, while the targeted call contexts were uncapped [EV-0650].

One candidate at RVA `0x6C6AEB` in `FUN_1406c68d0` forms `RCX=RSI+0xA0`, loads that subobject vtable, and calls slot `+0x50`. The containing decompilation confirms the `this` pointer is `param_1+0xA0`; the corresponding object also exposes an ActorValueOwner-shaped subobject at `param_1+0xB8`. These offsets match the RTTI/CommonLib-mapped Actor::MagicTarget and ActorValueOwner layout; the `+0x50` dispatch is the mapped `MagicTarget::CheckResistance` slot `0x0A` target [EV-0400]–[EV-0402], [EV-0651].

`FUN_1406c68d0` iterates target effect entries, applies entry predicates, invokes resistance checking, uses that return to scale accumulated effect values, and reads ActorValues through the `+0xB8` owner. It has three direct incoming edges from `FUN_1407ee620` and `FUN_140764c30` [EV-0651]. `FUN_1407ee620` also calls `FUN_1406be430`, the vector/physics-like helper previously seen from mapped HitData code. The captured arguments differ from the HitData-shaped call, and the bounded helper review has no direct AV11/AV12/UseSkill sink [EV-0600], [EV-0652]. Keep code reuse as a graph edge only; do not infer a shared ordinary-hit event or an armor-XP effect.

This resolves the static caller question for the sampled candidate and strengthens the magic-resistance mechanism. It does not show that a particular live incoming attack reduced Health, that Madesi naturally generates the item at player level one, or that the candidate provides physical armor protection or zero Heavy/Light XP. The decisive Steam inventory, matched-hit, effective-protection, and raw-AVSK observations remain open under EV-0260. Claims CL-L458–CL-L460, mechanism M-0198, and contradictions C-OBJ2-Q80-RESISTANCE-CLOTHING-VS-FUNCTIONAL-ARMOR and C-OBJ2-Q80-NPC-INVENTORY-REQUEST-LEVEL record the boundary.

