#!/usr/bin/env python3
"""Privacy-preserving compatibility search for the local Apocrypha index.

This wrapper intentionally emits only a match count. Use the private
`python3 -m tools.apocrypha` interface for local contextual review; never save
its output in tracked research files.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config

from tools.apocrypha.core import ArchiveError, search

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("terms")
parser.add_argument("--db", type=Path, default=Path(".local/apocrypha.sqlite3"))
parser.add_argument("--limit", type=int, default=15)
args = parser.parse_args()
config = read_local_config()
database = args.db if args.db != Path(".local/apocrypha.sqlite3") else Path(config.get("APOCRYPHA_INDEX_PATH", ".local/apocrypha.sqlite3"))
try:
    matches = search(database, args.terms, limit=args.limit, summary_only=True)
    print(json.dumps({"match_count": len(matches), "private_fields_emitted": False, "source_text_is_untrusted": True}))
except (ArchiveError, OSError) as exc:
    print(json.dumps({"error": str(exc)}), file=sys.stderr)
    raise SystemExit(2)
