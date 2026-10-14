# Active language audit

Audited 2026-10-14. The scan covered repository `.md`/`.mdx` files, including
hidden skills and untracked Markdown, for the legacy terms and workflows named
in `session-brief/LOCAL_CODEX_FINAL_AUDIT_PROMPT.md`: Claude runtime, mod
authoring/installation, release/porting, alternate editions, VR-specific terms,
asset authoring, pre-AE runtime hints, and writing into the game directory.
Generated caches and private `.local/` corpora were excluded. The scan found
627 matching lines in 24 files; matches were then classified by actual purpose,
not treated as instructions merely because a word matched.

## Operative-surface findings

| Path and line | Context | Disposition |
|---|---|---|
| `docs/xelib-guide.md:41` | “Release every record/element handle after use.” | Keep. “Release” means releasing an xEditLib resource handle, not publishing content. |
| `migration/LOCAL_SETUP_BASELINE.md:10` | `/etc/os-release` in captured OS metadata. | Keep. This is the Linux OS metadata file name, not a product release workflow. |
| `migration/LOCAL_SETUP_CHECKLIST.md:17` | A03 names the excluded Claude-runtime/content-authoring workflow as an audit criterion. | Keep. It is a negative acceptance test, not an instruction to use that workflow. |
| `tools/resaver-cli/analysis-overlay/NOTICE.md:6,27` | Upstream “MODIFICATION NOTICE”, project attribution, and a ReSaver release/API reference. | Keep as required third-party attribution and technical provenance; it is not an active authoring workflow. |
| `research/SESSION_LOG.md:20,213` | Historical checkpoint describes removing legacy instructions. | Keep as migration history; it does not direct current work. |
| `session-brief/LOCAL_CODEX_FINAL_AUDIT_PROMPT.md:97,99,243` | The audit prompt names forbidden legacy vocabularies and the A03 criterion. | Keep as the explicit audit specification; it is not a Skyrim workflow. |

No active root policy, skill, research protocol, or user-facing setup guide
offers alternate-edition support, asset authoring, a Claude runtime, or a
content-production workflow. The only `release` hit in active operating
documentation is the xEditLib handle instruction above.

## Historical and archival matches

The following files contain retained historical material or imported third-
party text. They are not operative policy; root `AGENTS.md` identifies
`KNOWLEDGEBASE.md` and `references/upstream/` as archival, while migration
reports label prior prompts/checklists as superseded or historical. Counts are
matching lines from the same scan; excerpts are not duplicated here because the
source files remain available and may contain personal or community-derived
material.

| Path | Matching lines | Classification |
|---|---:|---|
| `CHANGELOG.md` | 80 | Historical release notes, old Claude/VR workflows, and past toolkit features. |
| `KNOWLEDGEBASE.md` | 89 | Retained legacy knowledge source; not active instructions. |
| `references/upstream/AGENTS.md` | 11 | Immutable upstream agent instructions retained as source data. |
| `references/upstream/CLAUDE.md` | 45 | Upstream historical instructions, not discoverable as active skills. |
| `references/upstream/KNOWLEDGEBASE.md` | 89 | Upstream archival knowledge source. |
| `references/upstream/README.md` | 90 | Upstream project description and legacy usage. |
| `references/upstream/.claude/backups/kb/20261013_074133/CLAUDE.md` | 45 | Dated upstream backup. |
| `references/upstream/.claude/backups/kb/20261013_074133/KNOWLEDGEBASE.md` | 89 | Dated upstream backup. |
| `references/upstream/.claude/skills/port-to-vr/SKILL.md` | 9 | Archived upstream skill; excluded from `.agents/skills` discovery. |
| `references/upstream/.claude/skills/skyrim-audio/SKILL.md` | 8 | Archived upstream skill; excluded from `.agents/skills` discovery. |
| `references/upstream/.claude/skills/skyrim-context/SKILL.md` | 6 | Archived upstream skill; excluded from `.agents/skills` discovery. |
| `references/upstream/.claude/skills/skyrim-nif/SKILL.md` | 9 | Archived upstream skill; excluded from `.agents/skills` discovery. |
| `migration/FINAL_SETUP_BRIEF.md` | 24 | Superseded migration prompt; its authority notice points to the current prompt/checklist. |
| `migration/LEGACY_FINALIZATION_CHECKLIST_82.md` | 5 | Historical checklist; not the current 86-item source of truth. |
| `migration/PORTING_CHECKLIST.md` | 5 | Historical migration checklist. |
| `migration/PRUNE_REPORT.md` | 4 | Historical report of removed legacy surfaces. |
| `migration/SKILL_MIGRATION.md` | 8 | Historical migration map. |
| `migration/SOURCE_MAP.md` | 1 | Historical source map. |

The scan also found no additional matches in active skill frontmatter. Legacy
terms in raw imported documents, legal notices, test fixtures, or source
provenance are retained only where the research or attribution record requires
them; they do not establish support for those workflows.
