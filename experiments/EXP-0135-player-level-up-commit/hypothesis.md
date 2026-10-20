# Competing models

## Q86-H1 — level-up acceptance commits the Player Level

Skill experience can cross the next level threshold and produce pending level-up state while the Player Level read by GetLevel stays unchanged until the player accepts the level-up transaction.

**Prediction:** GetLevel reads a stored level field; a separate acceptance/apply-level path increments it. A save captured after threshold but before acceptance preserves the prior level.

## Q86-H2 — the threshold or notification advances GetLevel

The engine changes the Player Level used by GetLevel at the skill-experience threshold or when it opens/notifies the level-up UI, before the player accepts attribute or perk choices.

**Prediction:** GetLevel is computed from accumulated progress or the threshold/notification path writes the level before the acceptance path.

Both are proposed. Existing secondary descriptions are leads only; exact Steam state timing requires a clean transition trace.

## Q87 models after the writer trace

### Q87-H1 — attribute confirmation is the only commit point

The Player base-data level field is not written until the attribute-confirm callback accepts health, magicka, or stamina.

**Prediction:** every Player-provenance field-writer path must pass through that callback; an ordinary StatsMenu update before attribute selection leaves GetLevel unchanged.

**Current assessment:** the captured GOG StatsMenu `kUpdate` path reaches the field writer outside the resolved attribute-confirm callback body [EV-0691]–[EV-0693]. The relationship between the update message and the user's acceptance action remains unobserved, so this is weakened but not fully settled.

### Q87-H2 — due threshold is committed by StatsMenu `kUpdate`

When the Player's progress pair reaches its threshold, StatsMenu `ProcessMessage(kUpdate)` calls the threshold writer, which stores GetLevel+1.

**Prediction:** the identified handler receives `kUpdate`, reads the Player progress pair, and calls the exact base-data setter when the pair is due.

**Current assessment:** supported for this bounded GOG path [EV-0691]–[EV-0693]. Whether the update happens before or after the player's level-up action remains unresolved.

### Q87-H3 — entering/accepting the level-up UI is the commit action

The threshold check occurs on StatsMenu update, but that update is delivered only after the player opens or accepts the level-up interface; the menu transition itself may count as acceptance.

**Prediction:** a natural UI trace shows the field write only after an explicit input/menu state transition, and before attribute selection only if opening that interface is itself the accepted action.

**Current assessment:** proposed; static menu-factory registration identifies `StatsMenu`, not the user input or when the manager sends its update [EV-0693].

### Q87-H4 — a separate registered writer advances the field first

One of the remaining setter paths, including the Player increment wrapper or loop helper, commits level independently of StatsMenu.

**Prediction:** the untyped data references for `FUN_140355210` or `FUN_140356a10` resolve to a scheduler, event callback, or player-visible route that reaches the setter without StatsMenu `kUpdate`.

**Current assessment:** unresolved; direct call censuses and data references are preserved, but registration and dispatch meaning are not classified [EV-0691].

## Q88 assessment — update timing and displacement identity

### Q88-H1 — first ordinary StatsMenu update commits a due level

The threshold writer runs during the first ordinary `kUpdate` after a StatsMenu instance becomes active, before attribute selection.

**Prediction:** a natural, read-only Steam trace shows numeric GetLevel and serialized base-data level incrementing on an ordinary update with no preceding level-up input.

**Current assessment:** open. GOG proves the threshold write is inside the mapped StatsMenu `kUpdate` handler, but not when the UI manager delivers that message [EV-0691]–[EV-0693].

### Q88-H2 — level-up input precedes the due update/write

The StatsMenu threshold branch runs only after an explicit level-up interface transition or acceptance input.

**Prediction:** a clean Steam trace leaves GetLevel unchanged during ordinary updates and the pending state, then changes it after a separately logged UI action.

**Current assessment:** open; neither the StatsMenu `+0x325` state-byte producer nor the natural update/input order is identified [EV-0695].

### Q88-H3 — another registered writer commits first

The data-reference records associated with `FUN_140355210` or `FUN_140356a10` dispatch an independent Player level increment before the StatsMenu path.

**Prediction:** resolve a table consumer or producer-backed caller that reaches the exact setter without StatsMenu `kUpdate`.

**Current assessment:** open. The two bounded pointer records share `FUN_140341290` and have no analyzed table-base xrefs; they remain unresolved metadata candidates [EV-0691].

### Q88-H4 — an offset-only `+0x325` write is the StatsMenu byte producer

A matching displacement candidate writes the same object field that StatsMenu reads.

**Prediction:** receiver identity, an exact vtable entry, or a direct producer/call path connects the writer to the StatsMenu instance.

**Current assessment:** not supported by current evidence. The only analyzed caller of set-true wrapper `FUN_140717c50` is an inventory/soul-capture path; the separate unbounded store has no function owner/xrefs and is absent from the first 64 entries read from the StatsMenu vtable [EV-0695]. These bounded negatives do not prove the store is unrelated, but displacement equality alone is insufficient.
