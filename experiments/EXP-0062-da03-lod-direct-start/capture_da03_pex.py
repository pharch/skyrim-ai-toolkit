#!/usr/bin/env python3
"""Capture parsed DA03Start/Lod PEX bodies with the retained PEX decoder."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.papyrus_pex import parse_pex

INPUTS = {
    "TIF__000D7933": {
        "archive": "Skyrim - Misc.bsa",
        "archive_sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d",
        "source_string_offset": 6531055,
        "pex_offset": 6531037,
        "pex_end_offset": 6532036,
        "pex_size": 999,
    },
    "TIF__000E0D47": {
        "archive": "Skyrim - Misc.bsa",
        "archive_sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d",
        "source_string_offset": 6716558,
        "pex_offset": 6716540,
        "pex_end_offset": 6717428,
        "pex_size": 888,
    },
    "TIF__0010F590": {
        "archive": "Skyrim - Misc.bsa",
        "archive_sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d",
        "source_string_offset": 8480195,
        "pex_offset": 8480177,
        "pex_end_offset": 8480861,
        "pex_size": 684,
    },
    "QF_DA03Start_000D7939": {
        "archive": "Skyrim - Misc.bsa",
        "archive_sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d",
        "source_evidence": "EV-0321",
    },
}
PEX_DIR = ROOT / ".local/readiness/papyrus"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0323-da03-pex.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    scripts = []
    for name, provenance in INPUTS.items():
        path = PEX_DIR / f"{name}.pex"
        data = path.read_bytes()
        parsed = parse_pex(data)
        if parsed["consumed_bytes"] != len(data) or parsed["trailing_bytes"] != 0:
            raise ValueError(f"incomplete PEX parse for {name}")
        scripts.append({
            "script": name,
            "pex_path": path.relative_to(ROOT).as_posix(),
            "pex_sha256": sha256(data),
            "pex_size": len(data),
            "archive_extraction": provenance,
            "format": {
                "major": parsed["major"],
                "minor": parsed["minor"],
                "game_id": parsed["game_id"],
                "compiled": parsed["compiled"],
                "source": parsed["source"],
                "object_count": parsed["object_count"],
                "consumed_bytes": parsed["consumed_bytes"],
                "trailing_bytes": parsed["trailing_bytes"],
            },
            "disassembly_lines": parsed["lines"],
        })
    result = {
        "capture_id": "EV-0323",
        "transaction_id": "TX-20261017-0008",
        "frontier_id": "Q-0061",
        "decoder": "tools/papyrus_pex.py::parse_pex",
        "scope": "Bounded classic PEX 3.2 streams from the hash-identified base Skyrim - Misc.bsa; QF extraction provenance is cross-linked to EV-0321.",
        "scripts": scripts,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "scripts": [{"script": row["script"], "pex_sha256": row["pex_sha256"],
                     "pex_size": row["pex_size"], "consumed_bytes": row["format"]["consumed_bytes"]}
                    for row in scripts],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
