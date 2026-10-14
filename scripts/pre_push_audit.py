#!/usr/bin/env python3
"""Check that local research inputs and raw/heavy artifacts cannot enter Git."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HEAVY_LIMIT = 5 * 1024 * 1024
RAW_SUFFIXES = {".log", ".jsonl", ".ndjson", ".etl", ".dmp", ".crash", ".trace", ".dump", ".ess", ".skse", ".skseco", ".sqlite", ".sqlite3", ".db", ".xml", ".bz2", ".gz", ".zip", ".7z", ".rar", ".tar", ".xz"}
IGNORE_PROBES = (
    "config/local.env",
    "session_prompt.md",
    ".local/probe.sqlite3",
    ".local/probe.xml.bz2",
    "research/raw-private/probe.log",
    "logs/probe.log",
    "exports/discord-export.json",
    "exports/wiki-export.txt",
    "research/raw-private/capture.ndjson",
    "uespwiki-probe.xml.bz2",
    "local-investigation.tar.gz",
)


def _git(root: Path, *args: str) -> list[str]:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    return [entry.decode("utf-8", "surrogateescape") for entry in result.stdout.split(b"\0") if entry]


def _is_ignored(root: Path, path: str) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", "--no-index", "--", path], cwd=root).returncode == 0


def _is_raw_candidate(relative: str) -> bool:
    path = Path(relative)
    parts = {part.casefold() for part in path.parts}
    name = path.name.casefold()
    if path.suffix.casefold() in RAW_SUFFIXES or parts.intersection({"raw", "raw-private", "exports", "captures", "dumps", "logs"}):
        return True
    if any(service in name for service in ("discord", "apocrypha")) and any(token in name for token in ("export", "chat", "archive")):
        return True
    if any(token in name for token in ("uesp", "wiki")) and any(token in name for token in ("export", "dump", "current")):
        return True
    return False


def audit(root: Path = ROOT) -> dict[str, object]:
    tracked = _git(root, "ls-files", "-z")
    tracked_raw = [p for p in tracked if _is_raw_candidate(p)]
    tracked_heavy = []
    for relative in tracked:
        path = root / relative
        try:
            if path.is_file() and path.stat().st_size >= HEAVY_LIMIT:
                tracked_heavy.append(relative)
        except OSError:
            tracked_heavy.append(relative)
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    untracked_raw = [p for p in untracked if _is_raw_candidate(p)]
    probe_results = {path: _is_ignored(root, path) for path in IGNORE_PROBES}

    local_heavy = []
    local_root = root / ".local"
    if local_root.is_dir():
        for path in local_root.rglob("*"):
            if path.is_file():
                try:
                    if path.stat().st_size >= HEAVY_LIMIT:
                        local_heavy.append(path)
                except OSError:
                    local_heavy.append(path)
    local_types = {"sqlite_database": 0, "compressed_source_archive": 0, "other": 0}
    for path in local_heavy:
        if path.suffix.casefold() in {".sqlite", ".sqlite3", ".db"}:
            local_types["sqlite_database"] += 1
        elif path.suffix.casefold() in {".bz2", ".gz", ".xz", ".zip", ".7z"}:
            local_types["compressed_source_archive"] += 1
        else:
            local_types["other"] += 1
    local_bytes = sum(path.stat().st_size for path in local_heavy if path.exists())
    return {
        "tracked_file_count": len(tracked),
        "tracked_raw_artifact_count": len(tracked_raw),
        "tracked_heavy_file_count": len(tracked_heavy),
        "unignored_untracked_raw_artifact_count": len(untracked_raw),
        "ignore_probes": probe_results,
        "ignored_local_heavy_file_count": len(local_heavy),
        "ignored_local_heavy_size_mib": round(local_bytes / (1024 * 1024), 1),
        "ignored_local_heavy_types": local_types,
        "pass": not tracked_raw and not tracked_heavy and not untracked_raw and all(probe_results.values()),
    }


def main() -> int:
    try:
        result = audit()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    except (OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"pass": False, "error": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
