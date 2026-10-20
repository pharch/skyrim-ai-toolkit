# EXP-0013 — Negative AV39 and blocked-hit armor XP

**Status:** protocol and static candidate screen complete; live test not run.

**Objective:** OBJ-2 / Q-0015. Determine whether a natural, player-targeted negative Damage Resist state can make the blocked branch's Block points non-positive while worn armor still provides effective protection.

**Static result:** GOG AE 1.6.1179 code routes a blocked player hit to AV9 and skips AV11/12; PlayerCharacter rejects non-positive points. Marked for Death is a plausible AV39 candidate, but WICast's `R2` target semantics and ordinary player reachability remain unresolved. A Haknir AV39 enchant is quest-gated. Neither candidate has been measured in the installed Steam runtime. See [protocol](protocol.md), [results](results.md), and `EV-0217`–`EV-0233`.
