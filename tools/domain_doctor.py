#!/usr/bin/env python3
"""Run bounded, read-only readiness probes for the six requested research domains."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config  # noqa: E402
from scripts.local_paths import _native_path  # noqa: E402
from tools.ae_target import TargetError, read_executable_version  # noqa: E402


def _path(value: str) -> Path | None:
    if not value:
        return None
    return _native_path(value)


def _synthetic_cosave_response() -> dict[str, object]:
    spec = importlib.util.spec_from_file_location("cosave_info", ROOT / "tools/cosave-info.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the Python co-save parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = bytes(200)
    header = b"SKSE" + struct.pack("<IIIIIII", 1, 0x02000600, 0x01040F00, 0, 0, 0, 0)
    fixture = header + b"ATAD" + struct.pack("<II", 1, len(payload)) + payload
    with tempfile.NamedTemporaryFile(suffix=".skse") as stream:
        stream.write(fixture)
        stream.flush()
        response = module.survey(stream.name)
    return {"response_ok": bool(response.get("ok")), "chunk_count": response.get("chunkCount"),
            "coverage_pct": response.get("coveragePct"), "fixture_only": True}


def _tool_paths(config: dict[str, str]) -> dict[str, object]:
    def status(key: str) -> bool:
        candidate = _path(config.get(key, ""))
        return bool(candidate and candidate.exists())

    exe = _path(config.get("SKYRIM_EXE_PATH", ""))
    game_root = _path(config.get("GAME_ROOT", ""))
    plugins = _path(config.get("PLUGINS_TXT", ""))
    ghidra_home = _path(config.get("GHIDRA_HOME", ""))
    ghidra_headless = _path(config.get("GHIDRA_HEADLESS", ""))
    commonlib = _path(config.get("COMMONLIBSSE_NG", ""))
    xedit = _path(config.get("SSEEDIT_EXE", ""))
    java_home = _path(config.get("JAVA_HOME", ""))
    java_bin = (java_home / "bin" / ("java.exe" if os.name == "nt" else "java")) if java_home else None
    ghidra_launchers = [
        ghidra_home / "support" / ("analyzeHeadless.bat" if os.name == "nt" else "analyzeHeadless")
    ] if ghidra_home else []
    return {
        "ae_executable_configured_exists": bool(exe and exe.is_file()),
        "game_root_configured_exists": bool(game_root and game_root.is_dir()),
        "explicit_plugins_txt_configured_exists": bool(plugins and plugins.is_file()),
        "ghidra_home_configured_exists": bool(ghidra_home and ghidra_home.is_dir()),
        "ghidra_headless_configured_exists": bool(ghidra_headless and ghidra_headless.exists()),
        "ghidra_standard_launcher_exists": any(p.is_file() for p in ghidra_launchers),
        "commonlibsse_source_configured_exists": bool(commonlib and commonlib.is_dir()),
        "commonlibsse_cmake_project_present": bool(commonlib and (commonlib / "CMakeLists.txt").is_file()),
        "sseedit_executable_configured_exists": bool(xedit and xedit.is_file()),
        "java_home_configured_exists": bool(java_bin and java_bin.is_file()),
    }


def run_doctor(root: Path = ROOT) -> dict[str, object]:
    config = read_local_config(root)
    paths = _tool_paths(config)
    reports: dict[str, object] = {}

    # A synthetic fixture proves the parser returns a complete, machine-readable
    # response without touching a user's save or co-save.
    try:
        skse = _synthetic_cosave_response()
        reports["SKSE"] = {"status": "python_parser_responds", **skse,
                           "live_bridge": "not attempted; requires verified Windows AE target and a running game"}
    except Exception as exc:  # a concise doctor should still report later domains
        reports["SKSE"] = {"status": "technical_failure", "error": type(exc).__name__}

    ghidra_ready = bool(paths["ghidra_standard_launcher_exists"] and paths["java_home_configured_exists"])
    reports["Ghidra"] = {
        "status": "configured_toolchain_present" if ghidra_ready else "blocked_external",
        "configured_home_exists": paths["ghidra_home_configured_exists"],
        "configured_headless_path_exists": paths["ghidra_headless_configured_exists"],
        "standard_launcher_exists": paths["ghidra_standard_launcher_exists"],
        "java_home_executable_exists": paths["java_home_configured_exists"],
        "path_invocation_available": bool(shutil.which("analyzeHeadless") or shutil.which("ghidraRun")),
        "analysis_run": False,
    }

    reports["CommonLibSSE"] = {
        "status": "ready_to_build" if paths["commonlibsse_source_configured_exists"] and shutil.which("cmake") else "blocked_external",
        "source_candidate_present": bool(paths["commonlibsse_source_configured_exists"]),
        "source_directory_exists": paths["commonlibsse_source_configured_exists"],
        "cmake_project_present": paths["commonlibsse_cmake_project_present"],
        "cmake_available": bool(shutil.which("cmake")),
        "native_compiler_available": any(shutil.which(command) for command in ("cl", "clang++", "g++")),
        "build_run": False,
    }

    reports["SSEEdit"] = {
        "status": "configured_executable_present_but_unverified" if paths["sseedit_executable_configured_exists"] else "blocked_external",
        "configured_executable_exists": paths["sseedit_executable_configured_exists"],
        "windows_host": os.name == "nt",
        "product_version_verified": False,
        # A configured file path is only a candidate. Target preflight must
        # parse and validate the entire current profile before this is true.
        "full_active_order_verified": False,
        "explicit_plugins_txt_candidate_exists": bool(paths["explicit_plugins_txt_configured_exists"]),
        "xedit_call": False,
        "python_fallback": "python3 scripts/python_env.py run tools/plugin_reader.py",
    }

    try:
        from tools.uesp.core import doctor as uesp_doctor, page as uesp_page, search as uesp_search

        database = root / ".local" / "uesp.sqlite3"
        if not database.is_file():
            raise FileNotFoundError
        metadata = uesp_doctor(database)
        sample = uesp_page(database, "Skyrim:Karstaag", raw=True)
        matches = uesp_search(database, "Karstaag", namespace="Skyrim", limit=3)
        reports["UESP"] = {
            "status": "usable_local_database",
            "page_count": metadata.get("total_pages"),
            "skyrim_namespace_pages": metadata.get("skyrim_namespace_pages"),
            "fts_rows": metadata.get("fts_rows"),
            "sample_page_found": True,
            "sample_revision_id": sample.get("revision_id"),
            "sample_content_characters": len(str(sample.get("content", ""))),
            "search_response_count": len(matches),
            "source_completeness": metadata.get("source_completeness"),
        }
    except Exception as exc:
        reports["UESP"] = {"status": "unavailable_or_error", "error": type(exc).__name__}

    try:
        from tools.apocrypha.core import doctor as apocrypha_doctor, search as apocrypha_search

        database = root / ".local" / "apocrypha.sqlite3"
        if not database.is_file():
            raise FileNotFoundError
        metadata = apocrypha_doctor(database)
        # Search executes locally; discard every returned private identifier and
        # report only the aggregate count to prove the query path responds.
        matches = apocrypha_search(database, "level", limit=3, summary_only=True)
        reports["Apocrypha"] = {
            "status": "usable_private_local_database",
            "message_count": metadata.get("message_count"),
            "declared_message_count": metadata.get("declared_message_count"),
            "fts_rows": metadata.get("fts_rows"),
            "search_response_count": len(matches),
            "private_fields_emitted": False,
            "source_text_is_untrusted": metadata.get("source_text_is_untrusted"),
        }
    except Exception as exc:
        reports["Apocrypha"] = {"status": "unavailable_or_error", "error": type(exc).__name__}

    reports["target_gate"] = {
        "executable_candidate_exists": paths["ae_executable_configured_exists"],
        "product_version_verified": False,
        "full_active_order_configured": paths["explicit_plugins_txt_configured_exists"],
        "preflight_command": "python3 scripts/python_env.py run tools/ae_preflight.py",
        "live_or_xedit_calls_permitted": False,
    }
    reports["python_environment"] = {
        "name": "skyrim-ae-research",
        "manifest_present": (root / "environment.yml").is_file(),
        "conda_available": bool(shutil.which("conda")),
        "current_python": ".".join(map(str, sys.version_info[:3])),
    }
    return reports


def main() -> int:
    try:
        print(json.dumps(run_doctor(), indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "doctor_failed", "error": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
