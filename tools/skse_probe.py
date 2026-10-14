#!/usr/bin/env python3
"""Read-only identity check for installed SKSE and Address Library files.

This verifies local file versions/hashes and runtime-named filenames only. It
does not load SKSE, attach to Skyrim, or prove that a plugin ran in-game.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config  # noqa: E402
from tools.ae_target import _native_path, assert_ae_target, read_executable_version  # noqa: E402


def _file_info(path: Path, version_reader: Callable[[str | Path], str]) -> dict[str, object]:
    if not path.is_file():
        return {"filename": path.name, "present": False}
    data = path.read_bytes()
    result: dict[str, object] = {
        "filename": path.name,
        "present": True,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    if path.suffix.lower() in {".exe", ".dll"}:
        try:
            result["product_version"] = version_reader(path)
        except (OSError, RuntimeError, ValueError) as exc:
            result["product_version"] = None
            result["version_error"] = type(exc).__name__
    return result


def inspect_install(
    game_root: Path,
    data_dir: Path,
    runtime: str,
    *,
    version_reader: Callable[[str | Path], str] = read_executable_version,
) -> dict[str, object]:
    version_parts = runtime.split(".")[:3]
    if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
        raise ValueError("verified target runtime must have major.minor.build form")
    runtime_tag = "_".join(version_parts)
    address_tag = "-".join(version_parts)
    loader = _file_info(game_root / "skse64_loader.exe", version_reader)
    runtime_dll = _file_info(game_root / f"skse64_{runtime_tag}.dll", version_reader)
    address_library = _file_info(
        data_dir / "SKSE" / "Plugins" / f"versionlib-{address_tag}-0.bin",
        version_reader,
    )
    present = all(bool(item["present"]) for item in (loader, runtime_dll, address_library))
    versions_read = bool(loader.get("product_version") and runtime_dll.get("product_version"))
    return {
        "edition": "AE",
        "runtime": runtime,
        "skse_loader": loader,
        "runtime_dll": runtime_dll,
        "address_library": address_library,
        "runtime_filename_match": bool(runtime_dll["present"] and address_library["present"]),
        "metadata_only": True,
        "live_handshake_attempted": False,
        "versions_read": versions_read,
        "status": "matching_runtime_files_present" if present and versions_read else "incomplete_or_unreadable",
    }


def probe(root: Path = ROOT, *, version_reader=read_executable_version) -> dict[str, object]:
    target = assert_ae_target(root=root)
    config = read_local_config(root)
    game_value = config.get("GAME_ROOT", "")
    data_value = config.get("SKYRIM_DATA", "")
    if not game_value or not data_value:
        raise ValueError("GAME_ROOT and SKYRIM_DATA must be configured")
    result = inspect_install(
        _native_path(game_value), _native_path(data_value), target["version"],
        version_reader=version_reader,
    )
    result["executable_sha256"] = hashlib.sha256(Path(target["executable"]).read_bytes()).hexdigest()
    return result


def main() -> int:
    try:
        result = probe()
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "matching_runtime_files_present" else 1


if __name__ == "__main__":
    raise SystemExit(main())
