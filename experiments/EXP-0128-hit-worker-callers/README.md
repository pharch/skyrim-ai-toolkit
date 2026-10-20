# EXP-0128 — Remaining HitData worker callers

- **Frontier:** Q-0079 (OBJ-2)
- **Question:** Do the 62 direct caller functions not decompiled in EV-0397 include a tag-0xB event producer that reaches the GOG HitData skill resolver?
- **Scope:** Existing GOG Skyrim AE 1.6.1179.0 Ghidra project, queried read-only with auto-analysis disabled. No GOG RVA or runtime result transfers to Steam AE 1.6.1170.0.
- **Starting evidence:** EV-0397 contains 95 direct call sites from 95 unique caller functions; EV-0423 verifies the same caller set in a fresh query, confirms 33 caller bodies decompiled, and identifies 64 as the query's storage cap, leaving 62 bodies. EV-0291 maps the tag-0xB dispatcher and resolver routes. EV-0260 preserves the unavailable Steam hit/protection/raw-AVSK discriminator.
- **Protocol and outcomes:** [protocol](protocol.md), [hypotheses](hypothesis.md), [discriminants](expected-discriminants.md), [results](results.md), and [implications](implications.md).
