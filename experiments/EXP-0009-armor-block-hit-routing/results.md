# Results

The hashed historical GOG analysis reports a receiver branch on the blocked flag that calls UseSkill for AV9 with physicalDamage minus totalDamage and skips worn-armor AV11/12 calls. It explicitly warns that ordinary blocked points may remain positive. No live hit was measured in this setup.

**Lane:** `mechanism_inference` (legacy report review).

**Not performed:** runtime test, current xEdit load, or live-game inspection; AE target and active order are not verified.

## Next action

Only after AE executable ProductVersion and the complete active profile order are verified, perform matched unblocked/blocked hits and capture hit flags, damage fields, AV9/11/12 calls, armor rating, and raw AVSK progress.
