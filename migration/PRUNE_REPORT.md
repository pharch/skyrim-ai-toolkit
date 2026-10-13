# Active-surface prune report

The current pass converts the active onboarding, research instructions,
tool-routing protocol, and AE path/load-order logic. Historical source material
remains available through Git and archived references.

## Remove from active use

- Claude-only `.claude/` settings and hooks.
- Root `CLAUDE.md`, `SETUP_PROMPT.txt`, and game-install `setup.sh`.
- VR and cross-edition workflows.
- Mod creation, plugin writing, asset authoring, and unrelated examples.
- Game-mounting devcontainer and cross-compile documentation if no retained
  research tool depends on them.
- Claude setup prompts, hook-specific tests, and release packaging that assumes
  extraction into Skyrim.

## Preserve

- Research skills and fixture tests.
- xEdit/xelib, winner, ReSaver, cosave, log triage, BSA read/extract, and
  inspection tools.
- `KNOWLEDGEBASE.md`, upstream snapshots, licenses, and Git history as archival
  provenance; do not treat archival content as current instructions.
- Raw evidence, negative results, and private paths outside the repository.

This report is an implementation record, not proof that every item is already
removed. Reconcile it with `git ls-files` and the missing authoritative
finalization brief before declaring the prune complete.
