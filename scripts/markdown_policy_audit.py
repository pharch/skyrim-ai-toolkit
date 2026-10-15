#!/usr/bin/env python3
"""Inventory Markdown and audit active local links and retired workflows."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "migration" / "ACTIVE_MARKDOWN_AUDIT.md"
EXCEPTIONS = ROOT / "migration" / "markdown-audit-exceptions.json"
SKIP_DIRS = {".git", ".local", ".venv", "node_modules", "__pycache__"}
# The machine-local handoff must not leak its path/hash. Mutable recovery
# checkpoints are validated by research-state tooling; omit them from this
# static inventory so every required next-action update does not stale it.
SKIP_FILES = {
    "config/LOCAL_TOOL_HANDOFF.private.md",
    "STATE.md",
    "research/SESSION_LOG.md",
}
ACTIVE_MIGRATION = {
    "migration/LOCAL_RESEARCH_READINESS_MISSION.md",
    "migration/LOCAL_READINESS_CHECKLIST.md",
    "migration/LOCAL_READINESS_REPORT.md",
    "migration/LOCAL_READINESS_BLOCKERS.md",
    "migration/LOCAL_READINESS_RESUME.md",
    "migration/LOCAL_READINESS_CHANGES.md",
    "migration/TOOL_CAPABILITY_MATRIX.md",
    "migration/TOOL_PATH_VERIFICATION.md",
    "migration/FINAL_ALIGNMENT_CHECKLIST.md",
    "migration/FINAL_ALIGNMENT_REPORT.md",
    "migration/FINAL_ALIGNMENT_RESUME.md",
    "migration/FINAL_ALIGNMENT_CHANGES.md",
    "migration/KNOWLEDGE_IMPORT_AUDIT.md",
    "migration/LANGUAGE_AUDIT.md",
    "migration/CONTINUITY_PILOT.md",
    "migration/ACTIVE_MARKDOWN_AUDIT.md",
    "migration/ARCHIVE_INDEX.md",
}
RETIRED_PATTERNS = {
    "timed_or_game_root_launcher": re.compile(r"(?:45[- ]minute|research_supervisor\.py|\bsetup\.sh\b)", re.I),
    "legacy_agent_control": re.compile(r"(?:\.claude/|\bClaude(?:\.md)?\b)", re.I),
    "non_ae_workflow": re.compile(r"(?:Skyrim\s*VR|SkyrimVR\.exe|Legendary Edition|Skyrim LE)", re.I),
}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def markdown_files(root: Path = ROOT) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if relative.as_posix() in SKIP_FILES:
            continue
        found.append(path)
    return sorted(found, key=lambda path: path.relative_to(root).as_posix().casefold())


def classification(relative: str) -> tuple[str, str]:
    parts = Path(relative).parts
    if relative in {"KNOWLEDGEBASE.md", "CHANGELOG.md"} or relative.startswith("references/upstream/"):
        return "ARCHIVAL", "Retained source; explicitly non-authoritative under AGENTS.md."
    if parts and parts[0] == "migration":
        if relative in ACTIVE_MIGRATION:
            return "ACTIVE", "Current readiness/audit record; reviewed for policy and links."
        return "ARCHIVAL", "Prior migration artifact; retained for provenance, not active instructions."
    if parts and parts[0] == "bounties":
        return "ACTIVE", "User-provided review packet; context only, not current-session evidence or research instructions."
    if parts and parts[0] in {"docs", "protocols", "research", ".agents", "config", "experiments", "tools"}:
        return "ACTIVE", "Current research guidance or evidence record; reviewed for policy and links."
    if len(parts) == 1:
        return "ACTIVE", "Current repository-level instruction or status document."
    if parts and parts[0] in {"session-brief", ".github"}:
        return "ARCHIVAL", "Retained historical or workflow source; not a primary instruction path."
    return "UNCLASSIFIED", "Requires explicit active/archive disposition."


def _exceptions() -> dict[str, list[dict[str, str]]]:
    if not EXCEPTIONS.is_file():
        return {}
    data = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
    return data.get("exceptions", {})


def _is_excepted(relative: str, rule: str, line: str, exceptions: dict[str, list[dict[str, str]]]) -> bool:
    for entry in exceptions.get(relative, []):
        if entry.get("rule") != rule or not entry.get("reason", "").strip():
            continue
        try:
            if re.search(entry.get("line_regex", r"."), line):
                return True
        except re.error:
            continue
    return False


def audit(root: Path = ROOT) -> tuple[list[str], list[tuple[str, str, str, str]]]:
    errors: list[str] = []
    rows: list[tuple[str, str, str, str]] = []
    exceptions = _exceptions()
    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        status, disposition = classification(relative)
        if status == "UNCLASSIFIED":
            errors.append(f"{relative}: missing active/archive disposition")
        if relative == INVENTORY.relative_to(root).as_posix():
            digest = "generated; self hash omitted"
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((relative, status, digest, disposition))
        if status != "ACTIVE" or relative == INVENTORY.relative_to(root).as_posix():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for rule, pattern in RETIRED_PATTERNS.items():
                if pattern.search(line) and not _is_excepted(relative, rule, line, exceptions):
                    errors.append(f"{relative}:{number}: retired-workflow pattern {rule}")
            for match in LINK_RE.finditer(line):
                destination = match.group(1).strip().split()[0].strip("<>")
                if not destination or destination.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                local = unquote(destination.split("#", 1)[0].split("?", 1)[0])
                if not local:
                    continue
                target = (path.parent / local).resolve()
                try:
                    target.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"{relative}:{number}: link escapes repository")
                    continue
                if not target.exists():
                    errors.append(f"{relative}:{number}: broken local link {local}")
    return errors, rows


def render(rows: list[tuple[str, str, str, str]]) -> str:
    active = sum(row[1] == "ACTIVE" for row in rows)
    archival = sum(row[1] == "ARCHIVAL" for row in rows)
    lines = [
        "# Active Markdown and provenance inventory",
        "",
        "Generated by scripts/markdown_policy_audit.py. Active files are checked",
        "for local link targets and retired launcher/agent/non-AE workflows;",
        "archival files remain preserved and are excluded from active instructions.",
        "Hashes identify source snapshots, not Git commits.",
        "",
        f"Inventory: {len(rows)} Markdown files; {active} active; {archival} archival.",
        "",
        "| Path | Class | SHA256 | Disposition |",
        "|---|---|---|---|",
    ]
    for path, status, digest, disposition in rows:
        lines.append(f"| `{path}` | {status} | `{digest}` | {disposition} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write a refreshed inventory after auditing")
    mode.add_argument("--check", action="store_true", help="verify the inventory is current without writing")
    args = parser.parse_args(argv)
    try:
        errors, rows = audit()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Markdown audit failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    rendered = render(rows)
    if args.write:
        INVENTORY.write_text(rendered, encoding="utf-8")
    elif not INVENTORY.is_file() or INVENTORY.read_text(encoding="utf-8") != rendered:
        errors.append("migration/ACTIVE_MARKDOWN_AUDIT.md: stale; rerun with --write")
    print(f"Markdown inventory: {len(rows)} files; {sum(row[1] == 'ACTIVE' for row in rows)} active; {sum(row[1] == 'ARCHIVAL' for row in rows)} archival")
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
