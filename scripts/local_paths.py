#!/usr/bin/env python3
"""Inspect the single ignored config/local.env binding without revealing paths."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PureWindowsPath
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config  # noqa: E402


def _native_path(value: str) -> Path | None:
    """Map a configured Windows drive path to its WSL mount for read-only checks."""
    if not value:
        return None
    win = PureWindowsPath(value)
    if os.name != "nt" and win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        return Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    return Path(value).expanduser()


def _configured_path(config: dict[str, str], key: str, root: Path) -> Path | None:
    candidate = _native_path(config.get(key, "").strip())
    if candidate is None:
        return None
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate


def _exists(config: dict[str, str], key: str, root: Path, *, directory: bool | None = None) -> bool:
    candidate = _configured_path(config, key, root)
    if candidate is None:
        return False
    if directory is True:
        return candidate.is_dir()
    if directory is False:
        return candidate.is_file()
    return candidate.exists()


def doctor(root: Path = ROOT, *, verify_target: bool = False) -> dict[str, object]:
    """Report configured/existing local bindings; never opens a native project."""
    config = read_local_config(root)
    project_rep_path = _configured_path(config, "GHIDRA_PROJECT_REP_PATH", root)
    project_files = bool(
        project_rep_path
        and project_rep_path.suffix.casefold() == ".rep"
        and project_rep_path.is_dir()
        and project_rep_path.with_suffix(".gpr").is_file()
    )
    java_home = _configured_path(config, "JAVA_HOME", root)
    java_bin = next((java_home / "bin" / name for name in ("java.exe", "java")
                     if java_home and (java_home / "bin" / name).is_file()), None)
    path_keys = (
        "GAME_ROOT", "SKYRIM_EXE_PATH", "SKYRIM_DATA", "SSEEDIT_EXE",
        "LEGACY_SKYRIM_REPO", "GHIDRA_HEADLESS_EXE", "GHIDRA_PROJECT_REP_PATH",
        "GHIDRA_ANALYSIS_EXE_GOG", "JAVA_HOME", "COMMONLIBSSE_ROOT",
        "ADDRESS_LIBRARY_DIR", "MO2_PROFILE_DIR", "PLUGINS_TXT",
        "SKYRIM_TEST_PROFILE_DIR", "SKYRIM_TEST_PLUGINS_TXT", "RESEARCH_TEST_SAVE",
        "SKYRIM_OBSERVER_STAGED_DLL", "SKYRIM_OBSERVER_DEPLOYED_DLL",
        "SKYRIM_OBSERVER_LOG_DIR", "SKYRIM_CONFIG_DIR", "PAPYRUS_LOG_DIR",
        "SKSE_CRASH_DIR", "UESP_DUMP_PATH", "UESP_INDEX_PATH",
        "APOCRYPHA_EXPORT_PATH", "APOCRYPHA_INDEX_PATH",
    )

    target: dict[str, object] = {"verified": False, "full_order_verified": False}
    if verify_target:
        try:
            from tools.ae_target import assert_ae_target, preflight

            verified = assert_ae_target(config, root=root)
            target = {"verified": True, "runtime": verified["version"], "full_order_verified": False}
            try:
                order = preflight(config, root=root)
                target["full_order_verified"] = True
                target["active_plugins"] = order["active_plugins"]
            except (OSError, ValueError, UnicodeError) as exc:
                target["order_error"] = str(exc)
        except (OSError, ValueError, UnicodeError) as exc:
            target = {"verified": False, "full_order_verified": False, "error": str(exc)}

    return {
        "canonical_registry": "config/local.env",
        "local_env_present": (root / "config" / "local.env").is_file(),
        "configured_binding_count": sum(bool(config.get(key, "").strip()) for key in path_keys),
        "legacy_toml_registry_read": False,
        "runtime_steam_executable_exists": _exists(config, "SKYRIM_EXE_PATH", root, directory=False),
        "runtime_data_dir_exists": _exists(config, "SKYRIM_DATA", root, directory=True),
        "sseedit_executable_exists": _exists(config, "SSEEDIT_EXE", root, directory=False),
        "xedit_bridge_entrypoint_exists": bool(
            _configured_path(config, "LEGACY_SKYRIM_REPO", root)
            and (_configured_path(config, "LEGACY_SKYRIM_REPO", root) / "scripts" / "skyrim_tool.py").is_file()
        ),
        "xedit_export_script_exists": bool(
            _configured_path(config, "LEGACY_SKYRIM_REPO", root)
            and (_configured_path(config, "LEGACY_SKYRIM_REPO", root) / "scripts" / "xedit" / "export-records.pas").is_file()
        ),
        "explicit_plugins_txt_configured_exists": _exists(config, "PLUGINS_TXT", root, directory=False),
        "mo2_profile_dir_configured_exists": _exists(config, "MO2_PROFILE_DIR", root, directory=True),
        "test_profile_configured_exists": _exists(config, "SKYRIM_TEST_PROFILE_DIR", root, directory=True),
        "test_plugins_txt_configured_exists": _exists(config, "SKYRIM_TEST_PLUGINS_TXT", root, directory=False),
        "test_save_configured_exists": _exists(config, "RESEARCH_TEST_SAVE", root, directory=False),
        "observer_staged_dll_exists": _exists(config, "SKYRIM_OBSERVER_STAGED_DLL", root, directory=False),
        "observer_deployed_dll_exists": _exists(config, "SKYRIM_OBSERVER_DEPLOYED_DLL", root, directory=False),
        "observer_log_dir_exists": _exists(config, "SKYRIM_OBSERVER_LOG_DIR", root, directory=True),
        "papyrus_log_dir_exists": _exists(config, "PAPYRUS_LOG_DIR", root, directory=True),
        "legacy_research_repo_exists": _exists(config, "LEGACY_SKYRIM_REPO", root, directory=True),
        "ghidra_headless_exists": _exists(config, "GHIDRA_HEADLESS_EXE", root, directory=False),
        "existing_ghidra_project_files_present": project_files,
        "gog_analysis_executable_exists": _exists(config, "GHIDRA_ANALYSIS_EXE_GOG", root, directory=False),
        "java_home_executable_exists": bool(java_bin and java_bin.is_file()),
        "commonlibsse_source_exists": _exists(config, "COMMONLIBSSE_ROOT", root, directory=True),
        "address_library_dir_exists": _exists(config, "ADDRESS_LIBRARY_DIR", root, directory=True),
        "uesp_index_exists": _exists(config, "UESP_INDEX_PATH", root, directory=False),
        "apocrypha_index_exists": _exists(config, "APOCRYPHA_INDEX_PATH", root, directory=False),
        "product_version_verified": target["verified"],
        "runtime": target.get("runtime"),
        "target_error": target.get("error"),
        "full_active_order_verified": target["full_order_verified"],
        "active_order_error": target.get("order_error"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    doctor_parser = subs.add_parser("doctor", help="report configured path readiness without printing path values")
    doctor_parser.add_argument("--verify-target", action="store_true",
                               help="read runtime ProductVersion and attempt full active-order validation")
    args = parser.parse_args(argv)
    if args.command != "doctor":
        parser.error("only the canonical local.env doctor is supported; bind paths in config/local.env")
    try:
        print(json.dumps(doctor(verify_target=args.verify_target), indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
