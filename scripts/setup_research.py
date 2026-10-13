#!/usr/bin/env python3
"""Initialize or validate the Codex research checkout; never configures Skyrim."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def initialize(root: Path = ROOT) -> bool:
    config = root / "config"
    example = config / "local.env.example"
    local = config / "local.env"
    if local.exists():
        print(f"Preserving existing local configuration: {local}")
        return False
    if not example.is_file():
        raise FileNotFoundError(f"configuration template is missing: {example}")
    config.mkdir(parents=True, exist_ok=True)
    with example.open("rb") as source, local.open("xb") as destination:
        shutil.copyfileobj(source, destination)
    if os.name != "nt":
        local.chmod(0o600)
    print(f"Created private local configuration: {local}")
    print("This did not inspect, configure, or write to Skyrim.")
    return True


def check(root: Path = ROOT) -> int:
    sys.path.insert(0, str(root / "scripts"))
    from validate_overlay import validate

    errors = validate(root)
    print("CODEX RESEARCH CHECK " + ("FAIL" if errors else "PASS"))
    for error in errors:
        print(f" - {error}")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="create config/local.env without overwriting it")
    commands.add_parser("check", help="validate repository structure and research data")
    args = parser.parse_args()
    if args.command == "init":
        initialize()
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
