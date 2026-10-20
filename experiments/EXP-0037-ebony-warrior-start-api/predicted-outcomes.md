# EXP-0037 predicted outcomes

| Model | Predicted observation | Discriminant |
|---|---|---|
| H1: ordinary wrappers enforce event scope | `Quest.Start` and `Quest.SetStage` wrapper paths reject nondefault event IDs before `EnsureQuestStarted`; the CLOC QUST has a nondefault serialized event type. | Decompile the GOG wrappers and verify branch edges, log strings, helper calls, build identity, and QUST ENAM. |
| H2: direct ordinary path bypasses event selection | A wrapper schedules startup anyway, or an official QUST/DIAL/INFO record references the target outside its own selected event path. | Query exact wrapper edges and scan all records in those three signatures across the five official master files. |

These static discriminants can narrow ordinary API behavior. They cannot prove a Steam runtime result, alias fill, level-one start, or absence of calls in unscanned signatures, archives, profile plugins, or dynamic native dispatch.
