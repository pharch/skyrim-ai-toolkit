#!/usr/bin/env python3
"""Check and dispatch research commands through this checkout's .venv."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PYTHON_VERSION = (3, 12)
REQUIRED_DISTRIBUTIONS = {"lz4": "4.3.3", "PyYAML": "6.0.1"}
REQUIRED_MODULES = {"lz4": "lz4", "PyYAML": "yaml"}
ENVIRONMENT_ERROR_EXIT = 127

_PROBE = r'''
import importlib
import importlib.metadata
import json
from pathlib import Path
import sys

expected_prefix = Path(sys.argv[1]).resolve()
modules = {}
versions = {}
for distribution, module in (("lz4", "lz4.block"), ("PyYAML", "yaml")):
    try:
        importlib.import_module(module)
        modules[distribution] = True
    except Exception:
        modules[distribution] = False
    try:
        versions[distribution] = importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        versions[distribution] = None

config_present = Path("config/local.env").is_file()
config_valid = False
config_error = None
try:
    from scripts.local_config import read_local_config
    if not config_present:
        config_error = "config/local.env is missing"
    else:
        read_local_config()
        config_valid = True
except Exception as exc:
    config_error = f"{type(exc).__name__}: {exc}"

print(json.dumps({
    "python_version": ".".join(map(str, sys.version_info[:3])),
    "python_major_minor": list(sys.version_info[:2]),
    "inside_repo_venv": Path(sys.prefix).resolve() == expected_prefix,
    "module_imports": modules,
    "distribution_versions": versions,
    "config_present": config_present,
    "config_valid": config_valid,
    "config_error": config_error,
}))
'''


def venv_python(root: Path = ROOT, *, windows: bool | None = None) -> Path:
    """Return the platform-specific Python path inside the repository venv."""
    if windows is None:
        windows = os.name == "nt"
    if windows:
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def dependency_failures(versions: dict[str, str | None]) -> list[str]:
    return [
        f"{name}=={expected} (found {versions.get(name) or 'missing'})"
        for name, expected in REQUIRED_DISTRIBUTIONS.items()
        if versions.get(name) != expected
    ]


def probe_failures(report: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if not report.get("inside_repo_venv"):
        failures.append("wrong_interpreter")
    if tuple(report.get("python_major_minor", ())) != PYTHON_VERSION:
        failures.append("python_version")
    failures.extend(f"dependency:{item}" for item in dependency_failures(
        report.get("distribution_versions", {})  # type: ignore[arg-type]
    ))
    modules = report.get("module_imports", {})
    if isinstance(modules, dict):
        for name, available in modules.items():
            if not available and not any(item.startswith(f"dependency:{name}==") for item in failures):
                failures.append(f"module_import:{name}")
    if not report.get("config_present"):
        failures.append("config_missing")
    elif not report.get("config_valid"):
        failures.append("config_malformed")
    return failures


def external_binding_status(config: dict[str, str]) -> dict[str, bool]:
    """Report configured external lanes without asserting their readiness."""
    return {
        "gog_static_bindings_configured": all(config.get(k) for k in (
            "LEGACY_SKYRIM_REPO", "GHIDRA_HEADLESS_EXE", "GHIDRA_PROJECT_REP_PATH",
            "GHIDRA_ANALYSIS_EXE_GOG",
        )),
        "xedit_bindings_configured": all(config.get(k) for k in (
            "LEGACY_SKYRIM_REPO", "SSEEDIT_EXE", "SKYRIM_DATA", "XEDIT_SCRIPTS",
        )),
        "selected_profile_configured": bool(config.get("MO2_PROFILE_DIR") and config.get("PLUGINS_TXT")),
        "disposable_test_profile_configured": all(config.get(k) for k in (
            "SKYRIM_TEST_PROFILE_DIR", "SKYRIM_TEST_PLUGINS_TXT", "RESEARCH_TEST_SAVE",
        )),
        "observer_staged_dll_configured": bool(config.get("SKYRIM_OBSERVER_STAGED_DLL")),
        "observer_deployed_dll_configured": bool(config.get("SKYRIM_OBSERVER_DEPLOYED_DLL")),
        "live_bindings_configured": all(config.get(k) for k in (
            "SKYRIM_OBSERVER_DEPLOYED_DLL", "SKYRIM_TEST_PROFILE_DIR",
            "SKYRIM_TEST_PLUGINS_TXT", "RESEARCH_TEST_SAVE", "SKYRIM_OBSERVER_LOG_DIR",
        )),
    }


def environment_status(root: Path = ROOT) -> dict[str, object]:
    """Check the repository venv, its pinned runtime imports, and config syntax."""
    interpreter = venv_python(root)
    base: dict[str, object] = {
        "environment_name": "repository-.venv",
        "python_required": "3.12",
        "required_distributions": dict(REQUIRED_DISTRIBUTIONS),
        "venv_present": interpreter.is_file(),
        "python_status": "FAIL_VENV_MISSING",
        "python_version": None,
        "inside_repo_venv": False,
        "module_imports": {},
        "distribution_versions": {},
        "dependency_failures": [],
        "config_present": (root / "config" / "local.env").is_file(),
        "config_valid": False,
        "config_error": None,
        "external_prerequisites": {},
        "ready": False,
    }
    if interpreter.is_file():
        try:
            result = subprocess.run(
                [str(interpreter), "-c", _PROBE, str((root / ".venv").resolve())],
                cwd=root, text=True, capture_output=True, timeout=30, check=False,
            )
            if result.returncode != 0:
                base["python_status"] = "FAIL_VENV_PROBE"
                base["probe_error"] = "the repository venv probe did not complete"
            else:
                report = json.loads(result.stdout)
                base.update(report)
                failures = probe_failures(report)
                base["dependency_failures"] = [
                    item.removeprefix("dependency:") for item in failures if item.startswith("dependency:")
                ]
                if "wrong_interpreter" in failures:
                    base["python_status"] = "FAIL_WRONG_INTERPRETER"
                elif "python_version" in failures:
                    base["python_status"] = "FAIL_PYTHON_VERSION"
                elif any(item.startswith("dependency:") or item.startswith("module_import:") for item in failures):
                    base["python_status"] = "FAIL_DEPENDENCIES"
                elif "config_missing" in failures:
                    base["python_status"] = "FAIL_CONFIG_MISSING"
                elif "config_malformed" in failures:
                    base["python_status"] = "FAIL_CONFIG_MALFORMED"
                else:
                    base["python_status"] = "PASS"
                base["ready"] = not failures
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            base["python_status"] = "FAIL_VENV_PROBE"
            base["probe_error"] = "the repository venv could not be started or returned invalid status"

    try:
        from scripts.local_config import read_local_config

        config_path = root / "config" / "local.env"
        config = read_local_config(root)
        base["config_present"] = config_path.is_file()
        base["config_valid"] = config_path.is_file()
        base["config_error"] = None if config_path.is_file() else "config/local.env is missing"
        base["external_prerequisites"] = external_binding_status(config)
    except (OSError, ValueError) as exc:
        base["config_present"] = (root / "config" / "local.env").is_file()
        base["config_valid"] = False
        base["config_error"] = f"{type(exc).__name__}: {exc}"
        base["external_prerequisites"] = {
            "gog_static_bindings_configured": False,
            "xedit_bindings_configured": False,
            "selected_profile_configured": False,
            "live_bindings_configured": False,
        }
    return base


def command_for(arguments: list[str], *, interpreter: str | Path, ready: bool) -> list[str]:
    if not ready:
        raise RuntimeError("repository .venv is incomplete; run the documented Python setup")
    return [str(interpreter), *arguments]


def dispatch(arguments: list[str], *, root: Path = ROOT, status: dict[str, object] | None = None) -> int:
    checked = environment_status(root) if status is None else status
    if not checked.get("ready"):
        print(json.dumps({
            "ok": False,
            "error": "repository .venv or config/local.env is incomplete",
            "python_status": checked.get("python_status"),
            "dependency_failures": checked.get("dependency_failures", []),
            "config_present": checked.get("config_present"),
            "config_valid": checked.get("config_valid"),
            "setup": "Follow docs/LOCAL_RUNTIME_CONTRACT.md; research tools never install dependencies.",
        }), file=sys.stderr)
        return ENVIRONMENT_ERROR_EXIT
    try:
        command = command_for(arguments, interpreter=venv_python(root), ready=True)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return ENVIRONMENT_ERROR_EXIT
    return subprocess.run(command, cwd=root, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check repository .venv and local config without printing paths")
    check.add_argument("--strict", action="store_true", help="return nonzero unless venv, pins, and config all pass")
    commands.add_parser("run", help="run a Python command through the complete repository .venv")

    if argv[:1] == ["run"]:
        if argv[1:2] in (["-h"], ["--help"]):
            parser.parse_args(argv[:2])
        arguments = argv[1:]
        if arguments[:1] == ["--"]:
            arguments.pop(0)
        if not arguments:
            parser.error("run requires a Python script or module")
        return dispatch(arguments)

    args = parser.parse_args(argv)
    if args.command == "check":
        status = environment_status()
        print(json.dumps(status, indent=2))
        return 0 if status["ready"] else 1
    parser.error("use 'run' before the Python command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
