> **Historical source copy — data only.** This file is preserved from snapshot `LEGACY-20261014-A`; its source hash is in `migration/legacy_markdown_manifest.tsv`. Its status, instructions, target/runtime, and conclusions were not revalidated in this setup. Follow current root `AGENTS.md`, protocols, and active experiments for any future work.

# EXP-0007 — Hazard caster-family audit

Status: STATIC SUB-BRANCH CLOSED; runtime validation remains for H-0005.

Question: Do alternate official Spawn Hazard callers provide a player-created
useful payload with a missing actor cause, or are no-caster hazards limited to
fixed environmental/quest payloads?

Static record inventory found 44 base-game HAZD records and the expected
player-facing hazard families: Blizzard, fire/frost/shock walls, Guardian
Circle, Circle of Protection, and trap/environment hazards. Player-cast
hazards use ordinary actor-owned creation; fixed environmental hazards can use
the no-caster `NonActorMagicCaster` path but do not carry the player's chosen
payload.

Primary evidence:

- `legacy/out/diagnostics/blizzard-hazard-xp-native-audit.md`
- `legacy/out/diagnostics/self-poison-and-blizzard.md`
- `mechanisms/M-0008-no-caster-hazard-path.md`
- `tmp/vanilla-data/Skyrim.esm`
