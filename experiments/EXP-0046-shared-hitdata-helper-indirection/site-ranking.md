# Ranked indirect sites in GOG `FUN_1407ddf50`

Scope: the ten sites captured in EV-0302 and classified in EV-0304, GOG Skyrim AE 1.6.1179.0. Ranking is by relevance to the helper's damage calculation and the OBJ-2 protection/XP question, not by runtime likelihood.

| Rank | GOG RVA | Resolved role | Relevance / route limit |
|---:|---:|---|---|
| 1 | `0x1407de113` | ActorValueOwner `GetActorValue` with index from weapon `+0x194`; conditionally scales HitData `totalDamage` | Additional record-selected damage input on weapon-bearing calls. Actual record indices/values are unscreened; this is not identified as AV39 or armor rating. Skipped by captured ProcessTrapHit construction because weapon is null. |
| 2 | `0x1407de518` | Actor `+0xA0` / MagicTarget slot 4, `IsInvulnerable` | A true return clears several HitData damage fields, but not `physicalDamage`. Base target is a false stub; derived Actor dispatch is not independently mapped. |
| 3 | `0x1407de049` | Actor slot `0xE7`, `GetArmorBaseFactorSum` | Previously mapped AV39/armor-related input into `totalDamage`; positive PlayerCharacter contribution remains unmeasured. |
| 4 | `0x1407de2fc` | Weapon `TESAttackDamageForm` slot 4, `GetAttackDamage` | Supplies attack damage to `percentBlocked`; skipped by the captured trap route's null weapon. |
| 5 | `0x1407de331` | ActorValueOwner `GetActorValue(0x42)`, ShieldPerks | Secondary input to `percentBlocked`; no armor AV11/12 award. |
| 6 | `0x1407de34a` | ActorValueOwner `GetActorValue(0x09)`, Block | Secondary input to `percentBlocked`; does not establish Block XP. |
| 7 | `0x1407de472` | ActorValueOwner `GetActorValue(0xA3)`, ReflectDamage | Contributes to `criticalDamageMult` under local conditions; not an armor skill award. |
| 8 | `0x1407de43e` | Refcount-guarded release dispatch | Cleanup classification; concrete destructor target not resolved. |
| 9 | `0x1407de554` | Refcount-guarded release dispatch | Cleanup classification; concrete destructor target not resolved. |
| 10 | `0x1407de579` | Refcount-guarded release dispatch | Cleanup classification; concrete destructor target not resolved. |

The dynamic `IsInvulnerable` call remains a source/layout inference at the derived-class level: CommonLibSSE-NG commit `b93280e832f263dbef44e44cbe2936622a02f91a` maps Actor's MagicTarget subobject at `+0xA0` and slot 4's name, while the queried matching-GOG base target returns false. The Actor/PlayerCharacter secondary vtable pointer and runtime return were not captured.

Raw query metadata/stdout hashes and CommonLib source hashes are listed in `.local/alignment/transactions/TX-20261016-0039/capture-manifest.json`; that manifest SHA-256 is `397015cac3dafff2d8d6cf1af99428116a073380a0dff433a1e30eade1481c15`. The concise source analysis is `.local/alignment/transactions/TX-20261016-0039/EV-0304-note.md` (SHA-256 `fca7dfab4daa3920a075392ba9183384ca4b685c6088a6878355c7065d33d4ec`).
