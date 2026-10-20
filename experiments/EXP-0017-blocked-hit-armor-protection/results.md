# EXP-0017 results

## Static evidence

EV-0222 shows the GOG blocked player-receiver route selects AV9 and skips the unblocked AV11/12 armor-skill route. EV-0261 shows the GOG hit builder copies physical damage, applies AV39 and the armor-base-factor result to total damage, and only later sets the blocked flag. EV-0263 resolves the PlayerCharacter slot `0xE7` implementation used by the armor-base-factor call: it returns a float stored at `this + 0x274`, with two virtual calls when the stored value is negative. Together these support the source-order component that armor-factor calculation precedes blocked-hit receiver routing.

The field at `+0x274` has not been independently named from a layout source, no positive value or actual worn-armor reduction was measured, and the GOG result is not transferred to Steam 1.6.1170.0. The source-order result does not establish XP deltas or level-one budget.

## Runtime result

Not run. EV-0260 records missing selected disposable profile, complete active order, clean save, deployed/loaded Observer, and live bindings. No live hit, protection, AVSK, or vanilla reproduction claim is made.

## Next discriminant

After prerequisites are independently verified, follow the matched four-condition protocol above and preserve raw AV9/11/12 `UseSkill` arguments, HitData, protection comparison, AVSK deltas, and save identity. Until then, continue available static OBJ-1 research.
