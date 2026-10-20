#!/usr/bin/env python3
"""Screen classic PEX streams in Skyrim - Misc.bsa for Story Manager send calls."""
from __future__ import annotations

import hashlib
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.papyrus_pex import MAGIC, configured_data_dir, parse_pex, PexFormatError

TARGETS = ("SendStoryEvent", "SendStoryEventAndWait")
MAX_STREAM = 4 * 1024 * 1024


def main() -> int:
    archive = configured_data_dir() / "Skyrim - Misc.bsa"
    if not archive.is_file():
        raise SystemExit("configured Skyrim - Misc.bsa is unavailable")
    sha = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    archive_hash = sha.hexdigest()
    valid_streams = 0
    rejected_markers = 0
    hits = []
    with archive.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as blob:
        positions = []
        cursor = 0
        while True:
            cursor = blob.find(MAGIC, cursor)
            if cursor < 0:
                break
            positions.append(cursor)
            cursor += len(MAGIC)
        for index, start in enumerate(positions):
            end = positions[index + 1] if index + 1 < len(positions) else len(blob)
            if end - start > MAX_STREAM:
                rejected_markers += 1
                continue
            try:
                parsed = parse_pex(blob[start:end])
            except (PexFormatError, ValueError, IndexError, struct.error):
                rejected_markers += 1
                continue
            source = str(parsed.get("source", ""))
            if parsed.get("major") != 3 or not source.casefold().endswith(".psc"):
                rejected_markers += 1
                continue
            valid_streams += 1
            lines = [line for line in parsed["lines"]
                     if any(target in line for target in TARGETS)]
            if lines:
                hits.append({
                    "source": source,
                    "pex_offset": start,
                    "candidate_stream_size": end - start,
                    "parsed_bytes": parsed["consumed_bytes"],
                    "trailing_bytes": parsed["trailing_bytes"],
                    "calls": lines,
                })
    print(json.dumps({
        "archive": archive.name,
        "archive_sha256": archive_hash,
        "parser": "tools.papyrus_pex.parse_pex over raw archive PEX magic candidates; read-only",
        "candidate_magic_count": len(positions),
        "validated_classic_pex_count": valid_streams,
        "rejected_or_non_pex_magic_count": rejected_markers,
        "story_event_call_hit_count": len(hits),
        "hits": hits,
        "coverage_limit": "Only parseable uncompressed classic PEX streams in Skyrim - Misc.bsa; no other BSA/BA2, loose scripts, dynamically constructed calls, or native senders.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
