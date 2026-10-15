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


def run_query(*, root: Path = ROOT, config: dict[str, str] | None = None, timeout: int = 300,
              rva: int | None = None) -> dict[str, object]:
    """Run the checked-in query against the configured GOG project in place."""
    if rva is not None and (rva < 0 or rva >= 2**63):
        raise GhidraProbeError("--rva must be a non-negative 63-bit image-relative address")
    local_env = root / "config" / "local.env"
    if config is None:
        if not local_env.is_file():
            raise GhidraProbeError("ignored config/local.env is missing; copy the portable template and bind local tools")
        config = read_local_config(root)
    binding = resolve_binding(config, root=root)
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
    wrapper = output_dir / f"{stem}.cmd"

    headless = binding["headless"]
    project_dir = binding["project_dir"]
    project_name = str(binding["project_name"])
    program_name = str(binding["program_name"])
    command = (
        f'call "{_windows_path(headless)}" "{_windows_path(project_dir)}" "{project_name}" '
        f'-process "{program_name}" -noanalysis -readOnly '
        f'-scriptPath "{_windows_path(script.parent)}" '
        f'-log "{_windows_path(log)}" -scriptlog "{_windows_path(script_log)}" '
        f'-postScript "{script.name}"'
        + (f' 0x{rva:X}' if rva is not None else "")
    )
    wrapper.write_text("@echo off\r\n" + command + "\r\nexit /b %ERRORLEVEL%\r\n", encoding="utf-8", newline="")

    started = time.monotonic()
    try:
        result = subprocess.run(
            [_cmd_executable(), "/d", "/c", _windows_path(wrapper)],
            cwd=root,
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
    checks = {
        "program_identity_matches_gog_binary": path_matches,
        "function_lookup": "FUNCTION_LOOKUP=" in stdout,
        "requested_rva_lookup": rva is None or f"TARGET_RVA=0x{rva:X}" in stdout,
        "xref_call_edge": "XREF_CALL_EDGE=" in stdout and "NOT_FOUND_IN_ANALYZED_PROJECT" not in stdout,
        "disassembly": "DISASM=" in stdout and "DISASSEMBLY_INSTRUCTION_COUNT=" in stdout,
        "decompilation": "DECOMPILATION_BEGIN=" in stdout and "DECOMPILATION_END=" in stdout,
        "script_no_error": not script_error,
    }
    script_log_hash = _capture_hash(script_log)
    meta: dict[str, object] = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "operation": "existing_gog_project_read_only_query",
        "analysis_distribution": "GOG",
        "analysis_binary_product_version": binding["version"],
        "analysis_binary_sha256": binding["sha256"],
        "project_alias": "config/local.env:GHIDRA_PROJECT_REP_PATH",
        "program": program_name,
        "requested_rva": f"0x{rva:X}" if rva is not None else None,
        "program_executable_path_matches_gog_binary": path_matches,
        "exit_code": result.returncode,
        "elapsed_seconds": elapsed,
        "checks": checks,
        "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
        "script_log_sha256": script_log_hash,
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
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.timeout > 1800:
        parser.error("--timeout must be between 1 and 1800 seconds")
    try:
        result = run_query(timeout=args.timeout, rva=args.rva)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, GhidraProbeError, TargetError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
