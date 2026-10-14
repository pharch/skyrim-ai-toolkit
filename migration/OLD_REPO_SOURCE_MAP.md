# Established source map

This file points to the single canonical source map and per-file disposition
ledger. It avoids maintaining a second copy of the 242-path mapping.

- [`LEGACY_SOURCE_INDEX.md`](LEGACY_SOURCE_INDEX.md) groups content by canonical
  destination and explains the provenance and epistemic boundary.
- [`legacy_disposition.tsv`](legacy_disposition.tsv) assigns each manifested
  Markdown/MDX path a disposition, review state, destination, and rationale.
- [`legacy_evidence_ids.json`](legacy_evidence_ids.json) maps imported source
  paths to stable `EV-` IDs in `research/EVIDENCE.json`.
- [`legacy_markdown_manifest.tsv`](legacy_markdown_manifest.tsv) records each
  candidate source path, SHA-256, and byte count.
- [`legacy_source_exclusions.tsv`](legacy_source_exclusions.tsv) records the
  generated vcpkg Markdown file excluded from the candidate manifest.
- [`legacy_artifact_disposition.tsv`](legacy_artifact_disposition.tsv) records
  SHA-256, treatment, destination, and test/runtime boundary for each relevant
  source script, Ghidra helper, and Observer implementation file discovered in
  the legacy `scripts/`, `observer/`, `data/`, and `experiments/` trees.

The old source `.git` metadata was empty. Provenance therefore uses snapshot
ID `LEGACY-20261014-A`, relative source paths, and content hashes rather than a
fabricated commit.
