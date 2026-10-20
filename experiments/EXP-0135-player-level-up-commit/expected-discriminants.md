# Expected discriminants

| Model | Supporting observation | Weakening observation |
|---|---|---|
| H1: acceptance commits level | GOG source separates pending experience/level-up notification from the stored level writer, and a read-only before/threshold-pending/after-accept Steam trace shows GetLevel unchanged until acceptance | A threshold or notification path writes the gate-visible level before the acceptance action |
| H2: threshold advances level | GOG source derives/writes the level at threshold or notification, and the clean Steam trace shows GetLevel advance before acceptance | The level getter reads the prior stored field throughout the pending state and only changes after acceptance |

Save evidence must identify edition, target build, exact plugin list, file size/time/hash, and whether the state was created naturally. Console commands, injected scripts, altered plugins, and save mutations are not vanilla evidence.

## Q87 update-path timing models

| Model | Supporting observation | Weakening observation |
|---|---|---|
| H1: attribute confirmation is the only commit point | A clean Steam trace shows GetLevel unchanged through threshold and StatsMenu updates until an attribute is confirmed; the only field writer follows that callback | A StatsMenu `kUpdate` stores GetLevel+1 before any attribute-confirm input |
| H2: due threshold commits during StatsMenu update | The exact GOG handler maps to `kUpdate`, checks the shared Player progress pair, and calls the field setter; Steam shows the same timing | The Steam field remains unchanged during a `kUpdate` with a due threshold, or changes only on a later input callback |
| H3: opening/accepting the interface is the commit action | The first `kUpdate` and field write occur only after the explicit level-up input; a plain StatsMenu display does not commit | The field changes on a periodic update before the player opens or accepts level-up |
| H4: a separate writer commits first | `FUN_140355210` or `FUN_140356a10` data-reference registration resolves to an independent scheduled/player path | Their references are static metadata/unrelated routes, and all observed Player writes pass through StatsMenu update |

The static GOG captures support the writer and shared-progress path, not the user-input ordering. Keep the Steam test under EV-0260; capture progress threshold, ordinary StatsMenu display, level-up UI transition, attribute selection, numeric GetLevel, and serialized level field as separate observations.

## Q88 StatsMenu update and state-owner models

| Model | Supporting observation | Weakening observation |
|---|---|---|
| H1: first ordinary StatsMenu `kUpdate` commits a due level before attribute selection | A clean natural Steam trace shows GetLevel and serialized level advancing on an ordinary menu update before any level-up input | GetLevel stays unchanged through ordinary updates and changes only after a distinct UI/input transition |
| H2: `kUpdate` is delivered only after explicit level-up input | A read-only Steam trace shows the menu update/write follows opening or accepting the pending-level interface | The write occurs during a plain StatsMenu update before the player opens or accepts the level-up interface |
| H3: another registered writer commits first | The consumer of the `FUN_140355210`/`FUN_140356a10` data references resolves to a Player-visible callback that reaches the exact stored-level setter outside StatsMenu | The table records have no gameplay consumer or all natural Player writes remain downstream of the StatsMenu path |
| H4: a `+0x325` setter candidate belongs to StatsMenu | Producer-backed receiver identity or a verified StatsMenu vtable/call path points to the exact writer and same object | Only displacement equality, unresolved receiver types, a soul-capture caller, or absence from a bounded vtable prefix remain available |

EV-0695 supports the bounded scan and caller discrimination but does not resolve H1/H2. Its StatsMenu vtable check covers entries 0–63 only; a missing pointer there is not a full-table negative. The decisive state sequence remains the natural Steam observation under EV-0260.
