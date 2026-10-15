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
from scripts.python_env import environment_dir, environment_status, execution_host  # noqa: E402
from tools.ae_target import TargetError, assert_ae_target  # noqa: E402


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
    ghidra_headless = _path(config.get("GHIDRA_HEADLESS_EXE", ""))
    ghidra_project_rep = _path(config.get("GHIDRA_PROJECT_REP_PATH", ""))
    ghidra_program = config.get("GHIDRA_PROJECT_PROGRAM", "").strip()
    gog_exe = _path(config.get("GHIDRA_ANALYSIS_EXE_GOG", ""))
    commonlib = _path(config.get("COMMONLIBSSE_ROOT", ""))
    xedit = _path(config.get("SSEEDIT_EXE", ""))
    java_home = _path(config.get("JAVA_HOME", ""))
    java_bin = next((java_home / "bin" / name for name in ("java.exe", "java")
                     if java_home and (java_home / "bin" / name).is_file()), None)
    wsl_java_home = _path(config.get("GHIDRA_JAVA_HOME_WSL", ""))
    wsl_java_bin = wsl_java_home / "bin" / "java" if wsl_java_home else None
    project_present = bool(ghidra_project_rep
                           and ghidra_project_rep.suffix.casefold() == ".rep"
                           and ghidra_project_rep.is_dir()
                           and ghidra_project_rep.with_suffix(".gpr").is_file())
    offsets_header = commonlib / "include" / "RE" / "Offsets.h" if commonlib else None
    gog_data_plugins = gog_exe.parent / "Data" / "SKSE" / "Plugins" if gog_exe else None
    gog_address_library_present = bool(gog_data_plugins and list(gog_data_plugins.glob("versionlib-*.bin")))
    return {
        "ae_executable_configured_exists": bool(exe and exe.is_file()),
        "game_root_configured_exists": bool(game_root and game_root.is_dir()),
        "explicit_plugins_txt_configured_exists": bool(plugins and plugins.is_file()),
        "ghidra_headless_configured_exists": bool(ghidra_headless and ghidra_headless.is_file()),
        "ghidra_project_present": project_present,
        "ghidra_project_program_configured": ghidra_program.casefold() == "skyrimse.exe",
        "gog_analysis_executable_exists": bool(gog_exe and gog_exe.is_file()),
        "gog_address_library_candidate_exists": gog_address_library_present,
        "commonlibsse_source_configured_exists": bool(commonlib and commonlib.is_dir()),
        "commonlibsse_cmake_project_present": bool(commonlib and (commonlib / "CMakeLists.txt").is_file()),
        "commonlibsse_offsets_header_present": bool(offsets_header and offsets_header.is_file()),
        "sseedit_executable_configured_exists": bool(xedit and xedit.is_file()),
        "java_home_configured_exists": bool(java_bin and java_bin.is_file()),
        "ghidra_wsl_java_executable_exists": bool(wsl_java_bin and wsl_java_bin.is_file()),
    }


def _windows_command(command: str, *, timeout: int = 30) -> dict[str, object]:
    """Run a fixed, read-only host query through Windows interop without a shell file."""
    executable = shutil.which("cmd.exe") or shutil.which("cmd")
    if not executable and os.name != "nt":
        candidate = Path("/mnt/c/Windows/System32/cmd.exe")
        if candidate.is_file():
            executable = str(candidate)
    if not executable:
        return {"available": False, "reason": "Windows command bridge not found"}
    try:
        result = subprocess.run(
            [executable, "/d", "/s", "/c", command],
            capture_output=True, text=False, timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "reason": type(exc).__name__}
    output = (result.stdout + b"\n" + result.stderr).decode("utf-8", errors="replace").strip()
    return {"available": result.returncode == 0, "exit_code": result.returncode, "output": output[:1200]}


def _host_java() -> dict[str, object]:
    result = _windows_command("java.exe -version")
    output = str(result.get("output", ""))
    version_line = next((line.strip() for line in output.splitlines() if "version" in line.lower()), "")
    return {
        "available": result.get("available", False),
        "version_line": version_line,
        "bridge_reason": result.get("reason"),
    }


def _verified_target(config: dict[str, str], root: Path) -> dict[str, object]:
    try:
        target = assert_ae_target(config, root=root)
        return {"verified": True, "edition": target["edition"], "runtime": target["version"]}
    except (TargetError, OSError, UnicodeError) as exc:
        return {"verified": False, "error": str(exc)}


def _sseedit_status(config: dict[str, str], paths: dict[str, object], target: dict[str, object]) -> dict[str, object]:
    """Report xEdit file/profile availability without conflating it with runtime identity."""
    executable_exists = bool(paths["sseedit_executable_configured_exists"])
    return {
        "status": "configured_executable_profile_unverified" if executable_exists else "blocked_external",
        "configured_executable_exists": executable_exists,
        "windows_host": os.name == "nt",
        "runtime_target": {
            "product_version_verified": bool(target.get("verified")),
            "version": target.get("runtime"),
            "error": target.get("error"),
        },
        # A configured file path is only a candidate. Target preflight must
        # parse and validate the entire current profile before this is true.
        "full_active_order_verified": False,
        "explicit_plugins_txt_candidate_exists": bool(paths["explicit_plugins_txt_configured_exists"]),
        "selected_mo2_profile_configured": bool(_path(config.get("MO2_PROFILE_DIR", ""))),
        "xedit_call": False,
        "python_fallback": "python3 scripts/python_env.py run tools/plugin_reader.py",
    }


def run_doctor(root: Path = ROOT) -> dict[str, object]:
    config = read_local_config(root)
    paths = _tool_paths(config)
    java = _host_java()
    target = _verified_target(config, root)
    reports: dict[str, object] = {}

    # A synthetic fixture proves the parser returns a complete, machine-readable
    # response without touching a user's save or co-save.
    try:
        skse = _synthetic_cosave_response()
        reports["SKSE"] = {"status": "python_parser_responds", **skse,
                           "live_bridge": "not attempted; requires verified Windows AE target and a running game"}
    except Exception as exc:  # a concise doctor should still report later domains
        reports["SKSE"] = {"status": "technical_failure", "error": type(exc).__name__}

    ghidra_ready = bool(paths["ghidra_headless_configured_exists"]
                        and paths["ghidra_project_present"]
                        and paths["gog_analysis_executable_exists"])
    ghidra_meta = sorted((root / ".local" / "ghidra").glob("gog-query-*.meta.json"))
    reports["Ghidra"] = {
        "status": "existing_gog_project_bound" if ghidra_ready else "blocked_external",
        "analysis_distribution": "GOG",
        "project_alias": "config/local.env:GHIDRA_PROJECT_REP_PATH",
        "project_program_configured": paths["ghidra_project_program_configured"],
        "existing_project_files_present": paths["ghidra_project_present"],
        "analysis_executable_present": paths["gog_analysis_executable_exists"],
        "configured_headless_path_exists": paths["ghidra_headless_configured_exists"],
        "java_home_executable_exists": paths["java_home_configured_exists"],
        "wsl_java_home_executable_exists": paths["ghidra_wsl_java_executable_exists"],
        "host_java": java,
        "read_only_query_metadata_count": len(ghidra_meta),
        "query_command": "python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]",
        "query_mode": "existing project; -process -noanalysis -readOnly; no import or overwrite",
    }

    cmake = _windows_command("cmake.exe --version")

    reports["CommonLibSSE"] = {
        "status": "source_and_header_present" if paths["commonlibsse_source_configured_exists"] and paths["commonlibsse_offsets_header_present"] else "blocked_external",
        "source_candidate_present": bool(paths["commonlibsse_source_configured_exists"]),
        "source_directory_exists": paths["commonlibsse_source_configured_exists"],
        "cmake_project_present": paths["commonlibsse_cmake_project_present"],
        "offsets_header_present": paths["commonlibsse_offsets_header_present"],
        "matching_gog_address_library_candidate_present": paths["gog_address_library_candidate_exists"],
        "address_library_probe_command": "python3 scripts/python_env.py run tools/address_library_probe.py --symbol Namespace::Name",
        "cmake_available": bool(shutil.which("cmake") or cmake["available"]),
        "host_cmake_probe": {key: cmake[key] for key in cmake if key != "output"},
        "native_compiler_available": any(shutil.which(command) for command in ("cl", "clang++", "g++")),
        "new_build_run": False,
    }

    reports["SSEEdit"] = _sseedit_status(config, paths, target)

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
        "product_version_verified": target["verified"],
        "runtime": target.get("runtime"),
        "target_error": target.get("error"),
        "full_active_order_configured": paths["explicit_plugins_txt_configured_exists"],
        "preflight_command": "python3 scripts/python_env.py run tools/ae_preflight.py",
        "live_or_xedit_calls_permitted": False,
    }
    python_status = environment_status(root)
    reports["python_environment"] = {
        "status": "verified_persistent_venv" if python_status.get("ready") else "needs_bootstrap_or_repair",
        "execution_host": execution_host(),
        "environment_path": environment_dir(root).relative_to(root).as_posix(),
        "python_required": python_status.get("python_required"),
        "python_version": python_status.get("python_version"),
        "strict_environment_ready": bool(python_status.get("ready")),
        "requirements_source": "requirements.txt",
        "pinned_distribution_count": len(python_status.get("required_distributions", {})),
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
