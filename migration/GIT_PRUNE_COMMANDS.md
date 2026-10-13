# Safe, repo-aware Git pruning

The upstream repository can change; this kit was prepared from upstream root docs and public file references but a **complete recursive file tree could not be downloaded** here. Never run blind, broad `git rm -rf` commands. `scripts/prune_preview.py` uses *your actual fork's* `git ls-files` to generate the exact current paths for removal/review.

## Baseline

```bash
git status --short
git switch -c research/codex-harness-v2
python scripts/upstream_snapshot.py
python scripts/prune_preview.py
cat migration/PRUNE_PLAN.md
```

## Concrete removals after snapshots and migration review

Run these commands *only if paths exist and `references/upstream/SNAPSHOT_MANIFEST.json` proves source preservation*. Git removal is reversible from your parent branch.

```bash
# 1. Remove Claude-only hook executable layer; these do not protect Codex.
git ls-files '.claude/hooks/**'            # preview
git rm -r --ignore-unmatch -- .claude/hooks

# 2. Retire Claude runtime configuration after inspecting the tree.
git rm --ignore-unmatch -- .claude/settings.json .claude/settings.local.json.example

# 3. Retire old top-level Claude instruction/setup files *after* preserving
#    the original text and adapting any paths used by tools.
git rm --ignore-unmatch -- CLAUDE.md SETUP_PROMPT.txt
# Do not yet delete setup.sh: it is a valuable reference for MO2/game path
# detection, even though it must NOT be executed in the fork.

# 4. After confirming no scripts depend on setup.sh, retire it:
# git rm --ignore-unmatch -- setup.sh

# 5. Conditionally retire particular asset-only skills after listing them.
git ls-files '.claude/skills/**' | sort
# Examples (ONLY if present, and after transferring unique engine facts):
# git rm -r --ignore-unmatch -- .claude/skills/skyrim-nif
# git rm -r --ignore-unmatch -- .claude/skills/skyrim-audio

# 6. Evaluate examples/doc/tests for mesh, texture, audio, animation, VR,
#    NIF, render, FOMOD, MCM. Do not delete their shared libraries blindly.
python scripts/prune_preview.py

# 7. See exactly what will be committed.
git diff --cached --name-status
git diff --cached --stat
```

## Exact reviewed asset file removals

After reviewing the `Manual audit` section of `migration/PRUNE_PLAN.md`, create `migration/PRUNE_APPROVED.txt` with **one exact tracked file path per line** (no directory globs or substitutions). This handles all files selected for asset-only deletion, without guessing their upstream names:

```bash
python scripts/prune_approved.py              # print exact git rm commands only
python scripts/prune_approved.py --apply      # run reviewed commands, not on main/master
git diff --cached --name-status
```

Do not add a directory merely because its name contains 'VR'; record-level or save-analysis scripts can contain VR-specific notes yet remain vital. Preserve knowledge and test fixtures before deletion.

## Do NOT remove during preliminary prune

`tools/xelib`, `tools/skyrim-winner.*`, `tools/resaver*`, `tools/cosave-*`, `tools/devbench-cli.sh`, `tools/papyrus-triage.py`, `tools/crash-triage.py`, `tools/skyrim_paths.py`, `docs/xelib-guide.md`, `KNOWLEDGEBASE.md`, `package.json`, requirements files, test suites exercising retained scripts, license notices, MO2/load-order detection. Retain relevant examples, BSA extraction and plugin record tooling, even if some tools also have unrelated modding capabilities.

## Cleanup discipline

For every path removed, log whether it is asset-only, replaced by a Codex skill, archived, or redundant. Keep original commit history. Ensure the copied `references/upstream/` includes the original upstream instructions, license is still present, and no retained script points silently into removed code.
