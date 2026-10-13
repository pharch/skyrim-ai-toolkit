#!/usr/bin/env python3
"""Research-checkout safety helpers; these are safeguards, not a shell sandbox."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
import ntpath

ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = ROOT / ".research-backups"
PROTECTED_SUFFIXES = {".esp", ".esm", ".esl", ".bsa", ".ba2", ".ess", ".skse"}
SNAPSHOT_SUFFIXES = {
    ".md", ".json", ".toml", ".py", ".sh", ".psc", ".txt", ".yaml", ".yml",
}


def _local_config() -> dict[str, str]:
    values: dict[str, str] = {}
    path = ROOT / "config" / "local.env"
    if path.is_file():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")
    for key in ("GAME_ROOT", "SKYRIM_CONFIG_DIR"):
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values


def _is_windows_path(value: str) -> bool:
    path = PureWindowsPath(value)
    return bool(path.drive) or value.startswith("\\\\")


def _normalized(value: str) -> str:
    if _is_windows_path(value):
        return ntpath.normcase(ntpath.normpath(value.replace("/", "\\"))).rstrip("\\")
    return str(Path(value).expanduser().resolve(strict=False))


def _within(path: str, root: str) -> bool:
    target, parent = _normalized(path), _normalized(root)
    try:
        return ntpath.commonpath([target, parent]) == parent
    except ValueError:
        return False


def _resolved_input_path(value: str) -> str:
    if _is_windows_path(value):
        return value
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return str(candidate.resolve(strict=False))


def _is_game_shaped_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return bool(
        re.search(r"(?:^|/)Documents/My Games/Skyrim(?:[^/]*)?(?:/|$)", normalized, re.I)
        or re.search(r"(?:^|/)Data/(?:SKSE|Scripts|Meshes|Textures|Sound|Video)(?:/|$)", normalized, re.I)
    )


def check_write(value: str, roots: list[str]) -> str | None:
    path = _resolved_input_path(value)
    suffix = Path(PureWindowsPath(value).name).suffix.lower() if _is_windows_path(value) else Path(value).suffix.lower()
    if suffix in PROTECTED_SUFFIXES:
        return f"refusing direct write to protected Skyrim binary/save format ({suffix})"
    if any(_within(path, root) for root in roots if root):
        return "refusing writes inside the configured Skyrim game or configuration directory"
    if _is_game_shaped_path(value):
        return "refusing a game-data/config-shaped path; configure and verify the exact local path first"
    return None


def _safe_snapshot_source(value: str) -> Path:
    candidate = ROOT / value
    if candidate.is_symlink():
        raise ValueError(f"snapshot source must not be a symlink: {value}")
    source = candidate.resolve(strict=True)
    if not source.is_relative_to(ROOT):
        raise ValueError(f"snapshot source is outside this checkout: {value}")
    if not source.is_file() or source.is_symlink():
        raise ValueError(f"snapshot source must be a regular, non-symlink file: {value}")
    if source.suffix.lower() not in SNAPSHOT_SUFFIXES:
        raise ValueError(f"unsupported snapshot file type: {value}")
    if source.is_relative_to(BACKUP_ROOT):
        raise ValueError(f"refusing to snapshot an existing backup: {value}")
    return source


def preflight() -> int:
    checks: list[tuple[bool, str]] = []
    checks.append((ROOT.is_dir() and (ROOT / ".git").exists(), "repository checkout"))

    try:
        import tomllib
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        checks.append((
            config.get("approval_policy") == "on-request"
            and config.get("sandbox_mode") == "workspace-write",
            "Codex requires on-request approvals and workspace-write sandbox",
        ))
    except (OSError, ValueError) as exc:
        checks.append((False, f"Codex configuration parses: {exc}"))

    settings_path = ROOT / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            hooks_disabled = settings.get("hooks", {}) == {}
            checks.append((hooks_disabled, "legacy Claude hooks are not registered"))
        except (OSError, json.JSONDecodeError) as exc:
            checks.append((False, f"legacy Claude settings parse: {exc}"))

    values = _local_config()
    game_root = values.get("GAME_ROOT", "").strip()
    if game_root:
        outside = not _within(str(ROOT), game_root)
        checks.append((outside, "research checkout is outside configured GAME_ROOT"))
        if not outside:
            print("Live/game paths must not be used from this checkout.", file=sys.stderr)
    else:
        print("Live-game lane: disabled (GAME_ROOT is not configured).")

    for okay, label in checks:
        print(f"{'PASS' if okay else 'FAIL'} {label}")
    failures = sum(not okay for okay, _ in checks)
    if failures:
        print(f"Preflight failed: {failures} check(s).", file=sys.stderr)
        return 1
    print("Preflight passed. This does not authorize live-game or save mutation.")
    return 0


def snapshot(values: list[str]) -> int:
    if not values:
        print("Provide one or more checkout-relative text files to snapshot.", file=sys.stderr)
        return 2
    sources = [_safe_snapshot_source(value) for value in values]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    destination = BACKUP_ROOT / stamp
    destination.mkdir(parents=True, exist_ok=False)
    entries = []
    try:
        for source in sources:
            relative = source.relative_to(ROOT)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            entries.append({
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            })
        (destination / "MANIFEST.json").write_text(
            json.dumps({"created_at": stamp, "files": entries}, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception:
        shutil.rmtree(destination)
        raise
    print(f"Snapshotted {len(entries)} file(s) to {destination.relative_to(ROOT)}")
    for entry in entries:
        print(f"  {entry['path']} sha256={entry['sha256']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preflight", help="check Codex settings and configured checkout boundary")
    check = commands.add_parser("check-write", help="reject protected game/save write targets")
    check.add_argument("paths", nargs="+")
    snap = commands.add_parser("snapshot", help="copy checkout text files to a timestamped backup")
    snap.add_argument("paths", nargs="+")
    args = parser.parse_args()

    if args.command == "preflight":
        return preflight()
    if args.command == "snapshot":
        return snapshot(args.paths)

    values = _local_config()
    roots = [values.get("GAME_ROOT", ""), values.get("SKYRIM_CONFIG_DIR", "")]
    failures = 0
    for value in args.paths:
        reason = check_write(value, roots)
        if reason:
            print(f"DENY {value}: {reason}", file=sys.stderr)
            failures += 1
        else:
            print(f"PASS {value}: not in a known protected boundary")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
