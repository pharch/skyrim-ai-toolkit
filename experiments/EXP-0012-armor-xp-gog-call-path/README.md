# EXP-0012 — GOG hit-to-armor-skill call path

**Status:** Completed as a bounded static mechanism investigation; no gameplay result.

**Objective:** OBJ-2 baseline Q-0003, with field-routing follow-up Q-0017. Establish how an incoming hit routes armor and Block skill use, then separate that from the unproven question of whether effective protection remains when armor XP is suppressed.

**Result:** A hash-attested GOG AE 1.6.1179 query found an inline player-receiver AV11/12 branch for unblocked hits with qualifying positive-DNAM armor and an AV9 Block branch for blocked hits. Both dispatch through Actor::UseSkill slot 0xF7; the concrete PlayerCharacter override rejects non-positive points. EV-0261 adds that AV39 and the armor-base-factor sum reduce HitData total damage before blocked-hit bookkeeping and the receiver skill branch. The concrete AV39 getter's clamp behavior and any live protection/XP result remain unknown. The legacy `[RSP+0xA0]` positive guard is on the attacker-side call, not a direct guard on receiver armor XP. See [protocol](protocol.md) and [results](results.md).

**Evidence:** EV-0217–EV-0223 and EV-0261, with historical lead EV-0036. GOG 1.6.1179 is separate from installed Steam AE 1.6.1170. No live hit, effective-protection delta, raw AVSK delta, profile winner or vanilla exploit was established.
