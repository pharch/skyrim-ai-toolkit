#!/usr/bin/env python3
"""Capture Misc.bsa identity without printing the configured machine path."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.papyrus_pex import configured_data_dir

OUTPUT = ROOT / ".local/alignment/transactions/TX-20261018-0005/misc-bsa-metadata.json"


def main() -> int:
    archive = configured_data_dir() / "Skyrim - Misc.bsa"
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        stream.seek(4)
        version = struct.unpack("<I", stream.read(4))[0]
    record = {
        "filename": archive.name,
        "size_bytes": archive.stat().st_size,
        "sha256": digest.hexdigest(),
        "bsa_version_u32": version,
        "source_path": "private local configured Skyrim data directory; exact path intentionally not emitted",
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
