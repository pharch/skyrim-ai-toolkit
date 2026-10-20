#!/usr/bin/env python3
"""Query the existing, configured GOG Skyrim AE Ghidra project read-only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import ntpath
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config  # noqa: E402
from tools.ae_target import (  # noqa: E402
    MIN_AE_VERSION,
    TargetError,
    _native_path,
    compare_version,
    parse_version,
    read_executable_version,
)


class GhidraProbeError(RuntimeError):
    """The configured existing-project query cannot be run safely."""


def _windows_path(path: Path) -> str:
    """Map a mounted WSL path to a Windows path without dropping spaces."""
    resolved = path.resolve()
    if os.name == "nt":
        return str(resolved)
    text = resolved.as_posix()
    match = re.match(r"^/mnt/([a-z])(?:/(.*))?$", text, re.IGNORECASE)
    if not match:
        raise GhidraProbeError("Ghidra paths must resolve under a mounted Windows drive")
    return match.group(1).upper() + ":\\" + (match.group(2) or "").replace("/", "\\")


def _required_path(config: dict[str, str], key: str) -> Path:
    value = config.get(key, "").strip()
    if not value:
        raise GhidraProbeError(
            f"{key} is missing from ignored config/local.env; no Ghidra project will be created"
        )
    return _native_path(value).resolve()


def _normalize_windows_path(value: str) -> str:
    text = value.strip().replace("/", "\\")
    if re.match(r"^\\[A-Za-z]:\\", text):
        text = text[1:]
    return ntpath.normcase(ntpath.normpath(text))


def resolve_binding(config: dict[str, str], *, root: Path = ROOT) -> dict[str, object]:
    """Resolve one local.env binding; never infer a project from the runtime path."""
    required_values = (
        "LEGACY_SKYRIM_REPO",
        "GHIDRA_HEADLESS_EXE",
        "GHIDRA_PROJECT_REP_PATH",
        "GHIDRA_PROJECT_PROGRAM",
        "GHIDRA_ANALYSIS_EXE_GOG",
    )
    missing = [key for key in required_values if not config.get(key, "").strip()]
    if missing:
        raise GhidraProbeError(
            "missing GOG project binding in ignored config/local.env: "
            + ", ".join(missing)
            + "; no import or replacement project will be attempted"
        )

    legacy_repo = _required_path(config, "LEGACY_SKYRIM_REPO")
    headless = _required_path(config, "GHIDRA_HEADLESS_EXE")
    project_rep_path = _required_path(config, "GHIDRA_PROJECT_REP_PATH")
    executable = _required_path(config, "GHIDRA_ANALYSIS_EXE_GOG")
    if project_rep_path.suffix.casefold() != ".rep":
        raise GhidraProbeError("GHIDRA_PROJECT_REP_PATH must identify the existing project's .rep directory")
    project_dir = project_rep_path.parent
    project_name = project_rep_path.stem
    program_name = config["GHIDRA_PROJECT_PROGRAM"].strip()

    if not legacy_repo.is_dir():
        raise GhidraProbeError("configured LEGACY_SKYRIM_REPO is not an accessible directory")
    if not headless.is_file():
        raise GhidraProbeError("configured GHIDRA_HEADLESS_EXE is not an accessible file")
    if program_name.casefold() != "skyrimse.exe":
        raise GhidraProbeError("GHIDRA_PROJECT_PROGRAM must identify the existing AE SkyrimSE.exe")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", project_name):
        raise GhidraProbeError("GHIDRA_PROJECT_REP_PATH basename must be a simple existing project name")
    if not project_dir.is_dir():
        raise GhidraProbeError("configured GHIDRA_PROJECT_REP_PATH parent is missing; no project will be created")
    if not project_rep_path.is_dir():
        raise GhidraProbeError("configured GOG .rep project data directory is missing; no replacement will be created")
    if not project_rep_path.with_suffix(".gpr").is_file():
        raise GhidraProbeError("configured GOG .gpr project is missing; no replacement will be created")
    if not executable.is_file() or executable.name.casefold() != "skyrimse.exe":
        raise GhidraProbeError("configured GOG analysis executable must be an accessible SkyrimSE.exe")

    repository = root.resolve()
    for external_path, key in ((project_rep_path, "GHIDRA_PROJECT_REP_PATH"), (executable, "GHIDRA_ANALYSIS_EXE_GOG")):
        if external_path == repository or repository in external_path.parents:
            raise GhidraProbeError(f"{key} must point to an external local installation/project, not this Git checkout")

    try:
        version_text = read_executable_version(executable)
        version = parse_version(version_text)
    except (TargetError, OSError, UnicodeError) as exc:
        raise GhidraProbeError("could not read ProductVersion from the configured GOG executable") from exc
    if version[0] != 1 or version[1] != 6 or compare_version(version, MIN_AE_VERSION) < 0:
        raise GhidraProbeError("configured GOG analysis executable is not a supported AE 1.6.318+ build")

    digest = hashlib.sha256(executable.read_bytes()).hexdigest()
    return {
        "legacy_repo": legacy_repo,
        "headless": headless,
        "project_dir": project_dir,
        "project_name": project_name,
        "project_rep_path": project_rep_path,
        "program_name": program_name,
        "executable": executable,
        "version": ".".join(map(str, version)),
        "sha256": digest,
    }


def _cmd_executable() -> str:
    candidate = shutil.which("cmd.exe") or shutil.which("cmd")
    if not candidate and os.name != "nt":
        fallback = Path("/mnt/c/Windows/System32/cmd.exe")
        if fallback.is_file():
            candidate = str(fallback)
    if not candidate:
        raise GhidraProbeError("Windows cmd.exe bridge is unavailable")
    return candidate


def _capture_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _is_wsl_windows_mount(path: Path) -> bool:
    """Detect DrvFS/9P paths even when an elevated process reports them writable."""
    return os.name != "nt" and bool(re.match(r"^/mnt/[a-z](?:/|$)", path.resolve().as_posix(), re.IGNORECASE))


def _project_source_manifest(project_dir: Path, project_name: str) -> dict[str, object]:
    """Describe an existing project snapshot without changing its source tree."""
    rep = project_dir / f"{project_name}.rep"
    gpr = project_dir / f"{project_name}.gpr"
    files = []
    for path in sorted((gpr, *rep.rglob("*"))):
        if not path.is_file():
            continue
        stat = path.stat()
        files.append({
            "path": path.relative_to(project_dir).as_posix(),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        })
    if not gpr.is_file() or not rep.is_dir() or not files:
        raise GhidraProbeError("configured GOG Ghidra project cannot be snapshotted")
    return {"source_rep_path": str(rep.resolve()), "files": files}


def _wsl_project_workspace(
    binding: dict[str, object], *, root: Path, config: dict[str, str],
) -> tuple[dict[str, object], str]:
    """Cache a faithful copy for Windows-mounted or read-only WSL project sources."""
    source_dir = Path(binding["project_dir"])
    if os.access(source_dir, os.W_OK) and not _is_wsl_windows_mount(source_dir):
        return binding, "configured_existing_project"

    source_name = str(binding["project_name"])
    source_rep = Path(binding["project_rep_path"])
    source_manifest = _project_source_manifest(source_dir, source_name)
    manifest_payload = json.dumps(source_manifest, sort_keys=True, separators=(",", ":"))
    source_fingerprint = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()

    cache_value = config.get("GHIDRA_PROJECT_CACHE_WSL", "").strip()
    if cache_value:
        cache_root = Path(cache_value).expanduser()
        if not cache_root.is_absolute():
            raise GhidraProbeError("GHIDRA_PROJECT_CACHE_WSL must be an absolute WSL-native path")
        cache_root = cache_root.resolve()
        if Path("/mnt") == cache_root or Path("/mnt") in cache_root.parents:
            raise GhidraProbeError("GHIDRA_PROJECT_CACHE_WSL must be on the WSL-native filesystem, outside /mnt")
        repository = root.resolve()
        if cache_root == repository or repository in cache_root.parents:
            raise GhidraProbeError("GHIDRA_PROJECT_CACHE_WSL must be outside the repository checkout")
    else:
        # A cache under a /mnt-mounted checkout inherits DrvFS/9P locking
        # limitations. Require an explicit, machine-local WSL path there.
        if root.resolve() == Path("/mnt") or Path("/mnt") in root.resolve().parents:
            raise GhidraProbeError(
                "GHIDRA_PROJECT_CACHE_WSL must name an absolute WSL-native path in ignored config/local.env "
                "when the checkout is under /mnt"
            )
        cache_root = (root / ".local" / "ghidra" / "project-cache").resolve()
    cache_rep = cache_root / source_rep.name
    cache_gpr = cache_root / f"{source_name}.gpr"
    cache_manifest_path = cache_root / "source-manifest.json"
    cached_manifest = None
    if cache_manifest_path.is_file():
        try:
            cached_manifest = json.loads(cache_manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached_manifest = None
    cache_matches = bool(
        cached_manifest
        and cached_manifest.get("source_fingerprint") == source_fingerprint
        and cached_manifest.get("source_rep_path") == source_manifest["source_rep_path"]
        and cache_rep.is_dir()
        and cache_gpr.is_file()
    )
    if not cache_matches:
        if cache_root.exists():
            # Delete only a cache carrying our exact ownership marker. Never
            # remove an arbitrary directory at a configured or user path.
            if not cached_manifest or cached_manifest.get("managed_by") != "tools/ghidra_probe.py":
                raise GhidraProbeError(
                    "WSL Ghidra project cache exists without its ownership manifest; inspect it before reuse"
                )
            if cached_manifest.get("source_rep_path") != source_manifest["source_rep_path"]:
                raise GhidraProbeError("WSL Ghidra project cache belongs to a different configured source project")
            shutil.rmtree(cache_root)
        cache_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_rep, cache_rep, symlinks=True)
        shutil.copy2(source_dir / f"{source_name}.gpr", cache_gpr)
        cache_manifest_path.write_text(json.dumps({
            "schema": 1,
            "managed_by": "tools/ghidra_probe.py",
            "source_rep_path": source_manifest["source_rep_path"],
            "source_fingerprint": source_fingerprint,
            "source_file_count": len(source_manifest["files"]),
        }, indent=2) + "\n", encoding="utf-8")

    workspace = dict(binding)
    workspace["project_dir"] = cache_root
    return workspace, "wsl_native_copy_of_configured_existing_project"


def run_query(*, root: Path = ROOT, config: dict[str, str] | None = None, timeout: int = 300,
              rva: int | None = None, vtable_slot: int | None = None,
              vtable_rtti_rvas: list[int] | None = None,
              address_rva: int | None = None,
              pointer_table_rva: int | None = None, pointer_count: int = 0,
              follow_direct_calls: int = 0, follow_incoming_calls: int = 0,
              enumerate_call_edges: bool = False,
              search_string: str | None = None,
              search_displacement: int | None = None) -> dict[str, object]:
    """Run the checked-in query against the configured GOG project in place."""
    if search_string is not None:
        if not re.fullmatch(r"[A-Za-z0-9_.$:]{1,128}", search_string):
            raise GhidraProbeError("--search-string accepts 1-128 ASCII identifier characters only")
        if any((rva is not None, vtable_slot is not None, vtable_rtti_rvas is not None, address_rva is not None, pointer_table_rva is not None,
                pointer_count, follow_direct_calls, follow_incoming_calls, enumerate_call_edges,
                search_displacement is not None)):
            raise GhidraProbeError("--search-string cannot be combined with function or call-trace options")
    if search_displacement is not None:
        if search_displacement < 0 or search_displacement >= 2**63:
            raise GhidraProbeError("--search-displacement must be a non-negative 63-bit integer")
        if any((rva is not None, vtable_slot is not None, vtable_rtti_rvas is not None, address_rva is not None, pointer_table_rva is not None,
                pointer_count, follow_direct_calls, follow_incoming_calls, enumerate_call_edges,
                search_string is not None)):
            raise GhidraProbeError("--search-displacement cannot be combined with other query modes")
    if (pointer_table_rva is None) != (pointer_count == 0):
        raise GhidraProbeError("--pointer-table-rva and --pointer-count must be supplied together")
    if pointer_table_rva is not None and (pointer_table_rva < 0 or pointer_table_rva >= 2**63):
        raise GhidraProbeError("--pointer-table-rva must be a non-negative 63-bit image-relative address")
    if pointer_count < 0 or pointer_count > 128:
        raise GhidraProbeError("--pointer-count must be between 1 and 128")
    if vtable_rtti_rvas is not None:
        if not 1 <= len(vtable_rtti_rvas) <= 32:
            raise GhidraProbeError("--vtable-rtti-rvas must contain 1-32 comma-separated RVAs")
        if any(value < 0 or value >= 2**63 for value in vtable_rtti_rvas):
            raise GhidraProbeError("--vtable-rtti-rvas values must be non-negative 63-bit RVAs")
        if any((rva is not None, vtable_slot is not None, address_rva is not None,
                pointer_table_rva is not None, pointer_count, follow_direct_calls,
                follow_incoming_calls, enumerate_call_edges, search_string is not None,
                search_displacement is not None)):
            raise GhidraProbeError("--vtable-rtti-rvas cannot be combined with other query modes")
    if pointer_table_rva is not None and any((rva is not None, vtable_slot is not None,
            vtable_rtti_rvas is not None, follow_direct_calls, follow_incoming_calls, enumerate_call_edges)):
        raise GhidraProbeError("--pointer-table-rva cannot be combined with function or call-trace options")
    if address_rva is not None and (address_rva < 0 or address_rva >= 2**63):
        raise GhidraProbeError("--address-rva must be a non-negative 63-bit image-relative address")
    if address_rva is not None and any((rva is not None, vtable_slot is not None, vtable_rtti_rvas is not None, pointer_table_rva is not None,
            pointer_count, follow_direct_calls, follow_incoming_calls, enumerate_call_edges)):
        raise GhidraProbeError("--address-rva cannot be combined with function or call-trace options")
    if rva is not None and (rva < 0 or rva >= 2**63):
        raise GhidraProbeError("--rva must be a non-negative 63-bit image-relative address")
    if vtable_slot is not None and rva is None:
        raise GhidraProbeError("--vtable-slot requires --rva with the vtable base RVA")
    if vtable_slot is not None and (vtable_slot < 0 or vtable_slot > 0x10000):
        raise GhidraProbeError("--vtable-slot must be a non-negative slot index no greater than 0x10000")
    if follow_direct_calls < 0 or follow_direct_calls > 8:
        raise GhidraProbeError("--follow-direct-calls must be between 0 and 8")
    if follow_direct_calls and rva is None:
        raise GhidraProbeError("--follow-direct-calls requires --rva")
    if enumerate_call_edges and rva is None:
        raise GhidraProbeError("--list-call-edges requires --rva")
    if follow_incoming_calls < 0 or follow_incoming_calls > 32:
        raise GhidraProbeError("--follow-incoming-calls must be between 0 and 32")
    if follow_incoming_calls and rva is None:
        raise GhidraProbeError("--follow-incoming-calls requires --rva")
    local_env = root / "config" / "local.env"
    if config is None:
        if not local_env.is_file():
            raise GhidraProbeError("ignored config/local.env is missing; copy the portable template and bind local tools")
        config = read_local_config(root)
    binding = resolve_binding(config, root=root)
    workspace = binding
    project_workspace = "configured_existing_project"
    if os.name != "nt":
        workspace, project_workspace = _wsl_project_workspace(binding, root=root, config=config)
    script = root / "tools" / "ghidra_scripts" / "ReadOnlyTargetedQuery.java"
    if not script.is_file():
        raise GhidraProbeError("checked-in read-only Ghidra query script is missing")

    output_dir = root / ".local" / "ghidra"
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"gog-query-{stamp}"
    log = output_dir / f"{stem}.log"
    script_log = output_dir / f"{stem}.script.log"
    stdout_path = output_dir / f"{stem}.stdout.raw"
    stderr_path = output_dir / f"{stem}.stderr.raw"
    metadata_path = output_dir / f"{stem}.meta.json"
    wrapper: Path

    headless = binding["headless"]
    project_dir = workspace["project_dir"]
    project_name = str(binding["project_name"])
    program_name = str(binding["program_name"])
    linux_headless = headless.parent / "analyzeHeadless"
    invocation_env: dict[str, str] | None = None
    if os.name != "nt" and linux_headless.is_file():
        java_home_value = config.get("GHIDRA_JAVA_HOME_WSL", "").strip()
        if java_home_value:
            java_home = _native_path(java_home_value).resolve()
            java = java_home / "bin" / "java"
            if not java_home.is_dir() or not java.is_file():
                raise GhidraProbeError("GHIDRA_JAVA_HOME_WSL must name a WSL Java 21+ home with bin/java")
        else:
            java_value = shutil.which("java")
            if not java_value:
                raise GhidraProbeError(
                    "WSL has the paired Linux analyzeHeadless launcher but no Java 21+ runtime; "
                    "set GHIDRA_JAVA_HOME_WSL in ignored config/local.env"
                )
            java = Path(java_value).resolve()
            java_home = java.parent.parent
        version_probe = subprocess.run(
            [str(java), "-version"], capture_output=True, timeout=20, check=False,
        )
        java_version_text = (version_probe.stderr + version_probe.stdout).decode("utf-8", errors="replace")
        java_version_match = re.search(r'version "(\d+)', java_version_text)
        if version_probe.returncode != 0 or not java_version_match or int(java_version_match.group(1)) < 21:
            raise GhidraProbeError("configured WSL Java runtime must start successfully and be version 21 or newer")
        invocation_env = os.environ.copy()
        invocation_env["JAVA_HOME"] = str(java_home)
        invocation_env["PATH"] = str(java.parent) + os.pathsep + invocation_env.get("PATH", "")
        user_home_value = config.get("GHIDRA_USER_HOME_WSL", ".local/ghidra-runtime/home").strip()
        user_home = _native_path(user_home_value).resolve()
        ignored_root = (root / ".local").resolve()
        if user_home != ignored_root and ignored_root not in user_home.parents:
            raise GhidraProbeError("GHIDRA_USER_HOME_WSL must resolve below this checkout's ignored .local directory")
        user_home.mkdir(parents=True, exist_ok=True)
        # Ghidra's LaunchSupport persists the selected JDK and preferences in
        # user.home. Keep that state beside the local Java runtime so a managed
        # WSL home or XDG setup is not an undocumented prerequisite.
        java_home_option = str(user_home).replace("\\", "\\\\").replace('"', '\\"')
        existing_java_options = invocation_env.get("JAVA_TOOL_OPTIONS", "").strip()
        invocation_env["JAVA_TOOL_OPTIONS"] = " ".join(
            part for part in (existing_java_options, f'-Duser.home="{java_home_option}"') if part
        )
        command_args = [
            str(linux_headless), str(project_dir), project_name,
            "-process", program_name, "-noanalysis", "-readOnly",
            "-scriptPath", str(script.parent), "-log", str(log),
            "-scriptlog", str(script_log), "-postScript", script.name,
        ]
        if rva is not None:
            command_args.append(f"0x{rva:X}")
        if pointer_table_rva is not None:
            command_args.extend((f"pointer-table:0x{pointer_table_rva:X}", f"pointer-count:{pointer_count}"))
        if vtable_rtti_rvas is not None:
            command_args.append("vtable-rtti:" + ",".join(f"0x{value:X}" for value in vtable_rtti_rvas))
        if address_rva is not None:
            command_args.append(f"address:0x{address_rva:X}")
        if vtable_slot is not None:
            command_args.append(f"slot:0x{vtable_slot:X}")
        if follow_direct_calls:
            command_args.append(f"calls:{follow_direct_calls}")
        if follow_incoming_calls:
            command_args.append(f"callers:{follow_incoming_calls}")
        if enumerate_call_edges:
            command_args.append("edges:all")
        if search_string is not None:
            command_args.append(f"string:{search_string}")
        if search_displacement is not None:
            command_args.append(f"offset:0x{search_displacement:X}")
        command = shlex.join(command_args)
        wrapper = output_dir / f"{stem}.sh"
        wrapper.write_text("#!/bin/sh\nexec " + command + "\n", encoding="utf-8")
        wrapper.chmod(wrapper.stat().st_mode | 0o111)
        invocation = command_args
    else:
        command = (
            f'call "{_windows_path(headless)}" "{_windows_path(project_dir)}" "{project_name}" '
            f'-process "{program_name}" -noanalysis -readOnly '
            f'-scriptPath "{_windows_path(script.parent)}" '
            f'-log "{_windows_path(log)}" -scriptlog "{_windows_path(script_log)}" '
            f'-postScript "{script.name}"'
            + (f' 0x{rva:X}' if rva is not None else "")
            + (f' pointer-table:0x{pointer_table_rva:X} pointer-count:{pointer_count}' if pointer_table_rva is not None else "")
            + (" vtable-rtti:" + ",".join(f"0x{value:X}" for value in vtable_rtti_rvas) if vtable_rtti_rvas is not None else "")
            + (f' address:0x{address_rva:X}' if address_rva is not None else "")
            + (f' slot:0x{vtable_slot:X}' if vtable_slot is not None else "")
            + (f' calls:{follow_direct_calls}' if follow_direct_calls else "")
            + (f' callers:{follow_incoming_calls}' if follow_incoming_calls else "")
            + (' edges:all' if enumerate_call_edges else "")
            + (f' string:{search_string}' if search_string is not None else "")
            + (f' offset:0x{search_displacement:X}' if search_displacement is not None else "")
        )
        wrapper = output_dir / f"{stem}.cmd"
        wrapper.write_text("@echo off\r\n" + command + "\r\nexit /b %ERRORLEVEL%\r\n", encoding="utf-8", newline="")
        invocation = [_cmd_executable(), "/d", "/c", _windows_path(wrapper)]

    started = time.monotonic()
    try:
        result = subprocess.run(
            invocation,
            cwd=root,
            env=invocation_env,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GhidraProbeError(f"read-only Ghidra invocation failed: {type(exc).__name__}") from exc
    elapsed = round(time.monotonic() - started, 3)
    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    stdout = result.stdout.decode("utf-8", errors="replace")
    script_error = "ERROR REPORT SCRIPT ERROR" in stdout
    program_path_match = re.search(r"PROGRAM_EXECUTABLE_PATH=([^\r\n]+)", stdout)
    reported_program_path = program_path_match.group(1).split(" (GhidraScript)")[0].strip() if program_path_match else ""
    path_matches = bool(
        reported_program_path
        and _normalize_windows_path(reported_program_path)
        == _normalize_windows_path(_windows_path(binding["executable"]))
    )
    vtable_slot_lookup = (
        vtable_slot is None
        or (f"VTABLE_SLOT_INDEX=0x{vtable_slot:X}" in stdout and "VTABLE_SLOT_TARGET_RVA=" in stdout)
    )
    if vtable_rtti_rvas is not None:
        checks = {
            "program_identity_matches_gog_binary": path_matches,
            "vtable_rtti_census_complete": "VTABLE_RTTI_CENSUS_COMPLETE=true" in stdout,
            "vtable_rtti_entry_count": stdout.count("VTABLE_RTTI_CENSUS_ENTRY=") == len(vtable_rtti_rvas),
            "vtable_rtti_rows_present": stdout.count("VTABLE_RTTI_SUBOBJECT_OFFSET=") == len(vtable_rtti_rvas),
            "script_no_error": not script_error,
        }
    elif address_rva is not None:
        checks = {
            "program_identity_matches_gog_binary": path_matches,
            "address_rva_requested": f"ADDRESS_RVA=0x{address_rva:X}" in stdout,
            "address_in_program_memory": "ADDRESS_MEMORY_CONTAINS=true" in stdout,
            "address_context_complete": "ADDRESS_CONTEXT_COMPLETE=true" in stdout,
            "script_no_error": not script_error,
        }
    elif pointer_table_rva is not None:
        checks = {
            "program_identity_matches_gog_binary": path_matches,
            "pointer_table_requested": f"POINTER_TABLE_REQUESTED_COUNT={pointer_count}" in stdout,
            "pointer_table_scan_complete": "POINTER_TABLE_SCAN_COMPLETE=true" in stdout,
            "pointer_table_xref_scan_complete": "POINTER_TABLE_XREF_SCAN_COMPLETE=true" in stdout,
            "script_no_error": not script_error,
        }
    elif search_string is not None:
        checks = {
            "program_identity_matches_gog_binary": path_matches,
            "requested_string": f"STRING_QUERY={search_string}" in stdout,
            "string_scan_complete": "STRING_SCAN_COMPLETE=true" in stdout,
            "string_reference_scan_complete": "STRING_REFERENCE_SCAN_COMPLETE=true" in stdout,
            "script_no_error": not script_error,
        }
    elif search_displacement is not None:
        checks = {
            "program_identity_matches_gog_binary": path_matches,
            "requested_displacement": f"OFFSET_QUERY=0x{search_displacement:X}" in stdout,
            "displacement_scan_complete": "OFFSET_SCAN_COMPLETE=true" in stdout,
            "visitor_symbol_scan_complete": "OFFSET_VISITOR_SYMBOL_SCAN_COMPLETE=true" in stdout,
            "writer_analysis_complete": "OFFSET_WRITER_ANALYSIS_COMPLETE=true" in stdout,
            "visitor_callee_analysis_complete": "OFFSET_VISITOR_CALLEE_ANALYSIS_COMPLETE=true" in stdout,
            "computed_writer_analysis_complete": "OFFSET_COMPUTED_WRITER_ANALYSIS_COMPLETE=true" in stdout,
            "visitor_method_analysis_complete": "OFFSET_VISITOR_METHOD_ANALYSIS_COMPLETE=true" in stdout,
            "script_no_error": not script_error,
        }
    else:
        checks = {
            "program_identity_matches_gog_binary": path_matches,
            "function_lookup": "FUNCTION_LOOKUP=" in stdout,
            "requested_rva_lookup": rva is None or (
                "VTABLE_BASE_RVA=" in stdout if vtable_slot is not None
                else f"TARGET_RVA=0x{rva:X}" in stdout
            ),
            "vtable_slot_lookup": vtable_slot_lookup,
            "direct_call_trace": follow_direct_calls == 0 or "OUTGOING_CALL_COUNT=" in stdout,
            "incoming_call_trace": follow_incoming_calls == 0 or "INCOMING_CALLER_FUNCTION_COUNT=" in stdout,
            "direct_call_edge_scan": not enumerate_call_edges or "DIRECT_CALL_EDGE_SCAN_COMPLETE=true" in stdout,
            "disassembly": "DISASM=" in stdout and "DISASSEMBLY_INSTRUCTION_COUNT=" in stdout,
            "decompilation": "DECOMPILATION_BEGIN=" in stdout and "DECOMPILATION_END=" in stdout,
            "script_no_error": not script_error,
        }
        if vtable_slot is not None:
            # A virtual target can legitimately have no direct call xref. The
            # table's data reference is the relevant provenance for this query.
            checks["vtable_target_reference"] = (
                "VTABLE_SLOT_TARGET_RVA=" in stdout and "XREF_ANY_COUNT=" in stdout
            )
            checks["vtable_rtti_identity"] = (
                "VTABLE_RTTI_SIGNATURE=0x1" in stdout and "VTABLE_RTTI_TYPE_NAME=" in stdout
            )
        else:
            checks["xref_call_edge"] = (
                "DIRECT_CALL_EDGE_SCAN_COMPLETE=true" in stdout
                if enumerate_call_edges
                else "XREF_CALL_EDGE=" in stdout and "NOT_FOUND_IN_ANALYZED_PROJECT" not in stdout
            )
    script_log_hash = _capture_hash(script_log)
    workspace_rep = project_dir / f"{project_name}.rep"
    try:
        workspace_rep_path = workspace_rep.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        workspace_rep_path = (
            "config/local.env:GHIDRA_PROJECT_REP_PATH"
            if project_workspace == "configured_existing_project"
            else f"config/local.env:GHIDRA_PROJECT_CACHE_WSL/{project_name}.rep"
        )
    meta: dict[str, object] = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "operation": "existing_gog_project_read_only_query",
        "analysis_distribution": "GOG",
        "execution_launcher": "wsl-linux-analyzeHeadless" if invocation_env is not None else "windows-analyzeHeadless",
        "analysis_binary_product_version": binding["version"],
        "analysis_binary_sha256": binding["sha256"],
        "project_alias": "config/local.env:GHIDRA_PROJECT_REP_PATH",
        "project_workspace": project_workspace,
        "project_workspace_rep_path": workspace_rep_path,
        "program": program_name,
        "requested_rva": f"0x{rva:X}" if rva is not None else None,
        "query_mode": "memory_displacement_search" if search_displacement is not None else (
            "vtable_rtti_census" if vtable_rtti_rvas is not None else (
            "address_context_query" if address_rva is not None else (
            "pointer_table_query" if pointer_table_rva is not None else (
            "literal_reference_search" if search_string is not None else (
            "direct_call_edge_census" if enumerate_call_edges else "function_query"
        ))))),
        "requested_string": search_string,
        "requested_search_displacement": f"0x{search_displacement:X}" if search_displacement is not None else None,
        "requested_address_rva": f"0x{address_rva:X}" if address_rva is not None else None,
        "requested_pointer_table_rva": f"0x{pointer_table_rva:X}" if pointer_table_rva is not None else None,
        "requested_pointer_count": pointer_count if pointer_table_rva is not None else None,
        "requested_vtable_rtti_rvas": [f"0x{value:X}" for value in vtable_rtti_rvas] if vtable_rtti_rvas is not None else None,
        "requested_vtable_slot": f"0x{vtable_slot:X}" if vtable_slot is not None else None,
        "follow_direct_calls": follow_direct_calls,
        "follow_incoming_calls": follow_incoming_calls,
        "enumerate_call_edges": enumerate_call_edges,
        "program_executable_path_matches_gog_binary": path_matches,
        "exit_code": result.returncode,
        "elapsed_seconds": elapsed,
        "checks": checks,
        "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
        "script_log_sha256": script_log_hash,
        "adapter_sha256": _capture_hash(Path(__file__).resolve()),
        "query_script_sha256": _capture_hash(script),
        "artifacts": {
            "stdout": stdout_path.relative_to(root).as_posix(),
            "stderr": stderr_path.relative_to(root).as_posix(),
            "log": log.relative_to(root).as_posix(),
            "script_log": script_log.relative_to(root).as_posix(),
        },
        "read_only": True,
        "auto_analysis_disabled": True,
        "import_attempted": False,
        "overwrite_attempted": False,
        "project_created": False,
    }
    meta["metadata_artifact"] = metadata_path.relative_to(root).as_posix()
    meta["ok"] = result.returncode == 0 and all(checks.values())
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=300, help="headless query timeout in seconds (1-1800)")
    parser.add_argument("--rva", type=lambda value: int(value, 0), help="optional image-relative function RVA to query")
    parser.add_argument("--vtable-slot", type=lambda value: int(value, 0), help="read an x64 function pointer from this zero-based slot at --rva")
    parser.add_argument("--vtable-rtti-rvas", type=lambda value: [int(part, 0) for part in value.split(",")], help="read bounded MSVC RTTI identities for 1-32 comma-separated vtable RVAs")
    parser.add_argument("--address-rva", type=lambda value: int(value, 0), help="inspect instructions and references around an image-relative address even when it has no function boundary")
    parser.add_argument("--pointer-table-rva", type=lambda value: int(value, 0), help="read a bounded table of x64 function pointers at this image-relative address")
    parser.add_argument("--pointer-count", type=int, help="number of consecutive eight-byte pointers to read (1-128)")
    parser.add_argument("--follow-direct-calls", type=int, default=0, help="decompile up to this many direct call targets from the selected function (0-8)")
    parser.add_argument("--follow-incoming-calls", type=int, default=0, help="decompile up to this many distinct direct callers of the selected function (0-32)")
    parser.add_argument("--list-call-edges", action="store_true", help="list every direct call edge and unresolved indirect call site in the selected function")
    parser.add_argument("--search-string", help="search initialized GOG program memory for an exact ASCII literal and list its analyzed references")
    parser.add_argument("--search-displacement", type=lambda value: int(value, 0), help="search analyzed instruction operands for a memory operand containing this displacement (for example 0x274)")
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.timeout > 1800:
        parser.error("--timeout must be between 1 and 1800 seconds")
    try:
        result = run_query(
            timeout=args.timeout, rva=args.rva, vtable_slot=args.vtable_slot,
            vtable_rtti_rvas=args.vtable_rtti_rvas,
            address_rva=args.address_rva,
            pointer_table_rva=args.pointer_table_rva, pointer_count=args.pointer_count or 0,
            follow_direct_calls=args.follow_direct_calls,
            follow_incoming_calls=args.follow_incoming_calls,
            enumerate_call_edges=args.list_call_edges,
            search_string=args.search_string,
            search_displacement=args.search_displacement,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, GhidraProbeError, TargetError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
