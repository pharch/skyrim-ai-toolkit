# Expected discriminants

1. Whether a successful EnchantMenuCraftCallback path reaches `Actor::UseSkill` once, and whether its skill/points arguments depend on selected item, effect count, or soul size.
2. Whether the PlayerCharacter skill-progress path stores a sublevel progress delta before checking the level threshold.
3. Whether the ordinary official Enchanting workbench's `WBDT.usesSkill` field resolves to AV23.
4. On a verified Steam runtime, whether matched raw AVSK deltas are equal for one-factor item/soul changes and whether two crafts accumulate two deltas.
5. The live measure must expose raw progress and the next-level threshold; UI level alone cannot distinguish no XP from subthreshold XP.

EV-0280 and EV-0281 resolve discriminants 1–3 for a scoped GOG/static plus base-record path. Discriminants 4–5 remain unmeasured because the live instrument and disposable save are unavailable (EV-0260).
