# Protocol

1. Verify the configured GOG executable identity, then query `FUN_14048a5b0` with bounded incoming direct callers in the existing Ghidra project using read-only/no-analysis mode.
2. Trace the nonzero setter argument backward through the exact call site and parameter accessor; preserve the field index and byte/bit operations without inventing a field name.
3. Query the direct caller and the process-level helper; distinguish direct xrefs, data references, and possible indirect dispatch.
4. Interpret `AIProcess+0x137` only against the pinned CommonLib header recorded with EV-0287. Do not transfer addresses to Steam.
5. Leave the action dispatch owner, parameter schema, natural occurrence, Steam behavior, protection, and XP open unless directly measured or independently mapped.
