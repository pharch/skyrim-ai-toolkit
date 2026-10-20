#!/usr/bin/env python3
"""Check and dispatch research commands through this host's persistent .local venv."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PYTHON_VERSION = (3, 12)
ENVIRONMENT_ERROR_EXIT = 127
REQUIREMENTS_FILE = ROOT / "requirements.txt"


def execution_host() -> str:
    """Return the OS environment that owns native processes for this Python."""
    if os.name == "nt" or sys.platform == "win32":
        return "windows"
    if sys.platform.startswith("linux"):
        try:
            release = Path("/proc/version").read_text(encoding="utf-8", errors="replace").casefold()
        except OSError:
            release = ""
        if "microsoft" in release or os.environ.get("WSL_DISTRO_NAME"):
            return "wsl"
        return "linux"
    return sys.platform


def environment_dir(root: Path = ROOT, host: str | None = None) -> Path:
    """Return this host's ignored persistent environment directory."""
    host = execution_host() if host is None else host
    override = os.environ.get("SKYRIM_PYTHON_ENV_DIR")
    if override and root.resolve() == ROOT.resolve():
        path = Path(override).expanduser().resolve()
        local_root = (root / ".local").resolve()
        if path != local_root and local_root not in path.parents:
            raise ValueError("SKYRIM_PYTHON_ENV_DIR must stay under this checkout's ignored .local directory")
        return path
    return root / ".local" / "python-envs" / host


def venv_python(
    root: Path = ROOT,
    *,
    host: str | None = None,
    environment_path: Path | None = None,
) -> Path:
    """Return the active host's Python path inside its persistent environment."""
    host = execution_host() if host is None else host
    directory = environment_dir(root, host) if environment_path is None else environment_path
    if host == "windows":
        return directory / "Scripts" / "python.exe"
    return directory / "bin" / "python"


def pinned_distributions(requirements_file: Path = REQUIREMENTS_FILE) -> dict[str, str]:
    """Read the complete pinned requirements set, following nested -r files."""
    found: dict[str, str] = {}
    visited: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in visited:
            return
        visited.add(path)
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            if line.startswith(("-r ", "--requirement ")):
                visit(path.parent / line.split(maxsplit=1)[1])
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+-]+)", line)
            if not match:
                raise ValueError(f"requirements must pin every package with ==: {path.name}: {line}")
            name, version = match.groups()
            normalized = name.casefold().replace("_", "-").replace(".", "-")
            prior = next((key for key in found if key.casefold().replace("_", "-").replace(".", "-") == normalized), None)
            if prior is not None and found[prior] != version:
                raise ValueError(f"conflicting pins for {name}: {found[prior]} and {version}")
            found[name if prior is None else prior] = version

    visit(requirements_file)
    return found


REQUIRED_DISTRIBUTIONS = pinned_distributions()
REQUIRED_MODULES = {"lz4": "lz4.block", "PyYAML": "yaml", "pytest": "pytest"}

_PROBE = r'''
import importlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys

expected_prefix = Path(sys.argv[1]).resolve()
required_distributions = json.loads(sys.argv[2])
required_modules = json.loads(sys.argv[3])
modules = {}
versions = {}
for distribution, module in required_modules.items():
    try:
        importlib.import_module(module)
        modules[distribution] = True
    except Exception:
        modules[distribution] = False
for distribution in required_distributions:
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
    "pip_available": importlib.util.find_spec("pip") is not None,
    "config_present": config_present,
    "config_valid": config_valid,
    "config_error": config_error,
}))
'''
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
    if not report.get("pip_available"):
        failures.append("pip_missing")
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
    """Check the host's ignored persistent venv, all pinned packages, and config syntax."""
    directory = environment_dir(root)
    interpreter = venv_python(root, environment_path=directory)
    base: dict[str, object] = {
        "environment_name": directory.relative_to(root).as_posix(),
        "environment_path": str(directory),
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
                [
                    str(interpreter), "-c", _PROBE, str(directory.resolve()),
                    json.dumps(REQUIRED_DISTRIBUTIONS), json.dumps(REQUIRED_MODULES),
                ],
                # Imports from a WSL checkout on a Windows-mounted workspace can
                # exceed the old 30-second ceiling even when bootstrap verifies
                # the same environment successfully.
                cwd=root, text=True, capture_output=True, timeout=90, check=False,
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
                elif "pip_missing" in failures:
                    base["python_status"] = "FAIL_PIP_MISSING"
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
        raise RuntimeError("persistent .local Python environment is incomplete; run scripts/bootstrap_python.py")
    return [str(interpreter), *arguments]


def dispatch(arguments: list[str], *, root: Path = ROOT, status: dict[str, object] | None = None) -> int:
    checked = environment_status(root) if status is None else status
    if not checked.get("ready"):
        print(json.dumps({
            "ok": False,
            "error": "persistent .local Python environment or config/local.env is incomplete",
            "python_status": checked.get("python_status"),
            "dependency_failures": checked.get("dependency_failures", []),
            "config_present": checked.get("config_present"),
            "config_valid": checked.get("config_valid"),
            "setup": "Run the host's documented bootstrap command; research tools never install dependencies.",
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
    check = commands.add_parser("check", help="check the persistent .local environment and local config")
    check.add_argument("--strict", action="store_true", help="return nonzero unless venv, pins, and config all pass")
    commands.add_parser("run", help="run a Python command through the validated persistent .local venv")

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
