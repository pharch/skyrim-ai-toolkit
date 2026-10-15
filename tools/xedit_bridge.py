#!/usr/bin/env python3
"""Route the installed read-only SSEEdit helper from canonical local bindings.

`file-records` is a plugin-file parser. `prepare` creates a view-only SSEView
session. Neither command performs a native xEdit record export.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BRIDGE_COPY = Path(".local/xedit-authoritative-copy")
SOURCE_FILES = (
    "scripts/skyrim_tool.py",
    "scripts/run-xedit.ps1",
    "scripts/xedit-status.ps1",
    "scripts/xedit-export-hotkey.ps1",
    "scripts/xedit/README.md",
    "scripts/xedit/export-records.pas",
    "scripts/xedit/investigation-export.pas",
    "scripts/xedit/investigation-references.pas",
)
OFFICIAL_PLUGINS = (
    "Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm",
)


class BridgeError(ValueError):
    """The configured authoritative bridge cannot be safely staged."""


def _same_path(left: str, right: str) -> bool:
    return left.replace("/", "\\").rstrip("\\").casefold() == right.replace("/", "\\").rstrip("\\").casefold()


def helper_config(config: dict[str, str]) -> dict[str, str]:
    """Map the toolkit's canonical names to the legacy helper's local schema."""
    canonical_exe = config.get("SKYRIM_EXE_PATH", "").strip()
    legacy_exe = config.get("SKYRIM_EXE", "").strip()
    if canonical_exe and legacy_exe and not _same_path(canonical_exe, legacy_exe):
        raise BridgeError("SKYRIM_EXE conflicts with canonical SKYRIM_EXE_PATH")
    values = {
        "SSEEDIT_EXE": config.get("SSEEDIT_EXE", "").strip(),
        "SKYRIM_DATA": config.get("SKYRIM_DATA", "").strip(),
        "XEDIT_SCRIPTS": config.get("XEDIT_SCRIPTS", "").strip(),
        "SKYRIM_EXE": canonical_exe or legacy_exe,
        "INCLUDE_CREATION_CLUB": config.get("INCLUDE_CREATION_CLUB", "0").strip() or "0",
    }
    missing = [key for key in ("SSEEDIT_EXE", "SKYRIM_DATA", "XEDIT_SCRIPTS", "SKYRIM_EXE") if not values[key]]
    if missing:
        raise BridgeError("missing xEdit bindings in config/local.env: " + ", ".join(missing))
    if values["INCLUDE_CREATION_CLUB"] not in {"0", "1"}:
        raise BridgeError("INCLUDE_CREATION_CLUB must be 0 or 1")
    if any('"' in value or "\n" in value or "\r" in value for value in values.values()):
        raise BridgeError("xEdit bindings contain a quote or newline unsupported by the bridge config")
    return values


def render_helper_config(values: dict[str, str]) -> str:
    lines = [
        "# Generated from the toolkit's ignored config/local.env by tools/xedit_bridge.py.",
        "# Do not edit this derived file; change the toolkit's canonical local.env.",
    ]
    lines.extend(f'{key}="{value}"' for key, value in values.items())
    return "\n".join(lines) + "\n"


def materialize(root: Path = ROOT, config: dict[str, str] | None = None) -> tuple[Path, dict[str, str]]:
    """Stage verified helper files under ignored .local without touching source."""
    from scripts.local_config import read_local_config
    from tools.ae_target import _native_path

    values = read_local_config(root) if config is None else config
    source_value = values.get("LEGACY_SKYRIM_REPO", "").strip()
    if not source_value:
        raise BridgeError("set LEGACY_SKYRIM_REPO to the read-only authoritative helper checkout")
    source = _native_path(source_value).resolve()
    if not source.is_dir():
        raise BridgeError("configured LEGACY_SKYRIM_REPO is not accessible")
    translated = helper_config(values)
    destination = root / BRIDGE_COPY
    destination.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for relative in SOURCE_FILES:
        source_file = source / relative
        if not source_file.is_file():
            raise BridgeError(f"authoritative bridge file is missing: {relative}")
        content = source_file.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            target.write_bytes(content)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise BridgeError(f"staged bridge file hash mismatch: {relative}")
        hashes[relative] = digest
    private_config = destination / "config" / "local.env"
    private_config.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_helper_config(translated)
    private_config.write_text(rendered, encoding="utf-8")
    return destination, hashes


def _capture_dir(root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    path = root / ".local" / "alignment" / "xedit-bridge" / stamp
    path.mkdir(parents=True, exist_ok=False)
    return path


def _captured_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def invoke_helper(
    bridge: Path,
    command: list[str],
    *,
    root: Path = ROOT,
    timeout: int = 120,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    capture = _capture_dir(root)
    try:
        result = subprocess.run(
            [sys.executable, str(bridge / "scripts" / "skyrim_tool.py"), *command],
            cwd=bridge, text=True, capture_output=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        (capture / "stdout.raw").write_text(_captured_text(exc.stdout), encoding="utf-8", errors="replace")
        (capture / "stderr.raw").write_text(_captured_text(exc.stderr), encoding="utf-8", errors="replace")
        raise BridgeError(f"helper timed out after {timeout} seconds; raw output is retained under {capture.relative_to(root)}") from exc
    (capture / "stdout.raw").write_text(result.stdout, encoding="utf-8")
    (capture / "stderr.raw").write_text(result.stderr, encoding="utf-8")
    return result, capture


def _safe_result(command: str, result: subprocess.CompletedProcess[str], capture: Path, hashes: dict[str, str]) -> dict[str, object]:
    summary: dict[str, object] = {
        "command": command,
        "exit_code": result.returncode,
        "source_files_sha256": hashes,
        "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest(),
        "raw_output": str(capture.relative_to(ROOT)),
    }
    return summary


def _doctor(root: Path, bridge: Path, hashes: dict[str, str]) -> dict[str, object]:
    result, capture = invoke_helper(bridge, ["doctor"], root=root)
    summary = _safe_result("doctor", result, capture, hashes)
    try:
        raw = json.loads(result.stdout)
        summary["configured_inputs_exist"] = all(item.get("exists", False) for item in raw.values())
        summary["input_count"] = len(raw)
        summary["file_record_query_is_native_xedit"] = False
        summary["native_export_interface"] = "SSEView selection plus Apply Script; exporter not validated in this host"
    except (json.JSONDecodeError, AttributeError):
        summary["configured_inputs_exist"] = False
        summary["output_parse"] = "invalid helper doctor JSON"
    return summary


def _prepare(root: Path, bridge: Path, hashes: dict[str, str]) -> dict[str, object]:
    result, capture = invoke_helper(bridge, ["prepare-xedit"], root=root)
    summary = _safe_result("prepare", result, capture, hashes)
    if result.returncode != 0:
        summary["prepared"] = False
        return summary
    session = Path(result.stdout.strip().splitlines()[-1]).resolve()
    allowed = (bridge / "out" / "xedit").resolve()
    if allowed not in session.parents:
        raise BridgeError("helper returned a session outside its isolated xEdit output directory")
    manifest = json.loads((session / "manifest.json").read_text(encoding="utf-8"))
    summary.update({
        "prepared": True,
        "session": str(session.relative_to(root)),
        "manifest_sha256": hashlib.sha256((session / "manifest.json").read_bytes()).hexdigest(),
        "export_script_sha256": hashlib.sha256((session / "export-records.pas").read_bytes()).hexdigest(),
        "plugins": manifest.get("plugins", []),
        "mode": manifest.get("mode"),
        "native_launch_requested": False,
        "record_query_completed": False,
    })
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor", help="sync the configured helper into ignored .local and check bindings")
    subs.add_parser("prepare", help="prepare a scoped five-master SSEView -view session; does not launch it")
    records = subs.add_parser("file-records", help="read records directly from plugin bytes; this does not invoke xEdit")
    records.add_argument("--signature", required=True)
    records.add_argument("--editor-id", help="case-insensitive substring")
    records.add_argument("--form-id", help="plugin-local 6-digit object ID")
    records.add_argument("--plugin", action="append", choices=OFFICIAL_PLUGINS)
    args = parser.parse_args(argv)
    try:
        bridge, hashes = materialize()
        if args.command == "doctor":
            summary = _doctor(ROOT, bridge, hashes)
        elif args.command == "prepare":
            summary = _prepare(ROOT, bridge, hashes)
        else:
            command = ["records", "--signature", args.signature]
            if args.editor_id:
                command.extend(("--editor-id", args.editor_id))
            if args.form_id:
                command.extend(("--form-id", args.form_id))
            for plugin in args.plugin or []:
                command.extend(("--plugin", plugin))
            result, capture = invoke_helper(bridge, command)
            summary = _safe_result("file-records", result, capture, hashes)
            summary["query_route"] = "direct read-only TES4 file parser; not xEdit"
            if result.stdout:
                summary["record_count"] = sum(1 for line in result.stdout.splitlines() if line.strip())
                summary["records_jsonl"] = result.stdout
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0 if summary.get("exit_code") == 0 and summary.get("configured_inputs_exist", True) else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
