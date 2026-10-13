#!/usr/bin/env python3
"""Validate Codex settings, research files, and substantive skill metadata."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md",
    "NORTH_STAR.md",
    "STATE.md",
    "ROADMAP.md",
    "research/FRONTIER.json",
    "research/CLAIMS.md",
    "research/CONTRADICTIONS.md",
    "protocols/TOOL_ROUTING.md",
    "protocols/LIVE_GAME.md",
    "migration/SOURCE_MAP.md",
    "migration/SKILL_MIGRATION.md",
    "migration/TOOL_AUDIT.md",
    "migration/PRUNE_REPORT.md",
    "migration/UNRESOLVED.md",
    "migration/MIGRATION_PROGRESS.md",
    ".github/copilot-instructions.md",
    ".codex/config.toml",
)


def validate() -> list[str]:
    errors = [f"missing {path}" for path in REQUIRED if not (ROOT / path).is_file()]

    try:
        config = tomllib.loads((ROOT / ".codex/config.toml").read_text(encoding="utf-8"))
        if config.get("approval_policy") != "on-request":
            errors.append("Codex approval_policy must be on-request")
        if config.get("sandbox_mode") != "workspace-write":
            errors.append("Codex sandbox_mode must be workspace-write")
        if "mcp_servers" in config:
            errors.append("live MCP servers must not be enabled by the shared project config")
        if config.get("features", {}).get("hooks") is True:
            errors.append("provider-specific hooks must not be enabled as a safety boundary")
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"invalid Codex TOML: {exc}")

    settings_path = ROOT / ".claude/settings.json"
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            if settings.get("hooks", {}) != {}:
                errors.append("legacy Claude hook registrations must remain disabled")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid legacy Claude settings JSON: {exc}")

    try:
        frontier = json.loads((ROOT / "research/FRONTIER.json").read_text(encoding="utf-8"))
        items = frontier["items"]
        ids = [item["id"] for item in items]
        if len(ids) != len(set(ids)):
            errors.append("duplicate research frontier IDs")
        if not {"OBJ-1", "OBJ-2"}.issubset({item["objective"] for item in items}):
            errors.append("frontier must retain both P0 objectives")
        for item in items:
            if not isinstance(item.get("evidence"), list):
                errors.append(f"{item.get('id', '?')}: evidence must be a list")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"invalid research frontier: {exc}")

    skill_files = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    if len(skill_files) < 9:
        errors.append(f"expected at least 9 migrated research skills, found {len(skill_files)}")
    skill_names: set[str] = set()
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
        if not match:
            errors.append(f"{path.relative_to(ROOT)}: missing frontmatter")
            continue
        frontmatter, body = match.groups()
        name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", frontmatter, re.M)
        description = re.search(r"^description:\s*(.{40,})$", frontmatter, re.M)
        expected = path.parent.name
        if not name:
            errors.append(f"{path.relative_to(ROOT)}: missing valid name")
        elif name.group(1) != expected:
            errors.append(f"{path.relative_to(ROOT)}: name does not match skill directory")
        elif name.group(1) in skill_names:
            errors.append(f"{path.relative_to(ROOT)}: duplicate skill name")
        else:
            skill_names.add(name.group(1))
        if not description:
            errors.append(f"{path.relative_to(ROOT)}: missing substantive description")
        if len(re.findall(r"\b[\w'-]+\b", body)) < 120:
            errors.append(f"{path.relative_to(ROOT)}: workflow is too short to qualify as a migrated skill")
        if re.search(r"^paths:", frontmatter, re.M):
            errors.append(f"{path.relative_to(ROOT)}: remove unsupported Claude-only paths metadata")

    return errors


def main() -> int:
    errors = validate()
    print("RESEARCH HARNESS VALIDATION " + ("FAIL" if errors else "PASS"))
    for error in errors:
        print(f" - {error}")
    if not errors:
        print(f"Validated {len(list((ROOT / '.agents/skills').glob('*/SKILL.md')))} skill workflows and the research frontier.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
