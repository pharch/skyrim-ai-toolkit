# Migration source map

## Provenance boundary

The repository Git history remains the rollback source. The tracked
`references/upstream/` directory preserves legacy root guidance and a snapshot
manifest. `KNOWLEDGEBASE.md` is retained untouched as a legacy third-party
reference; it is not active Codex guidance. Do not promote its VR, non-AE, or
mod-authoring instructions into the current workflow.

## Active Codex surfaces

| Purpose | Active destination | Source / disposition |
|---|---|---|
| Stable agent rules | `AGENTS.md` | Rewritten as AE-only research instructions; legacy copy remains under `references/upstream/`. |
| Research state | `STATE.md`, `NORTH_STAR.md`, `ROADMAP.md` | Replaced template state; mission strategy remains separate from operational checkpoint. |
| Research-specific workflows | `.agents/skills/*/SKILL.md` | Migrated content from existing research skills; frontmatter follows Codex skill layout. |
| Tool operation knowledge | `.agents/skills/retained-tool-operations/SKILL.md`, `protocols/TOOL_ROUTING.md` | Concrete commands and caveats adapted from legacy tool docs and wrappers. |
| Live test constraints | `protocols/LIVE_GAME.md` | Rewritten for AE-only, explicit lanes, and observational-only autonomous access. |
| Evidence records | `research/EVIDENCE.json`, `research/EVIDENCE_MODEL.md` | New versioned evidence model; no unsupported historical findings imported. |
| Legacy experiment records EXP-0001–0005 and EXP-0007 | `migration/legacy_experiments/` | Archived with a data-only notice, per-file source manifest hashes, and result evidence IDs. No EXP-0006 Markdown record exists in the source manifest; active pilot questions are EXP-0008–0010. |
| Setup | `scripts/setup_research.py`, `docs/getting-started.md` | Replaces game-root setup with local checkout initialization and offline checks. |

Archived-only assets include the old `.claude/` directory, Claude settings,
old setup scripts, and third-party notes. Any deletion is subject to the
finalization checklist and must remain recoverable in Git.


## Current local snapshot import

See [`LEGACY_SOURCE_INDEX.md`](LEGACY_SOURCE_INDEX.md) for the content-to-destination map and exclusions. The 242-path manifest and per-file hashes are recorded under `migration/`. Imported research uses `research/EVIDENCE.json` IDs whose source revision/runtime remain explicitly unknown.

The complete Markdown/MDX path/hash/disposition ledger is [`legacy_disposition.tsv`](legacy_disposition.tsv). All 242 candidate Markdown/MDX paths now have a final disposition; none remain pending. Relevant scripts, Ghidra helpers, and Observer source also have per-file hashes and dispositions in [`legacy_artifact_disposition.tsv`](legacy_artifact_disposition.tsv). See [`LEGACY_SOURCE_INDEX.md`](LEGACY_SOURCE_INDEX.md) for reconciled counts and [`KNOWLEDGE_IMPORT_AUDIT.md`](KNOWLEDGE_IMPORT_AUDIT.md) for claim-level boundaries.
