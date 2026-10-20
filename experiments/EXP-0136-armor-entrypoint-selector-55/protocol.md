# EXP-0136 protocol

## Static investigation

- Run all research commands through `python3 scripts/python_env.py run` using the validated WSL Python 3.12 venv.
- Verify the GOG executable ProductVersion/hash and matching Address Library afresh before querying any RVA; use the configured existing project with `-process -noanalysis -readOnly`.
- Resolve `VTABLE::Actor` and `VTABLE::PlayerCharacter`; query the exact `+0x100` entry used by the selector helper, then inspect the owning function, call edges and bounded direct targets.
- Capture the exact contribution pointer and all writes around selector dispatch in `FUN_14072a500`; do not equate a pointer argument with a mutation.
- Ground selector identity and record schema from primary CommonLib/TES5Edit-compatible sources; enumerate official five-master PERK data with a parser whose field decoding and coverage are explicit. Do not call a raw file screen a native xEdit winner or a profile order.
- Retain metadata, stdout/stderr, logs, source identities/hashes, complete-scope markers, and output caps below ignored `.local/`.

## Controls and interpretation

The base visitor formula before selector dispatch is the static comparison. Compare callback input, any write, return value, and the accumulated cache result. A handler that returns without modifying data falsifies H1 only for its scoped target/path; a matching PERK row without a reachable condition does not support vanilla player access.

## Runtime lane

No live action is scheduled. EV-0260 lacks the exact verified Steam target profile/order, disposable save, loaded read-only Observer and live bindings. If later enabled, use a user-controlled clean level-one save and paired positive-hit no-armor/armor controls; record hit validity, damage, raw AVSK 11/12 before/after each repeated hit, and an ordinary unblocked armor-XP positive control. A diagnostic intervention is not vanilla reproduction.
