# Expected discriminants

1. Preserve exact GOG identity and read-only/no-analysis metadata for each native query.
2. Identify both direct callers of `FUN_1401bdf20`, their per-file record loops, and operations after the finalization call.
3. Classify the second caller of `FUN_1401be290` far enough to distinguish the file-load wrapper from a quest callback source.
4. Bind a callback target to the registered `Quest.SetStage` row; do not use method-name proximity or an untyped indirect site as proof.
5. Keep data-table references distinct from direct code call xrefs. Preserve incomplete or missing caller provenance.
6. A runtime ordering claim requires an exact Steam AE 1.6.1170.0 target, complete active order, clean level-one start, and read-only timestamps/state for file-load completion and the first natural SetStage callback.
