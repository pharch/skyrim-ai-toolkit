#!/usr/bin/env python3
"""Sync and check machine-local research paths without printing their values."""
from __future__ import annotations

import argparse
import json
import ntpath
import os
from pathlib import Path, PureWindowsPath
import shutil
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config  # noqa: E402


def _read_registry(root: Path) -> dict:
    path = root / ".local" / "research-paths.toml"
    if not path.is_file():
        raise FileNotFoundError("ignored local path registry is missing")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _registry_values(registry: dict) -> dict[str, str]:
    paths = registry.get("configured_paths", {})
    target = registry.get("target", {})
    private = registry.get("private_sources", {})
    exe = str(paths.get("skyrim_exe") or "")
    values = {
        "SKYRIM_EDITION": "AE",
        "GAME_ROOT": ntpath.dirname(exe) if exe else "",
        "SKYRIM_EXE_PATH": exe,
        "SKYRIM_DATA": str(paths.get("skyrim_data") or ""),
        "SSEEDIT_EXE": str(paths.get("sseedit_exe") or ""),
        "GHIDRA_HOME": str(paths.get("ghidra_home") or ""),
        "GHIDRA_HEADLESS": str(paths.get("ghidra_headless") or ""),
        "GHIDRA_PROJECTS": str(paths.get("ghidra_projects") or ""),
        "JAVA_HOME": str(paths.get("java_home") or ""),
        "COMMONLIBSSE_NG": str(paths.get("commonlibsse_ng") or ""),
        "ADDRESS_LIBRARY_DIR": str(paths.get("address_library_dir") or ""),
        "VCPKG_ROOT": str(paths.get("vcpkg_root") or ""),
        "UESP_DUMP_PATH": str(target.get("raw_uesp_dump") or ""),
        "UESP_INDEX_PATH": ".local/uesp.sqlite3",
        "APOCRYPHA_EXPORT_PATH": str(private.get("apocrypha_json") or ""),
        "APOCRYPHA_INDEX_PATH": ".local/apocrypha.sqlite3",
    }
    return {key: value for key, value in values.items() if value}


def sync(root: Path = ROOT, *, overwrite: bool = False) -> dict[str, int]:
    registry = _read_registry(root)
    template = root / "config" / "local.env.example"
    config = root / "config" / "local.env"
    if not config.exists():
        if not template.is_file():
            raise FileNotFoundError("tracked local.env template is missing")
        config.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(template, config)
        if os.name != "nt":
            config.chmod(0o600)
    values = _registry_values(registry)
    current_lines = config.read_text(encoding="utf-8-sig").splitlines()
    existing: dict[str, str] = {}
    for line in current_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, value = stripped.split("=", 1)
            existing[key.strip()] = value.strip().strip("\"'")
    output: list[str] = []
    seen: set[str] = set()
    filled = 0
    for line in current_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                seen.add(key)
                old = existing.get(key, "")
                new = values[key] if overwrite or not old else old
                if new != old:
                    filled += 1
                output.append(f"{key}='{new}'" if new else f"{key}=")
                continue
        output.append(line)
    for key, value in values.items():
        if key not in seen:
            output.append(f"{key}='{value}'")
            filled += 1
    config.write_text("\n".join(output) + "\n", encoding="utf-8")
    return {"registry_values": len(values), "updated_values": filled, "active_plugins_txt_configured": bool(existing.get("PLUGINS_TXT", "").strip())}


def _native_path(value: str) -> Path | None:
    if not value:
        return None
    win = PureWindowsPath(value)
    if win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        drive = win.drive[0].lower()
        return Path("/mnt") / drive / Path(*win.parts[1:])
    return Path(value).expanduser()


def doctor(root: Path = ROOT, *, verify_target: bool = False) -> dict[str, object]:
    try:
        registry = _read_registry(root)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        registry = {}
    config = read_local_config(root)
    values = _registry_values(registry) if registry else {}
    candidates = [value for key, value in values.items() if key not in {"SKYRIM_EDITION", "UESP_INDEX_PATH", "APOCRYPHA_INDEX_PATH"}]
    existing = sum(bool((_native_path(value) or Path("/nonexistent")).exists()) for value in candidates)
    exe = _native_path(config.get("SKYRIM_EXE_PATH", ""))
    plugins = _native_path(config.get("PLUGINS_TXT", ""))
    target: dict[str, object] = {"verified": False}
    if verify_target:
        try:
            from tools.ae_target import assert_ae_target

            verified = assert_ae_target(root=root)
            target = {"verified": True, "runtime": verified["version"]}
        except (OSError, ValueError, UnicodeError) as exc:
            target = {"verified": False, "error": str(exc)}
    return {
        "registry_present": bool(registry),
        "local_env_present": (root / "config" / "local.env").is_file(),
        "candidate_path_count": len(candidates),
        "existing_candidate_path_count": existing,
        "configured_executable_exists": bool(exe and exe.is_file()),
        "active_plugins_txt_configured": bool(config.get("PLUGINS_TXT", "").strip()),
        "active_plugins_txt_exists": bool(plugins and plugins.is_file()),
        "product_version_verified": target["verified"],
        "runtime": target.get("runtime"),
        "target_error": target.get("error"),
        "complete_active_order_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    sync_parser = subs.add_parser("sync", help="fill empty ignored local.env values from the local registry")
    sync_parser.add_argument("--overwrite", action="store_true", help="replace existing nonempty local values")
    subs.add_parser("doctor", help="report local path readiness without printing path values")
    args = parser.parse_args(argv)
    try:
        result = sync(overwrite=args.overwrite) if args.command == "sync" else doctor(verify_target=True)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
