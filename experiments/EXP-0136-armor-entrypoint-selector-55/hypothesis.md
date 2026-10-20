# EXP-0136 hypothesis outcome

Q89's initial alternatives were resolved only within the static scopes:

- **H1 supported:** the cached contribution is passed by pointer through selector 0x55; a concrete callback can alter it, and official source rows include SetValue 0.0 [EV-0696], [EV-0697].
- **H2 falsified for the captured static path:** the callback does not leave every value untouched, and two source MGEFs link to the zero-setting perks [EV-0696], [EV-0697]. Runtime activation remains unknown.
- **H3 falsified as a multiplier-only model:** the official selector rows are not all positive multipliers; SetValue 0.0 rows exist. No negative multiplier occurs in the five-master screen. A zero item contribution does not establish a negative or positive total armor rating [EV-0697].

## Q90 bounded result and Q91 continuation

In the captured GOG path, `FUN_1407ddf50` copies HitData `+0x50` to `+0x54` before later target-side AV39/armor-factor reductions to `+0x50`. The unblocked armor award uses `+0x54` after a separate positive raw-DNAM scan [EV-0670], [EV-0690], [EV-0699]. The captured bodies do not directly dispatch selector 0x55 on the points field [EV-0696], [EV-0699]. This narrows the conclusion to the direct path; upstream selectors run before the copy.

Q91 screens those pre-snapshot selectors. Neither static investigation establishes effective armor protection or zero armor XP on Steam. EV-0260 remains the matched-hit, protection, raw-AVSK discriminator.
