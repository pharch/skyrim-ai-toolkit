#!/usr/bin/env python3
"""Validate Codex discovery, AE policy, research state, and finalization closure."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlparse

import yaml

try:
    from .validate_research import validate as validate_research
except ImportError:
    from validate_research import validate as validate_research

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md", "NORTH_STAR.md", "STATE.md", "ROADMAP.md",
    "research/FRONTIER.json", "research/EVIDENCE.json",
    "research/EVIDENCE_MODEL.md", "research/CLAIMS.md",
    "research/CONTRADICTIONS.md", "research/KNOWLEDGE_GRAPH.md",
    "research/SESSION_LOG.md", "research/RECOVERY.json",
    "research/schema/frontier.schema.json", "research/schema/evidence.schema.json",
    "protocols/TOOL_ROUTING.md", "protocols/LIVE_GAME.md",
    "migration/FINAL_SETUP_BRIEF.md", "migration/FINALIZATION_CHECKLIST.md",
    "migration/FINALIZATION_LOG.md", "migration/SOURCE_MAP.md",
    "migration/SKILL_MIGRATION.md", "migration/TOOL_AUDIT.md",
    "migration/PRUNE_REPORT.md", "migration/UNRESOLVED.md",
    "migration/MIGRATION_PROGRESS.md", "migration/RESUME.md",
    ".github/copilot-instructions.md", ".codex/config.toml",
    "scripts/setup_research.py", "scripts/validate_research.py",
    "scripts/research_state.py", "tools/ae-target.js",
    "tools/ae-preflight.js", "tools/README.md", "docs/README.md",
    "docs/CODEX_START_PROMPT.md", "docs/WINDOWS_AE_VERIFICATION.md",
    "docs/SKSE_MCP_INTEGRATION.md", "experiments/TRANSACTION_TEMPLATE.md",
)
SKILL_KEYS = {
    "name", "description", "argument-hint", "user-invocable",
    "disable-model-invocation", "license", "compatibility", "metadata",
}
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
CHECKLIST_LINE = re.compile(
    r"^-\s+\[ \]\s+\*\*([A-Z]\d{2})\*\*\s+(.+?)\s+\*\*Status:\s*"
    r"(TODO|IN_PROGRESS|PASS|BLOCKED_ENV|FAIL)\*\*\s+\|\s+Evidence:\s*(.+)$",
    re.M,
)
BRIEF_CRITERION = re.compile(r"^-\s+\[ \]\s+\*\*([A-Z]\d{2})\*\*\s+(.+?)\s*$", re.M)
ALLOWED_ENV_BLOCKERS = {"I05"}


def _relative_links(markdown: str):
    for target in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", markdown):
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#"):
            continue
        yield target


def _resolve_reference(path: Path, root: Path, target: str) -> Path:
    cleaned = target.split("#", 1)[0]
    candidates = [
        (path.parent / cleaned).resolve(),
        (root / cleaned).resolve(),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _validate_skills(root: Path) -> list[str]:
    errors: list[str] = []
    skill_root = root / ".agents/skills"
    paths = sorted(skill_root.glob("*/SKILL.md"))
    if not paths:
        return ["no discoverable .agents/skills/*/SKILL.md files"]
    names: set[str] = set()
    for path in paths:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
        if not match:
            errors.append(f"{relative}: missing YAML frontmatter")
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{relative}: invalid YAML frontmatter: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{relative}: frontmatter must be a YAML mapping")
            continue
        unknown = sorted(set(metadata) - SKILL_KEYS)
        if unknown:
            errors.append(f"{relative}: unsupported skill metadata key(s): {', '.join(unknown)}")
        name = metadata.get("name")
        if not isinstance(name, str) or len(name) > 64 or not SKILL_NAME.fullmatch(name):
            errors.append(f"{relative}: name must be 1-64 lowercase alphanumeric/hyphen characters")
        elif name != path.parent.name:
            errors.append(f"{relative}: skill name does not match its folder")
        elif name in names:
            errors.append(f"{relative}: duplicate skill name {name}")
        else:
            names.add(name)
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{relative}: description must be non-empty text of at most 1024 characters")
        for key in ("user-invocable", "disable-model-invocation"):
            if key in metadata and not isinstance(metadata[key], bool):
                errors.append(f"{relative}: {key} must be a boolean")
        if "paths" in metadata:
            errors.append(f"{relative}: Claude-only paths metadata is not supported")
        body = text[match.end():]
        for link in _relative_links(body):
            target = _resolve_reference(path, root, link)
            if not target.exists():
                errors.append(f"{relative}: broken skill link {link}")
        for referenced in re.findall(r"`((?:\./)?(?:scripts|references|assets)/[^`]+)`", body):
            target = _resolve_reference(path, root, referenced.removeprefix("./"))
            if not target.exists():
                errors.append(f"{relative}: missing referenced skill resource {referenced}")
    return errors


def _validate_checklist(root: Path) -> list[str]:
    brief_path = root / "migration/FINAL_SETUP_BRIEF.md"
    checklist_path = root / "migration/FINALIZATION_CHECKLIST.md"
    if not brief_path.is_file() or not checklist_path.is_file():
        return ["authoritative brief and exact finalization checklist must both exist"]
    brief = brief_path.read_text(encoding="utf-8")
    section = brief.split("## 15. Closure checklist", 1)
    if len(section) != 2:
        return ["authoritative brief has no Section 15 closure checklist"]
    expected = BRIEF_CRITERION.findall(section[1].split("\n## 16.", 1)[0])
    checklist = checklist_path.read_text(encoding="utf-8")
    actual = CHECKLIST_LINE.findall(checklist)
    errors: list[str] = []
    expected_ids = [criterion_id for criterion_id, _ in expected]
    actual_ids = [criterion_id for criterion_id, _, _, _ in actual]
    if len(expected) != 82 or expected_ids != [f"{letter}{number:02d}" for letter, count in zip("ABCDEFGHIJ", [7, 8, 10, 9, 9, 6, 11, 5, 12, 5]) for number in range(1, count + 1)]:
        errors.append(f"brief Section 15 must contain its 82 ordered A01..J05 items; found {len(expected)}")
    if actual_ids != expected_ids:
        errors.append("checklist IDs or ordering do not exactly match the authoritative Section 15")
    if len(actual) != 82:
        errors.append(f"checklist must contain 82 complete status/evidence fields; found {len(actual)}")
    expected_by_id = dict(expected)
    for criterion_id, text, status, evidence in actual:
        if expected_by_id.get(criterion_id) != text:
            errors.append(f"{criterion_id}: criterion wording differs from the authoritative brief")
        if not evidence.strip():
            errors.append(f"{criterion_id}: evidence field is empty")
        if status in {"TODO", "IN_PROGRESS", "FAIL"}:
            errors.append(f"{criterion_id}: finalization status is {status}")
        if status == "BLOCKED_ENV":
            if criterion_id not in ALLOWED_ENV_BLOCKERS:
                errors.append(f"{criterion_id}: BLOCKED_ENV is not an approved external criterion")
            if criterion_id == "I05":
                guide = root / "docs/WINDOWS_AE_VERIFICATION.md"
                if not guide.is_file() or "node tools/ae-preflight.js" not in guide.read_text(encoding="utf-8"):
                    errors.append("I05: BLOCKED_ENV requires actionable Windows AE verification instructions")
    if not re.search(r"^\s*-\s+\*\*I05\*\*:", checklist, re.M):
        errors.append("checklist must explain why I05 is environment-blocked")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors = [f"missing {path}" for path in REQUIRED if not (root / path).is_file()]
    for legacy in ("CLAUDE.md", "SETUP_PROMPT.txt", "setup.sh", ".claude"):
        if (root / legacy).exists():
            errors.append(f"obsolete active Claude/game-install surface remains: {legacy}")

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
        node_engine = str(package.get("engines", {}).get("node", ""))
        if not re.search(r"(?:\^|>=)?20(?:\.|$)", node_engine):
            errors.append("Node.js 20 or newer must be declared")
    except (OSError, json.JSONDecodeError, ValueError, AttributeError) as exc:
        errors.append(f"invalid package.json engine metadata: {exc}")

    errors.extend(_validate_skills(root))
    errors.extend(validate_research(root))
    errors.extend(_validate_checklist(root))

    workflow = root / ".github/workflows/ci.yml"
    if workflow.is_file():
        try:
            workflow_text = workflow.read_text(encoding="utf-8")
            if "glitch-hunting-setup" not in workflow_text:
                errors.append("CI push trigger must include glitch-hunting-setup")
        except OSError as exc:
            errors.append(f"cannot read CI workflow: {exc}")
    return errors


def main() -> int:
    errors = validate()
    print("CODEX AE RESEARCH HARNESS " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print(f" - {error}")
    if not errors:
        print("Codex discovery, exact checklist, AE policy, and durable evidence/frontier state validate.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
