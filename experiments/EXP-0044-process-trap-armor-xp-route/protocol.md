# Protocol

1. Read EV-0292–EV-0295 and EXP-0039 before collecting further evidence. Keep their raw captures and source identity intact.
2. Query the configured GOG AE 1.6.1179.0 Ghidra project through the strict dispatcher with fresh executable/project identity. Use read-only, no-analysis operations. Do not import or reanalyze a binary and do not transfer GOG RVAs to Steam AE 1.6.1170.0.
3. Follow unresolved indirect calls from the previously captured `FUN_1406b9df0` receiver path, including relevant runtime-initialized callback/vtable targets. Record exact query scope and unresolved edges. Separately trace the armor mitigation dataflow through the common HitData path to the final damage value.
4. Compare the static route with the known AV11/AV12 award branch. Treat absence as bounded to enumerated calls/targets; do not claim a whole-program negative.
5. Keep runtime validation separate. It needs the exact Steam executable identity, complete active plugin order, a clean level-one save, a verified positive unblocked trap hit, functional worn armor, a matched protection control, and raw Light/Heavy Armor AVSK snapshots. No console, script injection, or plugin edits.
6. Preserve raw tool outputs and metadata below ignored `.local/alignment/transactions/TX-20261016-0037/`, add a manifest and evidence note, then update the claim/mechanism/knowledge graph and frontier only to the scope supported by the captures.
