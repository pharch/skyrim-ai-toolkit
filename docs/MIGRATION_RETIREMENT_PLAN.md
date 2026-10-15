# Migration retirement plan

This is a review plan only. No migration file was deleted or staged. The user-provided mission requires preserving tracked history during this setup session and prohibits pruning without approval of the exact paths.

## Inventory

`migration/FINAL_RETIREMENT_MANIFEST.tsv` classifies all 117 current files under `migration/`: 112 tracked and 5 untracked. Class totals: 38 ACTIVE_DEPENDENCY, 63 PROVENANCE, 15 HISTORICAL_ONLY, 1 DO_NOT_TOUCH.

Recreate the tracked-file preview with `git ls-files migration/`. The candidate list contains 13 exact tracked paths classified HISTORICAL_ONLY; it excludes user input, active dependencies, provenance, and untracked files. Review every row and migrate required facts before any future deletion.

## Classification rules

- `ACTIVE_DEPENDENCY`: a current doc, skill, script, or test refers to the path. Remove or migrate the dependency before retirement.
- `PROVENANCE`: source maps, evidence aliases, experiment records, or hashes needed to interpret retained research. Preserve concise canonical provenance first.
- `HISTORICAL_ONLY`: superseded setup reports and one-off notes with no current exact-path reference. Eligible for later review, never auto-delete.
- `DO_NOT_TOUCH`: user-provided or untracked files, or material requiring explicit review.

## Exact non-executed retirement command

Only after the user reviews and approves the contents of `migration/PROPOSED_RETIREMENT_PATHS.txt`, the exact command would be:

```bash
git rm --pathspec-from-file=migration/PROPOSED_RETIREMENT_PATHS.txt
```

This command was not run. The candidate list has no wildcards, parent traversal, untracked entries, or project-root paths. Before any future execution, compare it with `git ls-files migration/`, review staged name-status, run validation, and preserve the path list outside `migration/` if that directory is being pruned.
