# Predicted outcomes

| Observation | H1: null HitData handle on captured route | H2: helper writes a handle |
|---|---|---|
| Initializer writes `+0x18/+0x1C` | Zeroes both | May be overwritten later |
| Builder and helper writes to `+0x18` | None | At least one write/nonzero flow |
| Handler's HitData-derived handle | Zero/null | Nonzero/resolvable |
| First conditional cleanup | Skipped on this route | Can execute on this route |
| Receiver cleanup | Independent receiver handle | Independent receiver handle |

Neither outcome by itself resolves whether the receiver teardown's unresolved virtual descendants can award armor skill progress.
