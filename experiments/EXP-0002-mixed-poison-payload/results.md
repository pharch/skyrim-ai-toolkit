# Results

User correction — 2026-09-23: the core exploit is already confirmed. A
poison-classified mixed item boosts beneficial secondary effects under negative
Poison Resistance. The practical bottleneck is delivery: frenzy a follower,
allow the follower to hit the player, then calm the follower. The remaining
research target is therefore convenience/duration optimization, not proof of
amplification.

No new runtime result in the canonical root. A previous Steam probe observed the shape of a dynamic mixed poison but did not preserve recipe, amplification, delivery, or Alchemy budget.

Static prioritization — 2026-09-23: promote Nightshade (`0002F44C`) + glowDust
(`0003AD73`) as the first user-test candidate. The shared effect set contains
hostile `AlchDamageMagickaRate` and beneficial `AlchFortifyDestruction`; the
finite cost proxy is approximately 79.245 versus 21.077, and the combination
has no direct Damage Health anchor. This predicts poison classification only
if the hostile entry leads the commit matcher. It is not yet runtime-confirmed.
