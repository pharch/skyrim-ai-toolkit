# Later Integration: SkyLink AI / Skyrim-MCP

**Not part of the initial fork prune/build.** This is the integration design to evaluate after the existing read-only toolkit and DevBench lanes have passed tests.

Upstream: https://github.com/maksidze/Skyrim-MCP (source review required). Documented architecture is a C# stdio MCP server (.NET 10) connected via a named pipe to a CommonLibSSE-NG SKSE plugin running inside Skyrim. README advertises 74 tools, including player/inventory read, quest state/stages/aliases, NPCs, console commands, world, 17 event groups, Papyrus function introspection and invocation, load/save and state snapshots. The advertised supported game is SE/AE v1.6.1130+ on Windows; VR is **not documented as supported**. Verify your exact game build before attempting installation.

## Capability comparison

| Need | Existing toolkit/DevBench | Skyrim-MCP candidate |
|---|---|---|
| Repeated controlled actor-value snapshot | DevBench inspect/console, possibly custom probe | Player details, resistances, blueprint; verify whether exact AV modifier/skill XP components are exposed |
| Quest initiation/gate experiment | DevBench console + Papyrus | Quest stages, aliases, start/stop/complete, quest events |
| Correlated on-hit/XP capture | May need dedicated SKSE probe | Hits/combat/event stream + player skills, but per-hit skill XP granularity must be verified |
| Inventory/armor state | Console/custom probes | Equipped 32 slots, enchantment data, equip/unequip events |
| Crash/liveness diagnostics | DevBench + CrashLogger | Safety check/events, but add process watchdog |
| Version reliability | Tool-specific | CommonLib/Address Library/version verification required |

## Proposed integration boundaries

1. **Read-only first.** Configure server in Codex only after testing executable hash, build, game-side plugin and exact tool schemas; inspect public C# code. Start with status, player info, quest query and events.
2. **Observational benchmark.** Against a copied save compare direct DevBench queries, Skyrim-MCP queries, xEdit records and custom SKSE probe on representative known truths. Measure availability, stale reads, event omissions and execution latency.
3. **A safety gateway between Codex and game tools.** Build a new narrow MCP facade or wrapper exposing research primitives: `snapshot_state`, `list_quest_gates`, `observe_events`, `run_tagged_controlled_test`. Require experiment manifest, explicit allowed tool subset, rollback state and independent audit log. Never expose all 74 mutators to an unattended agent by default.
4. **Quest experiment flow.** Snapshot save/state -> subscribe to quest/location/activation events -> perform *approved reversible diagnostic intervention* -> capture all quest stages/aliases/conditions -> restore -> attempt vanilla-accessible equivalent in clean validation lane. Do not present forced stages as bypasses.
5. **Armor experiment flow.** Capture equipment + XP baseline -> verify hit actually occurred -> inspect XP and armor rating -> compare tagged controls -> restore test save. Custom probe required if bridge lacks exact skill XP measurement.
6. **Prefer compositional reuse.** Keep raw SkyLink as independently version-pinned component; don't copy its code into this fork without license/dependency review. Existing wrappers and MCP can coexist; deduplicate only after independent capability tests.
7. **Failure handling.** Named pipe unavailable, game load state, plugin crash, unknown version or null response: fail closed and return to offline lane; do not retry mutations blindly.

## Codex configuration proposal (manual opt-in; exact DLL path discovered locally)

```toml
# Add to a trusted local Codex config only after installing and verifying the bridge:
# [mcp_servers.skyrimReadOnlyGateway]
# command = "dotnet"
# args = ["C:\\path\\to\\verified\\gateway.dll"]
```

The upstream server's example launches `dotnet` with `Data\\SKSE\\Plugins\\SkyLinkAI_Server\\SkyrimMCP.dll`, but wiring it directly exposes all tools; prefer a gated gateway. The console and quest-stage mutation APIs are especially high risk for confounding experiments.

## Go / no-go checks

Version supported; original saves untouched; stable game connectivity; exact tool list inspected; event ordering understood; baseline queries verified; no mutations without approved manifest; game process crash/isolation test passed; logs with run IDs and before/after snapshots. Until then leave MCP disabled.
