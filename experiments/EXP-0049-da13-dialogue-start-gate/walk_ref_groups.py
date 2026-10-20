#!/usr/bin/env python3
"""Report type-6/8/9 parent-group ancestry for selected Skyrim.esm references."""
from __future__ import annotations

import hashlib
import json
import mmap
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local" / "xedit-data" / "official-ae-v1" / "Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
TARGETS = {"000E6C89", "0008998C", "000C2D2E", "00045F8E"}


def main() -> int:
    if not SOURCE.is_file():
        raise SystemExit("prepared official Skyrim.esm is unavailable")
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("prepared Skyrim.esm SHA-256 mismatch")
    found: list[dict[str, object]] = []

    def walk(data: mmap.mmap, start: int, end: int, stack: list[tuple[int, bytes]]) -> None:
        pos = start
        while pos < end:
            sig, size = struct.unpack_from("<4sI", data, pos)
            if sig == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"bad GRUP boundary at {pos:X}")
                label = data[pos + 8:pos + 12]
                kind = struct.unpack_from("<I", data, pos + 12)[0]
                walk(data, pos + 24, pos + size, stack + [(kind, label)])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"bad record boundary at {pos:X}")
            form_id = struct.unpack_from("<I", data, pos + 12)[0]
            form_text = f"{form_id:08X}"
            signature = sig.decode("ascii", "replace")
            if form_text in TARGETS:
                found.append({
                    "signature": signature,
                    "form_id": form_text,
                    "record_offset": f"0x{pos:X}",
                    "record_flags": f"0x{struct.unpack_from('<I', data, pos + 8)[0]:08X}",
                    "group_ancestry": [
                        {"type": kind, "label_hex": label.hex(), "label_little_endian": f"{int.from_bytes(label, 'little'):08X}"}
                        for kind, label in stack
                    ],
                })
            pos += 24 + size

    with SOURCE.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    print(json.dumps({
        "source": "prepared official Skyrim.esm",
        "source_sha256": digest,
        "record_groups_walked": True,
        "targets": sorted(TARGETS),
        "matches": found,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
