#!/usr/bin/env python3
"""Report and dispatch Python commands through the repository Conda environment."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV_NAME = "skyrim-ae-research"
REQUIRED_MODULES = ("pytest", "yaml", "pydantic", "cattrs")


def active_environment(env: dict[str, str] | None = None, prefix: str | None = None) -> bool:
    values = os.environ if env is None else env
    actual_prefix = prefix if prefix is not None else sys.prefix
    return values.get("CONDA_DEFAULT_ENV") == ENV_NAME or Path(actual_prefix).name == ENV_NAME


def command_for(argv: list[str], *, env: dict[str, str] | None = None, prefix: str | None = None,
                python_executable: str | None = None, conda_executable: str | None = None,
                require_conda: bool = False) -> list[str]:
    if active_environment(env, prefix):
        return [python_executable or sys.executable, *argv]
    if not conda_executable:
        if require_conda:
            raise FileNotFoundError("Conda is not on PATH; create environment.yml and rerun with conda available")
        return [python_executable or sys.executable, *argv]
    return [conda_executable, "run", "--no-capture-output", "--name", ENV_NAME, "python", *argv]


def environment_status() -> dict[str, object]:
    expected_active = active_environment()
    modules = {name: importlib.util.find_spec(name) is not None for name in REQUIRED_MODULES}
    system_python_supported = sys.version_info[:2] == (3, 12)
    return {
        "environment_name": ENV_NAME,
        "manifest_present": (ROOT / "environment.yml").is_file(),
        "conda_cli_available": shutil.which("conda") is not None,
        "expected_environment_active": expected_active,
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "required_modules": modules,
        "conda_environment_ready": expected_active and all(modules.values()),
        "system_python_supported": system_python_supported,
        "python_tools_usable_here": system_python_supported and modules["yaml"],
        "ready": (expected_active and all(modules.values())) or system_python_supported,
    }


def parse_run_args(values: list[str]) -> tuple[bool, list[str]]:
    """Parse dispatcher flags without interpreting the Python command's flags."""
    arguments = list(values)
    require_conda = bool(arguments and arguments[0] == "--require-conda")
    if require_conda:
        arguments.pop(0)
    if arguments[:1] == ["--"]:
        arguments.pop(0)
    return require_conda, arguments


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="report environment readiness without revealing paths")
    run = sub.add_parser("run", help="run a command with the repository Conda Python")
    run.add_argument("--require-conda", action="store_true", help="fail instead of using the current Python when Conda is absent")
    run.add_argument("args", nargs=argparse.REMAINDER, help="Python script/module and its arguments")
    if argv[:1] == ["run"]:
        if argv[1:2] in (["-h"], ["--help"]):
            parser.parse_args(argv[:2])
        require_conda, command_args = parse_run_args(argv[1:])
        if not command_args:
            parser.error("run requires a Python script or module")
        try:
            conda = shutil.which("conda")
            command = command_for(command_args, conda_executable=conda, require_conda=require_conda)
        except FileNotFoundError as exc:
            print(json.dumps({"ok": False, "error": str(exc), "environment_file": "environment.yml"}), file=sys.stderr)
            return 127
        if not conda and not require_conda and not active_environment():
            print("Conda is unavailable; running the current Python interpreter.", file=sys.stderr)
        return subprocess.run(command, cwd=ROOT, check=False).returncode

    args = parser.parse_args(argv)
    if args.command == "check":
        status = environment_status()
        print(json.dumps(status, indent=2))
        return 0 if status["ready"] else 1
    parser.error("use 'run' before the Python command")


if __name__ == "__main__":
    raise SystemExit(main())
