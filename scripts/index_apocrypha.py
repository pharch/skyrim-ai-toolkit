#!/usr/bin/env python3
"""Compatibility wrapper for private Apocrypha indexing.

The database is restricted to ignored `.local/`; the command prints only
aggregate count and source hash. It never prints private message content.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config

from tools.apocrypha.core import ArchiveError, ingest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("export", type=Path, nargs="?", help="authorized local DiscordChatExporter JSON; defaults to ignored local config")
parser.add_argument("--db", type=Path, default=Path(".local/apocrypha.sqlite3"))
parser.add_argument("--rebuild", action="store_true")
args = parser.parse_args()
config = read_local_config()
raw_input = str(args.export) if args.export else config.get("APOCRYPHA_EXPORT_PATH", "").strip()
if not raw_input:
    parser.error("provide EXPORT or set APOCRYPHA_EXPORT_PATH in ignored config/local.env")
input_path = Path(raw_input)
database = args.db if args.db != Path(".local/apocrypha.sqlite3") else Path(config.get("APOCRYPHA_INDEX_PATH", ".local/apocrypha.sqlite3"))
try:
    print(json.dumps(ingest(input_path, database, rebuild=args.rebuild), indent=2))
except (ArchiveError, OSError, json.JSONDecodeError) as exc:
    print(json.dumps({"error": str(exc)}), file=sys.stderr)
    raise SystemExit(2)
