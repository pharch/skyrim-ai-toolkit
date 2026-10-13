# Skyrim AE Glitch-Research Harness

An offline-first Codex workspace for evidence-backed research into Skyrim
Anniversary Edition engine behavior. It is **not** a mod pack, game installer,
or mod-authoring workflow. Priority research targets are:

1. Trigger a normally level-locked quest, encounter, or event while the
   character remains level 1, using a reproducible vanilla-game sequence.
2. Wear effective armor, receive verified hits, and gain zero armor skill XP.
3. Measure cumulative enchanting XP at the 15→16 and 20→21 boundaries.
4. Test whether alchemical ActiveEffects persist indefinitely across relevant
   transitions.

No exploit is currently claimed as verified merely because a frontier item is
open. See [STATE.md](./STATE.md), [research/FRONTIER.json](./research/FRONTIER.json),
and the [claims ledger](./research/CLAIMS.md).

## Start here

```sh
git clone https://github.com/pharch/skyrim-ai-toolkit.git
cd skyrim-ai-toolkit
python scripts/setup_research.py init
python scripts/setup_research.py check
npm ci
npm test
python -m pytest -q
```

Install and authenticate the Codex CLI using the official Codex documentation,
then open this trusted checkout with `codex`. Project guidance is in
[AGENTS.md](./AGENTS.md); investigation procedures are in
[.agents/skills/](./.agents/skills/). `config/local.env` is private and ignored
by Git; fill it in only on the Windows research machine.

## Skyrim AE targeting

The supported executable is `SkyrimSE.exe` with ProductVersion **1.6.318 or
newer**. On Windows, configure:

```dotenv
SKYRIM_EDITION=AE
GAME_ROOT=C:/Games/Skyrim Special Edition
SKYRIM_EXE_PATH=
PLUGINS_TXT=C:/Users/you/AppData/Local/Skyrim Special Edition/plugins.txt
```

Run `node tools/ae-preflight.js` before xEdit or live-game access. It reads the
executable's Windows version resource, hashes the executable, and verifies the
active plugin list. MO2 users must point `PLUGINS_TXT` to the selected AE
profile's virtualized list. The harness never scans and guesses among edition
paths; an empty, duplicate, or non-`Skyrim.esm`-first order fails closed.

Linux CI can validate parsers, fixtures, and repository policy. It cannot test
the Windows PE version reader against the user's game, the xEditLib DLL and
registry, MO2 virtualization, DevBench, or in-game behavior. The exact Windows
verification steps are in [docs/getting-started.md](./docs/getting-started.md).

## Research durability

- `research/FRONTIER.json` is the machine-readable queue with explicit evidence
  links and blockers.
- `research/CLAIMS.md`, `research/CONTRADICTIONS.md`, and
  `research/KNOWLEDGE_GRAPH.md` hold sourced claims, unresolved conflicts, and
  causal edges.
- `research/SESSION_LOG.md` and `STATE.md` provide append-only session notes and
  an exact recovery checkpoint.
- `scripts/research_supervisor.py` is an opt-in, bounded serial Codex runner.
  Inspect its dry run and safety configuration before using `--execute`.
  Create `.stop-research` for a graceful stop between cycles.

Never treat `setstage`, `setlevel`, injected scripts, altered plugins, or
patched executables as a vanilla-valid result. Preserve raw evidence and
negative results. Live experiments use a separately approved disposable save;
unattended runs must remain offline and must not receive arbitrary mutator
tools.

## Retained tools

Concrete commands, prerequisites, and limits are documented in
[the retained-tool skill](./.agents/skills/retained-tool-operations/SKILL.md)
and [tool routing](./protocols/TOOL_ROUTING.md). In brief: xEdit/xelib and
DevBench require Windows; ReSaver, co-save inspection, Papyrus/crash triage,
source indexing, and fixture tests are offline analysis. Optional proprietary
or third-party binaries are not bundled.

## Provenance and licensing

This repository retains its upstream license and Git history. Original
Original upstream material is archival only under `references/upstream/` or
`KNOWLEDGEBASE.md`; it is not active guidance. Do not commit game binaries,
saves, private exports, local paths, API keys, or raw Discord data.
