# SKSE / MCP integration policy

This repository does not install or enable live MCP servers by default. The active Codex config in `.codex/config.toml` remains a workspace-local, read-only repository policy and does not include a live server connection.

## Allowed status
- Optional, future integration only.
- Must be documented as a local Windows-only future stage.
- Must not be treated as required for repository readiness.
- Must not be enabled by default in CI or a repo configuration file.

## Forbidden status
- No live SKSE/MCP endpoint is automatically launched by this repo.
- No mutating game server or process is exposed to an unattended run.
- No Windows game connection is implied by Linux validation or by a repository check.

## Process
If a local Windows research session later decides to integrate SKSE or MCP tooling:
1. Verify `SkyrimSE.exe` ProductVersion `1.6.318+` with `python3 scripts/python_env.py run tools/ae_preflight.py`.
2. Confirm the exact active `plugins.txt` and selected MO2 profile.
3. Keep the integration strictly optional and separate from the repository's core offline validation.
4. Preserve raw logs and hashes; never silently rewrite them.

This document exists to keep the repository honest: no live runtime integration is considered validated until the exact Windows AE preflight passes.
