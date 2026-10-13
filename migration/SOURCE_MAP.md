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
| Setup | `scripts/setup_research.py`, `docs/getting-started.md` | Replaces game-root setup with local checkout initialization and offline checks. |

Archived-only assets include the old `.claude/` directory, Claude settings,
old setup scripts, and third-party notes. Any deletion is subject to the
finalization checklist and must remain recoverable in Git.
