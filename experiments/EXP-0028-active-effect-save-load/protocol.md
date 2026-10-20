# Protocol — EXP-0028

## Static source protocol (completed)

1. Verify the exact existing GOG analysis executable and matching Address Library through the retained adapter; resolve VTABLE::ActiveEffect in this session.
2. Query base ActiveEffect slots Update, CanFinish, SaveGame, LoadGame, FinishLoadGame, Compare, and Finish in the existing project with auto-analysis disabled and read-only mode.
3. Map slots and fields through the hash-identified local CommonLib header. Preserve all metadata and raw output under ignored .local/; keep GOG addresses separate from the installed Steam target.
4. Treat base stubs as base-stub evidence only. Do not infer that timer update, expiry dispatch, or derived-class behavior is absent.

## Runtime discriminator (not performed)

When an exact target build, complete active order, designated disposable test save, and a read-only observer that reports ActiveEffect instances are available:

1. Choose one known finite potion effect and one known finite poison effect; record each item's and base MGEF's FormIDs, duration data, target, numeric level, and executable/order identity. Use an untreated save as a baseline and preserve the original save unchanged.
2. Capture the active-effect list before application, immediately after application, after controlled wait/travel, immediately before saving, immediately after reload, and after any recalculation that could refresh displayed values. Keep a matched no-effect control and a separate deliberate-reapplication control.
3. At every point record target handle, base-effect/source/spell FormIDs, usUniqueID, elapsed time, duration, magnitude, flags/condition, active-list membership, and apply/remove event sequence. Record game time and wall-clock/load boundary separately.
4. A restored logical effect requires matching source/base effect/target/ID across the transition, coherent saved timer fields, continued active-list membership, and no intervening removal/reapplication. A replacement requires a changed logical ID/source or a new apply event; an alternate passive source must be traced independently.
5. Do not use the Magic menu display alone as proof. If the observer cannot expose the required fields/events, record that limitation and do not promote the result. Console commands, injected scripts, edited saves, and modified plugins are not vanilla validation.

No save input or ActiveEffect observer is configured in the current lane (EV-0260); this protocol was not run.
