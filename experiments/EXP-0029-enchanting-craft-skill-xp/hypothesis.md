# Hypothesis

## H1 — Input-sensitive or quantized craft credit

The skill-use award may vary with the selected item, enchantment/effect count, or soul size, with rounding producing discrete raw-progress steps. Matched crafts that vary one of those inputs should produce different raw Enchanting progress or a repeatable step boundary.

## H2 — One station-selected award per craft, accumulated below the level display

Each successful craft confirmation may dispatch one station-selected `UseSkill` call with a fixed points input. Raw progress can change while the displayed skill level remains the same; the level changes only when accumulated progress reaches its current threshold.

These are competing models for the source of the per-craft credit, while rounding can still occur in H2's downstream threshold calculation. Static evidence EV-0280 narrows H1 at the visible GOG callback call site and is consistent with H2. It does not provide a raw XP measurement or resolve the global points value.
