#!/usr/bin/env python3
"""Validate Codex research setup, strict AE scope, skills, and durable state."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

try:
    from .validate_research import validate as validate_research
except ImportError:
    from validate_research import validate as validate_research

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md",
    "NORTH_STAR.md",
    "STATE.md",
    "ROADMAP.md",
    "research/FRONTIER.json",
    "research/EVIDENCE.json",
    "research/EVIDENCE_MODEL.md",
    "research/CLAIMS.md",
    "research/CONTRADICTIONS.md",
    "research/KNOWLEDGE_GRAPH.md",
    "research/SESSION_LOG.md",
    "research/RECOVERY.json",
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
    "scripts/setup_research.py",
    "scripts/validate_research.py",
    "tools/ae-target.js",
    "tools/ae-preflight.js",
    "docs/getting-started.md",
)


def validate(root: Path = ROOT) -> list[str]:
    errors = [f"missing {path}" for path in REQUIRED if not (root / path).is_file()]

    for legacy in (".claude", "CLAUDE.md", "SETUP_PROMPT.txt", "setup.sh"):
        if (root / legacy).exists():
            errors.append(f"legacy active Claude/game-install surface remains: {legacy}")

    try:
        config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
        if config.get("approval_policy") != "on-request":
            errors.append("Codex approval_policy must be on-request")
        if config.get("sandbox_mode") != "workspace-write":
            errors.append("Codex sandbox_mode must be workspace-write")
        if "mcp_servers" in config:
            errors.append("shared Codex config must not enable live MCP servers")
        if config.get("features", {}).get("hooks") is True:
            errors.append("provider-specific hooks must not be a safety boundary")
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"invalid Codex TOML: {exc}")

    template = root / "config/local.env.example"
    if template.is_file():
        values = {}
        for line in template.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("\"'")
        if values.get("SKYRIM_EDITION") != "AE":
            errors.append("local configuration template must explicitly target AE")
        if "SKYRIM_GAME_VERSION" in values:
            errors.append("typed SKYRIM_GAME_VERSION must not substitute for executable detection")

    try:
        package = json.loads((root / "package.json").read_text(encoding="utf-8"))
        if int(package.get("engines", {}).get("node", "0").split(".")[0].lstrip(">=")) < 20:
            errors.append("Node.js 20 or newer must be declared")
    except (OSError, json.JSONDecodeError, ValueError, AttributeError) as exc:
        errors.append(f"invalid package.json engine metadata: {exc}")

    skills = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    if len(skills) < 10:
        errors.append(f"expected at least 10 Codex research/tool skills, found {len(skills)}")
    names: set[str] = set()
    for path in skills:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
        relative = path.relative_to(root)
        if not match:
            errors.append(f"{relative}: missing frontmatter")
            continue
        frontmatter, body = match.groups()
        name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", frontmatter, re.M)
        description = re.search(r"^description:\s*(.{40,})$", frontmatter, re.M)
        if not name:
            errors.append(f"{relative}: missing valid skill name")
        elif name.group(1) != path.parent.name:
            errors.append(f"{relative}: skill name does not match directory")
        elif name.group(1) in names:
            errors.append(f"{relative}: duplicate skill name")
        else:
            names.add(name.group(1))
        if not description:
            errors.append(f"{relative}: missing substantive skill description")
        if len(re.findall(r"\b[\w'-]+\b", body)) < 120:
            errors.append(f"{relative}: skill workflow is too short to preserve its operating knowledge")
        if re.search(r"^paths:", frontmatter, re.M):
            errors.append(f"{relative}: unsupported Claude-only paths metadata remains")

    errors.extend(validate_research(root))
    brief = root / "migration/FINAL_SETUP_BRIEF.md"
    if not brief.is_file():
        errors.append("authoritative migration/FINAL_SETUP_BRIEF.md is missing; exact 82-item finalization gate cannot be validated")
    checklist = root / "migration/FINALIZATION_CHECKLIST.md"
    if not checklist.is_file():
        errors.append("migration/FINALIZATION_CHECKLIST.md is missing")
    elif brief.is_file():
        text = checklist.read_text(encoding="utf-8")
        criteria = re.findall(r"^-\s+\[(?:x|X| )\]\s+AC-(\d{2}):\s+(.+?)\s+\|\s+Evidence:\s*(.*?)\s*$", text, re.M)
        ids = [int(item[0]) for item in criteria]
        if len(criteria) != 82 or ids != list(range(1, 83)):
            errors.append("finalization checklist must contain ordered AC-01..AC-82 evidence entries")
        if any(not evidence.strip() for _, _, evidence in criteria):
            errors.append("every finalization checklist criterion must record evidence")
        if len(re.findall(r"^-\s+\[ \]\s+AC-\d{2}:", text, re.M)):
            errors.append("one or more finalization criteria are not complete")
    elif "Status: NOT COMPLETE." not in checklist.read_text(encoding="utf-8"):
        errors.append("without the authoritative brief, the checklist must remain explicitly blocked")

    return errors


def main() -> int:
    errors = validate()
    print("CODEX AE RESEARCH HARNESS " + ("FAIL" if errors else "PASS"))
    for error in errors:
        print(f" - {error}")
    if not errors:
        print("Repository structure, Codex skills, AE targeting policy, and evidence/frontier data validate.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
