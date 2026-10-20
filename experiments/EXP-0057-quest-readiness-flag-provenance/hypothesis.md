# Competing models

## H1 — Serialized initialization

The GOG TESQuest parser copies QUST `DNAM.General.Flags` bit 0 into `TESQuest+0xDC.0`; the initial field therefore reflects the source `Start Game Enabled` setting.

**Status:** supported for the inspected GOG 1.6.1179.0 parser path [EV-0316].

## H2 — Independent initialization

The parser does not source `+0xDC.0` from serialized QUST flags; constructor or lifecycle state determines the initial bit independently of `Start Game Enabled`.

**Status:** falsified for the inspected GOG load-time path [EV-0316].

## H3 — Later virtual mutation

A later TESQuest virtual operation can change `+0xDC.0` after parsing, so the serialized source predicts only the load-time value and may not predict the field seen by a subsequent callback.

**Status:** a clear operation is supported in code, while its timing and target-quest reachability remain unresolved [EV-0316].
