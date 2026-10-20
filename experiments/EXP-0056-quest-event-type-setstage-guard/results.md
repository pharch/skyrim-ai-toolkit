# Results

EV-0314 resolves the inspected GOG/source field-map component. The GOG TESQuest constructor candidate `FUN_1403c6ff0` initializes `+0xE0` to `0xFFFFFFFF` and installs the TESQuest vtable. Its bounded slot-6 mapping points to QUST parser candidate `FUN_1403c7a50`; that parser's `ENAM` case reads four bytes to object `+0xE0`, while its separate `DATA` case writes only through `+0xDF` [EV-0314].

Direct-parser source records show `ENAM` bytes `4c45564c` (`LEVL`) for DA02 `0004D8D6`, DA09 `0004E4E1`, and DA06 `0003B681` [EV-0314], [EV-0310], [EV-0306], [EV-0308]. These are source-file records, not active-order winners.

EV-0313's distinct registered GOG SetStage callback reads the same `+0xE0` field and its initial predicate is `(quest+0xDC bit 0 set) OR (quest+0xE0 == -1)`. Consequently, a nondefault LEVL value with bit 0 clear fails that entry guard before `EnsureQuestStarted`; a set bit can satisfy the initial guard but does not prove later initialization, stage application, running state, aliases, journal/dialogue, or useful access [EV-0313], [EV-0314].

This is a GOG 1.6.1179.0 static mechanism inference combined with direct source parsing. No Steam 1.6.1170.0 field map or runtime snapshot, natural callback, stage transition, alias fill, running-state change, functional access, or level-one reproduction was captured.

No level-one callback, stage transition, alias fill, running state, or functional access is claimed.
