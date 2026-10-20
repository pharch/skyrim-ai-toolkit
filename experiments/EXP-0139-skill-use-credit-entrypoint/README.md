# EXP-0139 — Skill-use credit after the positive-points guard

**Status:** Q92 completed as a bounded GOG static and official-record investigation. No OBJ-2 exploit candidate was established.

**Question:** Can the PlayerCharacter progression path reduce Heavy or Light Armor skill credit to zero after a positive HitData points value passes the initial guard, while leaving HitData mitigation and armor protection intact?

**Result:** In GOG AE 1.6.1179.0, PlayerCharacter's progression helper conditionally applies the skill's AVIF `AVSK` use multiplier/offset, dispatches EntryPoint 22 (`kModSkillUse`) against the resulting float, then adds that float to the per-skill progress field before its threshold loop. The caller still rejects points unless they are strictly positive before entering the helper [EV-0221], [EV-0700], [EV-0703].

The five-master AVIF data gives Heavy Armor a use multiplier of 3.8 and Light Armor 4.0, both with zero offset. The full official PERK EntryPoint 22 screen has eight rows; their amounts are positive, and the Heavy/Light rows are positive 1.20 multipliers [EV-0262], [EV-0704]. This rules out a zeroing source in that scoped official layer, not in arbitrary plugins, optional Creation content, or unobserved runtime state.

**Interpretation:** The code exposes an award-side numeric control point downstream of incoming-damage calculation, but the official five-master source rows do not supply a zero or negative Heavy/Light modifier. This is useful causal separation, not a vanilla candidate or runtime result. No armor protection, raw AVSK delta, live Steam behavior, or level-one sequence was measured; EV-0260 remains the required test.

See [hypotheses](hypothesis.md), [predicted discriminants](expected-discriminants.md), [protocol](protocol.md), and [results](results.md).
