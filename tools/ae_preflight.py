#!/usr/bin/env python3
"""Verify the exact Skyrim AE executable and complete active plugin order."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.ae_target import TargetError, assert_ae_target, preflight, read_executable_version, settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-executable", action="store_true", help="read ProductVersion/hash only; this does not pass the xEdit/live gate")
    parser.add_argument("--game-root", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.probe_executable:
            target = assert_ae_target()
            digest = hashlib.sha256(Path(target["executable"]).read_bytes()).hexdigest()
            print(json.dumps({"edition": "AE", "runtime": target["version"], "executable_sha256": digest, "full_order_verified": False}, indent=2))
        elif args.game_root:
            target = assert_ae_target()
            print(target["game_root"])
        else:
            print(json.dumps(preflight(), indent=2))
        return 0
    except (TargetError, OSError, UnicodeError) as exc:
        print(f"AE preflight failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
