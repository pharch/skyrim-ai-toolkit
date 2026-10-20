# EXP-0122 — Hit resolver caller scope

**Status:** bounded GOG static caller map recorded; ordinary-hit coverage and all Steam runtime outcomes remain open.

**Objective:** Q-0073 / OBJ-2. Determine whether the two observed callers of the GOG HitData skill resolver establish a general ordinary incoming-player-hit route or only scoped event/state paths.

**Result:** the tagged event-dispatch case calls `FUN_1406bb690` with an Actor pointer and two event bytes. A separate Actor-state function calls the same helper only after a virtual state predicate and current-process target comparison. The helper calls the known `FUN_1406bcaa0` resolver at two sites. Corrected EV-0397 coverage is 95 unique worker callers, 33 decompiled bodies and 62 remaining; the original 64 count is a storage cap, not the complete caller count. None of the 33 inspected bodies contains a tag-0xB constructor, and a repeated function-pointer table plus its non-function data entry does not identify an owner. Ordinary physical-hit coverage remains unknown. See EV-0397, EV-0423 and [results](results.md).

**Boundary:** read-only GOG AE 1.6.1179.0 static analysis only. The findings do not transfer RVAs to installed Steam AE 1.6.1170.0 and do not prove a successful block, effective protection, AV9/AV11/AV12 progress, or a vanilla exploit. EV-0260 still blocks the exact Steam hit/protection/raw-AVSK test.
