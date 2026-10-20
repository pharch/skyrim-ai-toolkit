# EV-0637 — Caller 55 tag-0x57 numeric threshold and registry route

## Competing models and discriminants

- H1, ordinary-hit/armor route: tag 0x57 or a descendant performs HitData, effective-protection, AV11/AV12 or UseSkill work. It predicts a producer-backed data/control edge to a mapped combat or skill sink.
- H2, gated numeric-state notification: the producer compares a supplied numeric value with a separate limit, uses per-category state bits, and sends a small code through tag 0x57 to registry handling. It predicts literal category/code pairs, a numeric predicate, a worker dispatcher case, and a registry helper.
- H3, specifically named ActorValue or quest semantics: the literal categories and codes correspond to named game concepts. It predicts corroborating record/source names or a verified consumer mapping; numeric literals alone are insufficient.

## Direct GOG evidence

All captures are from the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata verifies read-only queries, auto-analysis disabled, and matching executable identity. GOG addresses are not transferred to Steam AE 1.6.1170.0.

- FUN_140658c90 writes worker tag 0x57 and copies its 32-bit argument into the following payload field, then calls FUN_14065b800. Its only analyzed direct producer is FUN_14075a430 [EV-0637].
- FUN_14075a430 has two direct calls and no indirect sites. Its predicate is (category != 0x18 or value > 0) and value < limit. When global DAT_1420f7e00+0x160 is nonzero it calls FUN_140971910(code) directly; otherwise it queues tag 0x57 with that code. It returns true on the qualifying route [EV-0637].
- The only analyzed caller of FUN_14075a430 is FUN_14074b720, which calls it for literal categories 0x18, 0x19 and 0x1a with threshold globals DAT_142008060, DAT_142008078 and DAT_142008090, and code values 0xfc, 0xfd and 0xfe. It tests and updates distinct bits 3, 4 and 5 in its receiver field +0xbe4. The captures do not establish the names of these categories or codes, and do not show a previous-value comparison; this is a bounded numeric predicate, not proof of a crossing event [EV-0637].
- Worker dispatcher case 0x57 passes payload field 2 to FUN_140971910 [EV-0637]. That helper has six direct calls and zero indirect sites. Its direct body binary-searches an integer list; when the code is absent and initialization gates pass, it invokes FUN_1409786e0 and inserts the code through FUN_140971e00. No mapped HitData, protection, AV11/AV12 or UseSkill call appears in this bounded helper body [EV-0637].
- The registry helper is also called from 16 other analyzed functions, so the route is a shared registry primitive. This code reuse does not show what named record or runtime object the codes represent [EV-0637].

## Result and limits

H2 is supported for the captured direct route: caller 55 is a gated numeric value/limit notification that carries one of codes 0xfc-0xfe through tag 0x57 to registry handling. H1 has no mapped direct sink in this bounded path. H3 remains unverified: do not label the categories as ActorValues, Health/Magicka/Stamina, quest stages, or achievement codes from these literals alone. The dispatcher has other unresolved cases and registry descendants are not fully traced, so no transitive no-hit, Steam, effective-protection, armor-XP, or bounty conclusion follows. No causal edge is added.

## Next action

Continue worker caller 56/62, FUN_140658cc0, with an exact tag/payload and producer trace.
