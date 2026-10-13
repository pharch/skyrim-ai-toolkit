# Live-Game Testing Protocol

## Allowed lanes

- **offline**: Ghidra, records, decompilation, saves copied to fixtures. Preferred autonomous lane.
- **diagnostic**: isolated throwaway save, approved DevBench/SKSE access, explicit tagged state changes (`setstage`, `modav`, spawning, load/save) to map mechanisms. Outcomes are not vanilla exploits.
- **vanilla-validation**: baseline clean save with only approved observational instrumentation. Test user-reproducible steps with no mod-mediated alteration of conditions.

## Minimum before a live action

Record game version, SKSE version, load order, exact save ID and duplicate save backup, existing quest state, current level, skills/XP, relevant ActorValues, active effects, equipped items, timestamp and plugin list. Show state-diff afterward. Unique saves and game files are protected.

## DevBench baseline (provided by upstream)

`bash tools/devbench-cli.sh alive` (not `ping` alone), then `health`, `state`, `inspect vm`. Inspect `CLAUDE.md` from archived upstream docs for the exact invocation patterns. Example of a read-only console request when correctly routed: `bash tools/devbench-cli.sh exec "player.getav health"`. Since the upstream wrapper assumes game-root placement in places, verify URL/port and game-instance identity first. Do not expose its general `exec`/`call` to unattended agents without a gate.

## Probe safeguards

- Generate an experiment manifest specifying allowed commands/forms/variables, preconditions, before/after captures and rollback.
- Use a separate test save and enforce command-level allowlist from trusted code, not only natural-language instructions.
- Deny plugin file writes, registry writes, save deletion, unknown teleport, overwriting main saves, and unbounded loops.
- For quest research, stage mutations are **diagnostic controls** only. Detect progression via journal, quest instance state, stage history, world-state effects and corresponding events; a `setstage` success alone is not an unlock.
- For armor XP, capture actual hit/damage and armor skill XP; state snapshots alone may not expose sub-level XP accurately—add a purpose-built read-only probe if required.
- If the game is loading, saving, freezing, or in an unsafe state, stop *that* experiment and continue offline research.

## Integration maturity

DevBench: upstream capability documented, local installation **unverified**.
SkyLink / Skyrim-MCP: design only; not installed. See `docs/SKSE_MCP_INTEGRATION.md`.
