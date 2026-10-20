# Results

## Field correction — EV-0683

The earlier Q82/Q84 interpretation treated EPFT values as handler IDs. The
build-identified BGSEntryPointPerkEntry wrapper shows slot +8 returns
DATA[1] as the handler ID and slot +0x10 returns a separate function-data
pointer. The GOG loader selects the function-data class from EPFT [EV-0681]–
[EV-0683]. The 23 official five-master rows for selectors 37/39 use IDs 1
(one row), 3 (19 rows), and 14 (three file rows); EPFT values 1/2 are class
IDs [EV-0675], [EV-0683]. The raw EV-0675 capture remains valid; its old
EPFT-as-handler interpretation is superseded.

## Actual handler bodies — EV-0684

Handler 3 at GOG RVA 0x386420 gates on function-data type 1 and multiplies the
numeric entrypoint result by the OneValue float at object +8. Handler 14 at
RVA 0x386870 gates on type 2, reads the TwoValue float at +8 as an ActorValue
index and the float at +0xC as a coefficient, then scales the numeric result
using ActorValue*coefficient plus a constant. The three file-level ID-14 rows
are selector-39 AlchemySkillBoosts and PerkSkillBoosts entries (the latter
also appears in Update.esm). Their payload bytes are
00 00 0A 43 0A D7 23 3C, encoding numeric index 138 and approximately 0.01.
CommonLib's mutable ActorValues.h labels 138 BlockPowerModifier; this is a
label reference only, without a pinned commit.

Handler 1 is the one DeflectArrows selector-39 row and is covered by EV-0672.
The captured direct handler writes are numeric result writes. The bodies do
not directly write equipment, HitData, source ActorValues, skill progress, or
event state.

## ActorValue getter side effects — EV-0685

Handler 14 calls ActorValueOwner slot +8 on its actor context. The captured
Actor getter checks an ActiveEffect derived-value cache, computes a value on
miss, sums modifier floats, and stores into the ActiveEffect cache. Its base
value virtual also reads and writes an Actor-side per-value cache. The traced
cache helpers store computed values and associated cache state; direct writes
are to derived caches, lock bookkeeping, or output arguments, not the source
permanent/temporary/damage ActorValue fields. No equipment, HitData,
UseSkill/AVSK, or event sink was identified in the bounded path.

The base-value path includes an indirect ActorValueInfo+0x68 default-value
callback. The static GOG image does not initialize the global ActorValueInfo
table pointer, so its runtime function target for index 138 is unresolved.
This is a concrete limit, not evidence of absence. The getter is therefore not
described as memory-pure, and the static result is not a transitive negative.

## Bounded assessment

The corrected GOG mapping supports synchronous numeric result computation for
the captured official rows and identifies cache-only writes on the traced
handler-14 getter path. It does not identify an equipment interposition
window or a direct source-AV/HitData/skill-progress writer before the
worn-armor scan. The dynamic ActorValueInfo callback, Steam differences,
active-profile winners, and runtime behavior remain open.

No positive armor protection, verified landed hit, raw AVSK change, zero-XP
result, level-one vanilla reproduction, or bounty resolution is established.
EV-0260 remains the exact Steam test requirement.
