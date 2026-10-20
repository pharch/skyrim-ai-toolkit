# Predicted outcomes

| Observation | H1: additional damage or armor behavior | H2: reads, gates and cleanup |
|---|---|---|
| A resolved target supplies an additional conditional value consumed by the `+0x50` multiplier | Supports H1 | Falsifies H2 for that branch |
| The target's value is selected from `HitData.weapon +0x194` and weapon may be null on a caller route | Supports H1 for weapon-bearing uses; bounds it to null/non-null route state | Falsifies H2 for weapon-bearing uses, but not for weapon-null routes |
| The HitData-associated `+0xC0` slot-`0x4` call returns attack damage used only in the `+0x5c` calculation | Does not support H1 | Supports H2 for this site |
| The Actor `+0xA0` slot-`0x4` call gates a clear of several damage fields | A separate conditional clear, not another multiplier | Supports H2 for this site |
| A virtual target cannot be typed or its derived target set is incomplete | Leaves H1 open | Does not support H2 as a complete result |

No static outcome alone establishes positive worn-armor protection, zero Light/Heavy Armor AVSK, Steam equivalence, or a vanilla level-one exploit.
