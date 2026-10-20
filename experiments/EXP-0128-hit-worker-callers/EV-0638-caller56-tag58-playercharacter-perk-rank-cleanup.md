# EV-0638 — Caller 56 tag-0x58 PlayerCharacter collection and perk-rank cleanup

## Competing models and discriminants

- H1, perk-rank/collection cleanup: tag 0x58 supplies an object and a mode byte to PlayerCharacter collection-removal code, with a FindPerkInRanksVisitor lookup when the object is no longer present in the relevant collection. It predicts the observed object-list scans, reference/list removal, RTTI-verified visitor, and pointer-match method.
- H2, HitData/effective-armor/armor-skill route: the object or a descendant reaches hit/protection/AV11/AV12/UseSkill processing. It predicts a producer-backed edge to a mapped combat/skill sink, including through dynamic callbacks.
- H3, level-gated perk access change: this cleanup changes perk eligibility or grants access to a gated perk. It predicts a rank/eligibility mutation or a positive perk-add/level condition; a removal and list cleanup alone do not support it.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata verifies read-only queries, auto-analysis disabled, and matching executable identity. GOG addresses are not transferred to Steam AE 1.6.1170.0.

- FUN_140658cc0 writes tag 0x58, copies its object pointer and one mode byte, then submits the record through FUN_14065b800. Its two direct producers FUN_14074b200 and FUN_14074b330 each require a nonnull object and pass mode 0 or 1 respectively [EV-0638].
- Dispatcher case 0x58 passes the PlayerCharacter singleton DAT_143188918, the queued object, and the mode byte to FUN_14074b350 [EV-0637], [EV-0638]. PlayerCharacter identity is independently verified [EV-0344].
- FUN_14074b350 has five direct calls and no indirect sites. It checks/removes the object across collection fields +0x4e8/+0x4f8 and +0x4d0/+0x4e0; one mode decrements a paired reference count before compacting. Its equality helper FUN_1407540f0 is a direct pointer comparison. Under the captured conditions it calls FUN_140750f70 for further cleanup [EV-0638].
- FUN_140750f70 scans a PlayerCharacter list at +0x4b8 with a stack visitor whose RTTI is verified as BGSPerk::FindPerkInRanksVisitor at RVA 0x18a5ef8 [EV-0638]. The visitor method FUN_140390a80 returns a match when the candidate pointer equals its stored object pointer and saves the matched rank entry [EV-0638].
- On a visitor match, FUN_140750f70 removes the rank entry, invokes PlayerCharacter vtable slot +0x650, then calls FUN_140225820 and conditionally FUN_140238a60. The latter resets two float fields to -1.0. A pointer read at primary Actor table base RVA 0x189ec20 plus 0x650 resolves to FUN_1406b21d0, which is empty in this GOG image; however, DAT_143188918's runtime PlayerCharacter vtable/override at that slot is not identified, so the actual virtual target remains open [EV-0400], [EV-0344], [EV-0638].
- FUN_140750f70 has five direct calls and one unresolved dynamic PlayerCharacter slot +0x650 call. The visitor comparison itself is resolved to FUN_140390a80. No mapped direct HitData, protection, AV11/AV12 or UseSkill sink appears in the bounded route [EV-0638].

## Result and limits

H1 is supported for the captured static path as conditional PlayerCharacter collection and perk-rank cleanup. H2 has no mapped direct sink in the bounded path, but the runtime PlayerCharacter virtual override at +0x650 remains unresolved. H3 is not supported: the captured route removes a matched rank entry and shows no perk-grant, eligibility-level comparison, or level-gate bypass. No armor-XP bypass or bounty outcome follows, and no causal edge is added to HitData, protection, AV11/AV12, UseSkill, or level-one quest access.

## Next action

Continue worker caller 57/62, FUN_140658d00, with an exact tag, payload, and producer trace.
