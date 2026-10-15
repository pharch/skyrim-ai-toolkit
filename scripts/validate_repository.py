#!/usr/bin/env python3
"""Validate the permanent Skyrim AE research repository policy."""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from scripts.validate_research import validate as validate_research
except ImportError:
    from validate_research import validate as validate_research

REQUIRED = (
    "AGENTS.md", "NORTH_STAR.md", "README.md", "STATE.md", "ROADMAP.md",
    "research/FRONTIER.json", "research/EVIDENCE.json", "research/CLAIMS.md",
    "research/MECHANISMS.md", "research/CONTRADICTIONS.md",
    "research/KNOWLEDGE_GRAPH.md", "research/SESSION_LOG.md",
    "research/RECOVERY.json", "research/LEGACY_IMPORT.md",
    "research/LEGACY_SOURCE_PROVENANCE.tsv", "protocols/TOOL_ROUTING.md",
    "protocols/LIVE_GAME.md", "docs/LOCAL_RUNTIME_CONTRACT.md",
    "docs/HARNESS_READINESS.md", "docs/RESEARCH_START_PROMPT.md",
    "docs/WEEK_LONG_OPERATION.md", "scripts/bootstrap_python.py",
    "scripts/python_env.py", "scripts/research_state.py",
    "scripts/harness_doctor.py", "tools/ghidra_probe.py",
    "tools/xedit_bridge.py", "tools/skse_probe.py",
    "bounties/BOUNTY-0001-LEVEL1-P0.md",
)
SKILL_KEYS = {
    "name", "description", "argument-hint", "user-invocable",
    "disable-model-invocation", "license", "compatibility", "metadata",
}
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
SKIP_DIRS = {".git", ".local", ".venv", ".pytest_cache", "__pycache__", "node_modules", "build", "dist"}


def _links(text: str):
    for target in LINK_RE.findall(text):
        parsed = urlparse(target)
        if not parsed.scheme and not target.startswith("#"):
            yield target


def _resolve(path: Path, root: Path, target: str) -> Path:
    cleaned = target.split("#", 1)[0]
    candidates = ((path.parent / cleaned).resolve(), (root / cleaned).resolve())
    return next((item for item in candidates if item.exists()), candidates[0])


def _validate_skills(root: Path) -> list[str]:
    errors: list[str] = []
    paths = sorted((root / ".agents/skills").glob("*/SKILL.md"))
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
            errors.append(f"{relative}: invalid skill name")
        elif name != path.parent.name or name in names:
            errors.append(f"{relative}: skill name mismatch or duplicate")
        else:
            names.add(name)
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{relative}: description must be non-empty text of at most 1024 characters")
        for key in ("user-invocable", "disable-model-invocation"):
            if key in metadata and not isinstance(metadata[key], bool):
                errors.append(f"{relative}: {key} must be a boolean")
        if "paths" in metadata:
            errors.append(f"{relative}: unsupported provider-specific paths metadata")
        body = text[match.end():]
        if re.search(r"(?im)^\s*(?:node|npm|npx|bash|sh|java|javac|dotnet)\s+(?:tools|scripts|npm|node)", body):
            errors.append(f"{relative}: invoke retained tools through the documented Python entrypoints")
        if re.search(r"(?im)^\s*python3?\s+(?!scripts/python_env\.py\b)(?:-m\s+(?:tools|scripts)\.|(?:tools|scripts)/)", body):
            errors.append(f"{relative}: research Python commands must use scripts/python_env.py")
        for link in _links(body):
            if not _resolve(path, root, link).exists():
                errors.append(f"{relative}: broken skill link {link}")
        for target in re.findall(r"`((?:\./)?(?:scripts|references|assets)/[^`]+)`", body):
            if not _resolve(path, root, target.removeprefix("./")).exists():
                errors.append(f"{relative}: missing referenced skill resource {target}")
    return errors


def _validate_python_tool_surface(root: Path) -> list[str]:
    errors: list[str] = []
    for name in ("package.json", "package-lock.json", ".node-version"):
        if (root / name).exists():
            errors.append(f"unsupported active non-Python runtime file: {name}")
    for folder in (root / "tools", root / "scripts"):
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.casefold() not in {".js", ".sh", ".java", ".bat", ".ps1"}:
                continue
            relative = path.relative_to(root).as_posix()
            if relative == "tools/ghidra_scripts/ReadOnlyTargetedQuery.java":
                if "extends ghidra.app.script.GhidraScript" in path.read_text(encoding="utf-8"):
                    continue
            errors.append(f"non-Python agent tool remains active: {relative}")
    try:
        from scripts.python_env import pinned_distributions
        requirements = pinned_distributions(root / "requirements.txt")
    except (OSError, ValueError) as exc:
        return [f"invalid canonical pinned requirements: {exc}"]
    if "PyYAML" not in requirements:
        errors.append("requirements.txt must pin PyYAML for skill metadata validation")
    return errors


def _validate_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    for directory, child_dirs, filenames in __import__("os").walk(root, topdown=True):
        child_dirs[:] = sorted(name for name in child_dirs if name not in SKIP_DIRS)
        for filename in filenames:
            path = Path(directory) / filename
            if path.suffix.casefold() not in {".md", ".mdx"}:
                continue
            relative = path.relative_to(root).as_posix()
            try:
                text = re.sub(r"```.*?```|~~~.*?~~~", "", path.read_text(encoding="utf-8"), flags=re.S)
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"{relative}: cannot read Markdown: {exc}")
                continue
            for target in _links(text):
                resolved = _resolve(path, root, target)
                if not resolved.exists():
                    errors.append(f"{relative}: broken internal link {target}")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors = [f"missing {name}" for name in REQUIRED if not (root / name).is_file()]
    for retired in ("migration", "session-brief", "references/upstream", "KNOWLEDGEBASE.md", "CHANGELOG.md", "CLAUDE.md", ".claude"):
        if (root / retired).exists():
            errors.append(f"retired setup or mod-authoring material remains: {retired}")
    config = root / ".codex/config.toml"
    try:
        data = tomllib.loads(config.read_text(encoding="utf-8"))
        if data.get("approval_policy") != "on-request" or data.get("sandbox_mode") != "workspace-write":
            errors.append("Codex policy must retain on-request approvals and workspace-write sandbox")
        if "mcp_servers" in data or data.get("features", {}).get("hooks") is True:
            errors.append("shared Codex config must not enable live MCP servers or provider hooks")
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
            errors.append("typed runtime version must not substitute for executable detection")
    errors.extend(_validate_skills(root))
    errors.extend(_validate_python_tool_surface(root))
    errors.extend(_validate_markdown_links(root))
    errors.extend(validate_research(root))
    return errors


def main() -> int:
    errors = validate()
    print("SKYRIM AE RESEARCH REPOSITORY " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print(f" - {error}")
    if not errors:
        print("Permanent research policy, skills, Markdown links, Python tool surface, and evidence state validate.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
