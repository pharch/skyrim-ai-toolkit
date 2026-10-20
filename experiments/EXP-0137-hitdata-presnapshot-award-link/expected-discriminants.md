# Expected discriminants — EXP-0137

| Model | Static prediction | Runtime discriminator |
|---|---|---|
| Selector 0x55 alters only the later cached armor factor | No direct 0x55 dispatch to HitData `+0x54`; award reads `+0x54`, while positive DNAM controls armor eligibility | Selector-0x55 effect can alter protection, but repeated landed hits with positive effective protection still change AV11/AV12 AVSK |
| Award uses post-mitigation totalDamage | Resolver points argument reads `+0x50` after AV39/armor-factor transforms | A trace shows points track post-mitigation `+0x50` |
| Earlier modifier zeros pre-snapshot input | One pre-snapshot selector/data path writes the field or award guard before the copy | Hit remains registered, armor protection is separately positive, and raw armor AVSK remains unchanged |

The third model needs a separate source screen and cannot be decided from the selector-0x55 callback. A zero-damage event is not by itself proof that armor supplied protection.
