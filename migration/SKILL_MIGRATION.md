# Codex skill migration map

Codex-discoverable skills live at `.agents/skills/<name>/SKILL.md`. Do not use
Claude-only `paths:` metadata. Scope is stated in each description and body.

| Legacy source | Codex destination | Disposition |
|---|---|---|
| `.claude/skills/skyrim-bsa/` | `.agents/skills/archive-source-discovery/` and `retained-tool-operations/` | Retained Skyrim AE BSA read/search/extract-only workflow; BA2 and archive writes excluded. |
| `.claude/skills/skyrim-save/` | `.agents/skills/save-state-forensics/` | Read-only ReSaver/cosave limits and protected-save protocol preserved. |
| `.claude/skills/inspect-esp/` | `.agents/skills/esp-record-research/` and `retained-tool-operations/` | Read-only xEdit/Spriggit inspection and summary procedures retained. |
| Existing Codex `armor-xp`, `quest-gates`, `experiment-design`, `source-verification`, `cross-domain-synthesis` | Same Codex skills | Retained and used for target research; improve only with source-backed AE details. |
| Existing `edition-variant-audit` | Same path | Rewritten into strict AE executable/profile verification; no cross-edition research workflow. |
| `.claude/skills/create-mod/` | None | Mod-authoring workflow removed from active guidance. |
| `.claude/skills/port-to-vr/` | None | VR workflow is out of scope. |
| `.claude/skills/skyrim-audio/`, `skyrim-mcm/`, `skyrim-nif/` | None | Asset-authoring workflows are out of scope; original history/reference remains recoverable. |
| `.claude/skills/skyrim-context/` | Relevant research facts only | General mod-authoring and non-AE guidance excluded from active instructions. |

Review each skill against its source before removal. The retained-tool skill
contains operational details for xEdit/xelib, AutoMod BSA reads, Spriggit,
ReSaver, cosave, Champollion, Caprica, triage, and DevBench.
