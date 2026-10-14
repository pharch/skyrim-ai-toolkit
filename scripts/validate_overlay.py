#!/usr/bin/env python3
"""Validate Codex discovery, AE policy, research state, and the current setup audit."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

import yaml

try:
    from .validate_research import validate as validate_research
except ImportError:
    from validate_research import validate as validate_research

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.setup_audit import parse_prompt as parse_setup_prompt  # noqa: E402
from tools.setup_audit import validate as validate_setup_checklist  # noqa: E402
REQUIRED = (
    "AGENTS.md", "NORTH_STAR.md", "STATE.md", "ROADMAP.md",
    "research/FRONTIER.json", "research/EVIDENCE.json",
    "research/EVIDENCE_MODEL.md", "research/CLAIMS.md",
    "research/CONTRADICTIONS.md", "research/KNOWLEDGE_GRAPH.md",
    "research/SESSION_LOG.md", "research/RECOVERY.json",
    "research/schema/frontier.schema.json", "research/schema/evidence.schema.json",
    "research/schema/markdown-entities.md",
    "protocols/TOOL_ROUTING.md", "protocols/LIVE_GAME.md",
    "migration/FINAL_SETUP_BRIEF.md", "migration/FINALIZATION_CHECKLIST.md",
    "session-brief/LOCAL_CODEX_FINAL_AUDIT_PROMPT.md",
    "migration/local_setup_checklist.json", "migration/LOCAL_SETUP_CHECKLIST.md",
    "tools/setup_audit.py", "scripts/python_env.py", "scripts/pre_push_audit.py",
    "tools/ae_target.py", "tools/ae_preflight.py", "tools/plugin_reader.py",
    "tools/domain_doctor.py", "environment.yml", "migration/PRE_PUSH_SETUP_SUMMARY.md",
    "migration/FINALIZATION_LOG.md", "migration/SOURCE_MAP.md",
    "migration/SKILL_MIGRATION.md", "migration/TOOL_AUDIT.md",
    "migration/PRUNE_REPORT.md", "migration/UNRESOLVED.md",
    "migration/MIGRATION_PROGRESS.md", "migration/RESUME.md",
    ".github/copilot-instructions.md", ".codex/config.toml",
    "scripts/setup_research.py", "scripts/validate_research.py",
    "scripts/research_state.py", "tools/README.md", "docs/README.md",
    "docs/CODEX_START_PROMPT.md", "docs/WINDOWS_AE_VERIFICATION.md",
    "docs/SKSE_MCP_INTEGRATION.md", "experiments/TRANSACTION_TEMPLATE.md",
)
SKILL_KEYS = {
    "name", "description", "argument-hint", "user-invocable",
    "disable-model-invocation", "license", "compatibility", "metadata",
}
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
CHECKLIST_ROW = re.compile(
    r"^\|\s*([A-G]\d{2})\s*\|\s*`(TODO|IN_PROGRESS|PASS|BLOCKED_EXTERNAL|FAIL|NOT_APPLICABLE)`"
    r"\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(?:—|\d{4}-\d{2}-\d{2})\s*\|$",
    re.M,
)
ARCHIVED_MARKDOWN = {
    "CHANGELOG.md", "KNOWLEDGEBASE.md",
    "migration/FINAL_SETUP_BRIEF.md", "migration/FINALIZATION_CHECKLIST.md",
    "migration/FINALIZATION_LOG.md", "migration/FINAL_VALIDATION.md",
    "migration/LEGACY_FINALIZATION_CHECKLIST_82.md", "migration/PORTING_CHECKLIST.md",
    "migration/PRUNE_PLAN.md", "migration/PRUNE_REPORT.md", "migration/RESUME.md",
    "migration/MIGRATION_PROGRESS.md", "migration/SKILL_MIGRATION.md",
}


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
        if re.search(r"(?im)^\s*(?:node|npm|npx|bash|sh|java|javac|dotnet)\s+(?:tools|scripts|npm|node)", body):
            errors.append(f"{relative}: agent skills must use Python tool entrypoints")
        if re.search(r"(?im)^\s*python3?\s+(?!scripts/python_env\.py\b)(?:-m\s+(?:tools|scripts)\.|(?:tools|scripts)/)", body):
            errors.append(f"{relative}: agent Python commands must use scripts/python_env.py")
        for link in _relative_links(body):
            target = _resolve_reference(path, root, link)
            if not target.exists():
                errors.append(f"{relative}: broken skill link {link}")
        for referenced in re.findall(r"`((?:\./)?(?:scripts|references|assets)/[^`]+)`", body):
            target = _resolve_reference(path, root, referenced.removeprefix("./"))
            if not target.exists():
                errors.append(f"{relative}: missing referenced skill resource {referenced}")
    return errors


def _validate_python_tool_surface(root: Path) -> list[str]:
    errors: list[str] = []
    retired = {"package.json", "package-lock.json", ".node-version"}
    for name in retired:
        if (root / name).exists():
            errors.append(f"retired non-Python runtime file remains active: {name}")
    for folder in (root / "tools", root / "scripts"):
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if path.suffix.casefold() in {".js", ".sh", ".java", ".bat", ".ps1"}:
                errors.append(f"non-Python agent tool remains active: {relative}")
    try:
        environment = yaml.safe_load((root / "environment.yml").read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"invalid Conda environment manifest: {exc}"]
    if not isinstance(environment, dict) or environment.get("name") != "skyrim-ae-research":
        errors.append("environment.yml must define the skyrim-ae-research Conda environment")
    workflow = root / ".github/workflows/ci.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        if re.search(r"setup-node|npm ci|npm test|node --test", text, re.I):
            errors.append("CI must run Python-only research validation")
    return errors


def _validate_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    archived_dirs = (
        "references/upstream/", "migration/legacy_experiments/",
        "migration/archived_tools/",
    )
    generated_dirs = {".git", ".local", "node_modules", "build", "dist"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".mdx"}:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in ARCHIVED_MARKDOWN or relative.startswith(archived_dirs):
            continue
        if any(part in generated_dirs for part in path.relative_to(root).parts):
            continue
        try:
            markdown = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{relative}: cannot read Markdown: {exc}")
            continue
        markdown = re.sub(r"```.*?```|~~~.*?~~~", "", markdown, flags=re.S)
        for target in _relative_links(markdown):
            resolved = _resolve_reference(path, root, target)
            if not resolved.exists():
                errors.append(f"{relative}: broken internal link {target}")
    return errors


def _validate_checklist(root: Path) -> list[str]:
    prompt_path = root / "session-brief/LOCAL_CODEX_FINAL_AUDIT_PROMPT.md"
    json_path = root / "migration/local_setup_checklist.json"
    markdown_path = root / "migration/LOCAL_SETUP_CHECKLIST.md"
    missing = [p.relative_to(root).as_posix() for p in (prompt_path, json_path, markdown_path) if not p.is_file()]
    if missing:
        return [f"current 86-item audit files missing: {', '.join(missing)}"]
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        errors = validate_setup_checklist(data)
        expected = parse_setup_prompt()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot validate current setup checklist: {exc}"]
    rows = data.get("criteria", [])
    if [(x.get("id"), x.get("criterion")) for x in rows] != [
        (x["id"], x["criterion"]) for x in expected
    ]:
        errors.append("86-item checklist IDs/wording/order differ from the authoritative session prompt")
    rendered = CHECKLIST_ROW.findall(markdown_path.read_text(encoding="utf-8"))
    if len(rendered) != 86:
        errors.append(f"rendered setup checklist must contain 86 complete rows; found {len(rendered)}")
    elif [(x[0], x[1]) for x in rendered] != [(x["id"], x["status"]) for x in rows]:
        errors.append("rendered checklist IDs/statuses do not match the JSON source of truth")
    for row in rows:
        if row.get("status") in {"PASS", "BLOCKED_EXTERNAL", "FAIL", "NOT_APPLICABLE"} and not str(row.get("evidence", "")).strip():
            errors.append(f"{row.get('id')}: terminal status requires criterion-specific evidence")
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

    errors.extend(_validate_skills(root))
    errors.extend(_validate_python_tool_surface(root))
    errors.extend(_validate_markdown_links(root))
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
