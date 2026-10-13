# Skyrim Exploit Research Harness — Codex Overlay (Preliminary)

An **offline-first, source-grounded** research layer for a fork of [ia-kobos/skyrim-ai-toolkit](https://github.com/ia-kobos/skyrim-ai-toolkit). This overlay converts the core operating model from Claude-driven mod creation to long-horizon Codex research into Skyrim's exploitable engine behavior. Its primary targets are **level-one access to level-gated quests/events** and **wearing armor without armor skill XP from incoming hits**; enchanting XP and permanent alchemical effects remain secondary targets.

**Status: preliminary port, not a verified live-game installation.** The overlay was authored against publicly accessible upstream docs, not a full local clone or execution of the upstream suite. The original repo must be cloned, inventoried and tested on your machine. The user chooses all game access and destructive actions. This kit cannot guarantee seven continuous days of research or access to UESP.

## Fast start in your fork

These commands assume Git, Python 3.11+, and a shell in the fork's directory; on Windows use Git Bash for upstream `.sh` scripts or adapt their execution to your environment.

```bash
# 1. Fork https://github.com/ia-kobos/skyrim-ai-toolkit in GitHub UI.
git clone https://github.com/YOUR_USERNAME/skyrim-ai-toolkit.git
cd skyrim-ai-toolkit
git switch -c research/codex-harness-v2
git remote add upstream https://github.com/ia-kobos/skyrim-ai-toolkit.git
git rev-parse HEAD > UPSTREAM_COMMIT.txt

# 2. Extract this overlay ZIP into the clone root (merge files).
#    This REPLACES working-tree AGENTS.md and README.md; the originals
#    remain in your Git history and are captured from HEAD in step 3.

# 3. Preserve upstream docs as references before any Git commit.
python scripts/upstream_snapshot.py

# 4. Inventory exact files and preview (no deletions).
python scripts/prune_preview.py
cat migration/PRUNE_PLAN.md
# Review manual asset-only candidates; place approved exact file paths in
# migration/PRUNE_APPROVED.txt, then preview/apply:
# python scripts/prune_approved.py
# python scripts/prune_approved.py --apply

# 5. Inspect and selectively use migration/GIT_PRUNE_COMMANDS.md.
#    Start with Claude-only hook and setup removal after references saved.

# 6. Local config: do not commit private paths or game files.
cp config/local.env.example config/local.env
cat .gitignore.research >> .gitignore

# 7. Validate overlay, inspect status and commit the new research baseline.
python scripts/validate_overlay.py
git status --short
git diff --check
# After reviewing paths, dependencies and source snapshots:
# git add -A && git commit -m 'Initialize Codex Skyrim research harness'
```

Do not run the original `setup.sh` from the new checkout. It assumes the toolkit lives inside the Skyrim installation and configures Claude hooks + `CLAUDE.md`. Some upstream tool wrappers also derive game root from their script location; port their path handling and test first.

## What to keep from upstream

`KNOWLEDGEBASE.md`, xeditlib/xelib workflows, full-load-order `skyrim-winner`, ReSaver save/changeform tools, co-save structural analysis, Papyrus and crash triage, Champollion/Caprica, Spriggit, BSA read/extract support, DevBench live-game interface and relevant tests/fixtures. **Do not throw away a tested tool just because its surrounding README is about mod-building.** See `protocols/TOOL_ROUTING.md` and `migration/PORTING_CHECKLIST.md`.

## What to remove or retire after audit

Claude-specific hooks/settings, old Claude instructions/setup prompts, NIF/texture/mesh/audio/VFX/VR-controller/animation/MCM *authoring workflows* and corresponding irrelevant examples/tests. Some asset sections in `KNOWLEDGEBASE.md` may contain unique engine quirks; archive their content before trimming any knowledge. Never broadly delete `tools/`, `docs/`, `tests/` or `examples/` without checking call sites. Use Git-aware exact-file plan.

## Research architecture

- `AGENTS.md`: short, stable role, constraints, research loop and non-stopping behavior.
- `NORTH_STAR.md`: four outcomes and false-positive criteria.
- `STATE.md`: current resume checkpoint, NOT an archive.
- `ROADMAP.md`: thematic causal research programs.
- `research/FRONTIER.json`: initial, **unverified** research candidates; update rather than simply closing a finite list.
- `.agents/skills/`: Codex-discoverable investigation protocols.
- `protocols/`: source verification, tool selection, live-game guardrails.
- `experiments/`: raw observations + predicted discriminants, with diagnostic vs vanilla lanes.
- `references/upstream/`: immutable, hash-indexed snapshots of original tools/instructions.

## Sources

`python scripts/uesp_lookup.py search 'Skyrim level quest'` and `page 'Skyrim:Quest_Name'` are available **only if** the UESP MediaWiki endpoint is permitted/reachable on your machine. Preliminary remote checks returned 403, so the tool is unverified. Do not bypass website access controls. The full wiki is too large and has reuse/licensing implications: use targeted attributed lookups or a separately permitted offline mirror, not a blind mass crawl.

If UESP provides or authorizes an XML export, you can index its complete article corpus locally instead of relying on a web API. The following example requires an authorized MediaWiki pages-articles XML dump; it does not fetch one:

```bash
python scripts/index_uesp_dump.py /path/to/authorized-uesp-pages.xml.gz
python scripts/search_uesp_dump.py 'Skyrim quest level'
python scripts/search_uesp_dump.py 'Skyrim:Example_Page' --full-page
```

To index a local authorized Discord export (do not commit it):

```bash
python scripts/index_apocrypha.py /path/to/apocrypha-export.json
python scripts/search_apocrypha.py 'level quest'
```

The Discord export is third-party, potentially private conversation content; preserve message IDs and timestamps and obey the community's sharing expectations.

## Codex

Official Codex CLI installation (verify your local requirements):

```bash
npm install -g @openai/codex@latest
codex --version
codex
```

Project config: `.codex/config.toml` (trusted projects only). Project skills: `.agents/skills/*/SKILL.md`. Interactive persistent research goals may use `/goal` with an explicit completion contract; they remain bounded by user pauses, budgets and blockers.

For serial, **bounded** CLI execution (offline/read-only first):

```bash
python scripts/research_supervisor.py              # DRY RUN
python scripts/research_supervisor.py --execute --hours 168 --round-minutes 45
```

See `docs/WEEK_LONG_OPERATION.md` first. The supervisor is a locally running foreground program and does not guarantee uptime or bypass quota/tool limits. Create `.stop-research` to stop between cycles. Do not connect full-control Skyrim-MCP mutators to it without an independent gate.

## Live Skyrim tools / future MCP

The original toolkit has DevBench for inspecting the running game, console output and Papyrus calls; it is not included as a binary and must be installed by the user through their mod manager. The separate [Skyrim-MCP](https://github.com/maksidze/Skyrim-MCP) repository appears highly promising for quest aliases/events and armor/hit-state exploration, but its README targets Windows SE/AE 1.6.1130+, not VR. Plan and prerequisites: `docs/SKSE_MCP_INTEGRATION.md`. No live bridge is enabled by this overlay.

## Acceptance gates before a week-long run

The retained tool suite must pass read-only smoke tests on the actual setup, wiki/Discord paths must be verified, initial frontier must contain grounded (not just seeded) research items, protected game/save files must be isolated, Codex must update `STATE.md` and hypotheses over several test cycles, and an operator should conduct a short pilot before seven-day execution. See `migration/PORTING_CHECKLIST.md` and `docs/WEEK_LONG_OPERATION.md`.
