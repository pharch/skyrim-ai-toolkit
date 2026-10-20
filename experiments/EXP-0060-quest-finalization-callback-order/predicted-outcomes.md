# Predicted outcomes

| Observation | H1: finalization first | H2: callback may precede finalization |
|---|---|---|
| Per-file records vs slot-19 sweep | Per-file record work completes before `FUN_1401bdf20` | A callback path is reached during/before the sweep |
| Loader to SetStage relation | No pre-return natural callback chain; callback follows loader completion | Concrete event/callback dispatch reaches registered `FUN_14034de90` before the sweep returns |
| Generic indirect calls | Must be class-resolved or left inconclusive | Must be bound to the SetStage row and a natural event source |
| Runtime observer | First natural callback follows finalization telemetry | Callback timestamp precedes finalization telemetry |

Missing direct xrefs alone do not support H1 because callback-table invocation may be indirect.
