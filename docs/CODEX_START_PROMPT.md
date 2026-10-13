# First Codex session prompt (after fork port + baseline verification)

Paste into Codex in the forked repository:

```text
Read AGENTS.md, NORTH_STAR.md, STATE.md, ROADMAP.md, research/FRONTIER.json,
protocols/TOOL_ROUTING.md, and migration/PORTING_CHECKLIST.md.

Your immediate objective is to bring the RESEARCH harness to validated readiness,
not to build a Skyrim mod.

First audit the fork's tracked files and the upstream artifacts in
references/upstream. Verify that the old Claude instructions contain no unique
operating knowledge missing from new protocols. Inventory native tools and
version/path assumptions; migrate useful Claude skills to .agents/skills,
without carrying asset-authoring workflows forward.

Then validate tools on read-only fixtures and establish a sourced, precise
research frontier focused overwhelmingly on the two P0 goals:
  1) trigger normally level-locked quests/encounters at level one;
  2) retain effective equipped armor without gaining armor skill XP from hits.

Import existing source notes and SKSE/Ghidra discoveries with provenance.
Check basic assumptions against UESP/Apocrypha if authorized and available;
otherwise record an access blocker and use verifiable game records.

Run research continuously by cycling between deep investigation and
cross-system synthesis. If a question depends on user-run tests, write a full
discriminating protocol, mark it awaiting-user-data, then continue another.
Never treat console-forced states or edited game records as a verified vanilla
exploit. Do not alter the original game installation or saves.

Before every CLI/context boundary, update STATE.md, the frontier and
research/SESSION_LOG.md. Do not spend the session rephrasing prior work.
```

During interactive pilot, start with this prompt; use `/goal` if your Codex version supports it. Only use `research_supervisor.py --execute` after the migration and read-only preflight have passed.
