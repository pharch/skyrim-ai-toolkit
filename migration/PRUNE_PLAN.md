# Generated pruning plan

Regenerate after upstream updates. No files have been deleted by this script.

Inventory: 98 tracked files; 10 retire candidates; 13 manual-review candidates; 75 initially retained.

## Remove after snapshots + Codex port

- `.claude/hooks/backup-before-edit.sh`
- `.claude/hooks/protect-bash.sh`
- `.claude/hooks/protect-files.sh`
- `.claude/hooks/session-kb-guard.sh`
- `.claude/hooks/snapshot-before-tool.sh`
- `.claude/settings.json`
- `.claude/settings.local.json.example`
- `CLAUDE.md`
- `SETUP_PROMPT.txt`
- `setup.sh`

### Exact Git removal commands (review each command first)

```bash
git rm -- .claude/hooks/backup-before-edit.sh
git rm -- .claude/hooks/protect-bash.sh
git rm -- .claude/hooks/protect-files.sh
git rm -- .claude/hooks/session-kb-guard.sh
git rm -- .claude/hooks/snapshot-before-tool.sh
git rm -- .claude/settings.json
git rm -- .claude/settings.local.json.example
git rm -- CLAUDE.md
git rm -- SETUP_PROMPT.txt
git rm -- setup.sh
```

## Manual audit before asset pruning

- `.claude/skills/create-mod/SKILL.md` — CLAUDE-SPECIFIC: migrate useful skill first
- `.claude/skills/inspect-esp/SKILL.md` — CLAUDE-SPECIFIC: migrate useful skill first
- `.claude/skills/port-to-vr/SKILL.md` — CLAUDE-SPECIFIC: migrate useful skill first
- `.claude/skills/skyrim-audio/SKILL.md` — ASSET-SKILL: preserve unique engine/protocol facts first
- `.claude/skills/skyrim-bsa/SKILL.md` — CLAUDE-SPECIFIC: migrate useful skill first
- `.claude/skills/skyrim-context/SKILL.md` — CLAUDE-SPECIFIC: migrate useful skill first
- `.claude/skills/skyrim-mcm/SKILL.md` — ASSET-SKILL: preserve unique engine/protocol facts first
- `.claude/skills/skyrim-nif/SKILL.md` — ASSET-SKILL: preserve unique engine/protocol facts first
- `.claude/skills/skyrim-save/SKILL.md` — CLAUDE-SPECIFIC: migrate useful skill first
- `.claude/skyrim-paths.env.example` — CLAUDE-SPECIFIC: migrate useful skill first
- `tools/blender-nif-render.py` — ASSET-PATH: inspect consumers and references; do not auto-delete
- `tools/blender-nif-validate.py` — ASSET-PATH: inspect consumers and references; do not auto-delete
- `tools/pyffi-geometry-split.py` — ASSET-PATH: inspect consumers and references; do not auto-delete

## Retain by default

- `.config/dotnet-tools.json`
- `.devcontainer/Dockerfile`
- `.devcontainer/devcontainer.json`
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.gitignore`
- `.node-version`
- `.python-version`
- `AGENTS.md`
- `CHANGELOG.md`
- `KNOWLEDGEBASE.md`
- `LICENSE`
- `README.md`
- `devshell-docker.sh`
- `devshell.sh`
- `docs/REVIEW-SCOPE.md`
- `docs/container-vs-windows.md`
- `docs/getting-started.md`
- `docs/safety-philosophy.md`
- `docs/skse-cross-compile.md`
- `docs/xelib-guide.md`
- `examples/create-esp.js`
- `examples/diff-esp.js`
- `examples/inspect-esp.js`
- `examples/inspect-esp.py`
- `package.json`
- `requirements-windows.txt`
- `requirements.txt`
- `scripts/build-nexus-pack.sh`
- `scripts/generate-baseline.sh`
- `scripts/read-save.py`
- `scripts/restore-from-backup.sh`
- `tests/bin/which`
- `tests/conftest.py`
- `tests/mock_devbench.py`
- `tests/test_cosave.py`
- `tests/test_devbench_cli.py`
- `tests/test_hook_canary.py`
- `tests/test_hooks.py`
- `tests/test_jq_path.py`
- `tests/test_kb_guard.py`
- `tests/test_mutations.py`
- `tests/test_nexus_pack.py`
- `tests/test_repo_invariants.py`
- `tests/test_setup_paths.py`
- `tests/test_skyrim_paths.py`
- `tests/test_triage.py`
- `tools/automod-cli.sh`
- `tools/cosave-cli.sh`
- `tools/cosave-info.py`
- `tools/crash-triage.py`
- `tools/devbench-cli.sh`
- `tools/esp-verify-wrapper.sh`
- `tools/hook-canary.sh`
- `tools/kb-guard.sh`
- `tools/nexus.sh`
- `tools/papyrus-triage.py`
- `tools/resaver-cli.sh`
- `tools/resaver-cli/ResaverCLI.java`
- `tools/resaver-cli/analysis-overlay/NOTICE.md`
- `tools/resaver-cli/analysis-overlay/resaver/ess/ChangeFormExtraDataData.java`
- `tools/resaver-cli/analysis-overlay/resaver/ess/ChangeFormQust.java`
- `tools/resaver-cli/analysis-overlay/resaver/ess/ChangeFormRefr.java`
- `tools/resaver-resolve-names.js`
- `tools/skyrim-winner.js`
- `tools/skyrim-winner.sh`
- `tools/skyrim-winner.test.js`
- `tools/skyrim_paths.py`
- `tools/spriggit-cli.sh`
- `tools/toolchain-check.sh`
- `tools/verify-release.sh`
- `tools/xelib/active-plugins.js`
- `tools/xelib/active-plugins.test.js`
- `tools/xelib/loader_diag.js`
