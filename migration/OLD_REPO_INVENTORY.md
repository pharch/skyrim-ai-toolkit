# Established source inventory

This is the redacted inventory of the user-specified legacy `skyrim` checkout.
The source tree was read-only. Its `.git` directory had no `HEAD`, config, or
index, so its commit, branch, initial status, and submodule state are unknown.

## Tree walk

The 2026-10-14 read-only walk counted 15,599 regular files after excluding VCS
internals, common language caches, virtual environments, and `node_modules`.
There were no symlinks. The old source's own `migration/INVENTORY.md` gives
different approximate totals from an earlier 2026-09-23 pass; those historical
estimates are not substituted for this walk.

| Area | Files in current walk | Notes |
|---|---:|---|
| `tmp/` | 14,335 | Includes 14,308 `.psc` files; source/version is not independently established. |
| `out/` | 731 | Generated reports, logs, exports, runtime notes, and analysis data; raw artifacts were not bulk-copied. |
| `legacy/` | 205 | Root and diagnostic backups; relevant Markdown files have per-file dispositions and linked knowledge records. |
| `scripts/` | 52 | Python, PowerShell, Java, and helper scripts; tool status is in `TOOL_AUDIT.md`. |
| `observer/` | 42 | Observer source, tests, docs, and build outputs; no current DLL build was established. |
| `data/` | 55 | Includes Ghidra/game-data material; project compatibility remains unverified. |
| `experiments/` | 33 | Thirty-two experiment Markdown source files plus one non-Markdown entry. |
| `.ghidra-user/` | 50 | Hidden local Ghidra state; treated as environment-specific, not canonical research. |
| `config/` | 3 | Local machine configuration; values are kept out of this tracked checkout. |

The largest extension groups were `.psc` (14,308), `.log` (662), `.md` (243),
`.txt` (71), `.class` (39), `.json` (39), `.py` (34), `.csv` (27), and `.java`
(16). This is a path inventory, not a semantic review of every generated or
binary file.

## Markdown/MDX disposition

A complete Markdown/MDX walk found 243 files. The 242 relevant first-party or
research-corpus candidates have per-file SHA-256 and byte counts in
[`legacy_markdown_manifest.tsv`](legacy_markdown_manifest.tsv); the canonical
manifest-file SHA-256 is recorded in
[`LEGACY_SOURCE_SNAPSHOT.json`](LEGACY_SOURCE_SNAPSHOT.json). One generated
third-party vcpkg issue-body document under `observer/build/` is deliberately
excluded and recorded with its hash in
[`legacy_source_exclusions.tsv`](legacy_source_exclusions.tsv).

The disposition for each manifested path is in
[`legacy_disposition.tsv`](legacy_disposition.tsv). The grouped source map is
[`LEGACY_SOURCE_INDEX.md`](LEGACY_SOURCE_INDEX.md); the full source-to-active
destination crosswalk is linked by
[`OLD_REPO_SOURCE_MAP.md`](OLD_REPO_SOURCE_MAP.md).

## Protected and generated material

- Private Discord export material and its per-message content/identifiers were
  not copied into tracked files. The ignored local index is covered by the
  privacy tests; the source summary remains untrusted research input.
- Machine-specific paths are stored only in ignored local configuration; the
  tracked template contains placeholders. No credentials or private path
  values are included in this inventory.
- The source tree's raw Ghidra project, game archives, decompiled source,
  runtime logs, saves, and generated outputs remain at their original paths.
  They are not treated as current AE evidence merely because files exist.
- The original source checkout was not written by this migration. Final source
  manifest comparison found no missing or changed manifested files.

## Canonical detailed inventories

- Content and per-file disposition: [`OLD_REPO_SOURCE_MAP.md`](OLD_REPO_SOURCE_MAP.md)
- Relevant source code/probe dispositions and hashes: [`legacy_artifact_disposition.tsv`](legacy_artifact_disposition.tsv)
- Tool paths and validation: [`TOOL_PATH_VERIFICATION.md`](TOOL_PATH_VERIFICATION.md)
- Tool compatibility: [`TOOL_COMPATIBILITY_MATRIX.md`](TOOL_COMPATIBILITY_MATRIX.md)
- Knowledge import decisions: [`KNOWLEDGE_IMPORT_AUDIT.md`](KNOWLEDGE_IMPORT_AUDIT.md)
