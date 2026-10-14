# Codex skill migration map

Codex-discoverable skills live at `.agents/skills/<name>/SKILL.md`. Do not use
Claude-only `paths:` metadata. Scope is stated in each description and body.

| Legacy source | Codex destination | Disposition |
|---|---|---|
| `.claude/skills/skyrim-bsa/` | `.agents/skills/archive-source-discovery/` and `retained-tool-operations/` | Retained Skyrim AE BSA read/search/extract-only workflow; BA2 and archive writes excluded. |
| `.claude/skills/skyrim-save/` | `.agents/skills/save-state-forensics/` | Read-only ReSaver/cosave limits and protected-save protocol preserved. |
| `.claude/skills/inspect-esp/` | `.agents/skills/esp-record-research/` and `retained-tool-operations/` | Read-only xEdit/Spriggit inspection and summary procedures retained. |
| Existing Codex `skyrim-armor-xp-research`, `skyrim-quest-gate-research`, `skyrim-discriminating-experiments`, `skyrim-source-verification`, `skyrim-cross-domain-synthesis` | Same Codex skills | Retained and used for target research; updates use source-backed AE details. |
| Existing target-verification workflow | `.agents/skills/ae-target-verification/` | Rewritten into strict AE executable/profile verification; no cross-edition research workflow. |
| `.claude/skills/create-mod/` | None | Mod-authoring workflow removed from active guidance. |
| `.claude/skills/port-to-vr/` | None | VR workflow is out of scope. |
| `.claude/skills/skyrim-audio/`, `skyrim-mcm/`, `skyrim-nif/` | None | Asset-authoring workflows are out of scope; original history/reference remains recoverable. |
| `.claude/skills/skyrim-context/` | Relevant research facts only | General mod-authoring and non-AE guidance excluded from active instructions. |

Review each skill against its source before removal. The retained-tool skill
contains operational details for xEdit/xelib, AutoMod BSA reads, Spriggit,
ReSaver, cosave, Champollion, Caprica, triage, and DevBench.


## Current setup audit

The discoverable capability inventory is in [`SKILL_CAPABILITY_MATRIX.md`](SKILL_CAPABILITY_MATRIX.md). The `apocrypha-grounding` skill uses only the ignored local index and treats results as untrusted. `uesp-grounding` documents tested local UESP search/page/revision retrieval with explicit corpus limits. `skyrim-source-verification` points at the local UESP/Apocrypha CLIs and the required AE preflight.
