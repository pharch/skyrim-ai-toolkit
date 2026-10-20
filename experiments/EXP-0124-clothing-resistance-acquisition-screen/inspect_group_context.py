#!/usr/bin/env python3
"""Capture TES4 group ancestry for Savos Aren and the placed Arch-Mage boots."""
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

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import PluginFormatError, _subrecords

TARGET_ACTOR = 0x0001C19F  # Skyrim.esm NPC_ SavosAren
TARGET_BOOT_REFERENCE = 0x00077D05  # Skyrim.esm REFR; NAME is 0007C92E
TARGET_VENDOR_REFERENCE = 0x00078C0B  # Skyrim.esm REFR; NAME is MerchantRiverwoodTraderChest
INTERESTING_FIELDS = {"NAME", "XESP", "XLCN", "XOWN", "XTEL", "DATA", "XPRM", "XORD"}


def walk(data: mmap.mmap, start: int = 0, end: int | None = None, groups=()):
    limit = len(data) if end is None else end
    pos = start
    while pos < limit:
        if limit - pos < 24:
            raise PluginFormatError(f"truncated record/group header at offset 0x{pos:X}")
        signature, size = struct.unpack_from("<4sI", data, pos)
        if signature == b"GRUP":
            if size < 24 or pos + size > limit:
                raise PluginFormatError(f"invalid record group at offset 0x{pos:X}")
            label = bytes(data[pos + 8:pos + 12])
            group_type = struct.unpack_from("<i", data, pos + 12)[0]
            if group_type == 0:
                label_text = label.decode("ascii", "replace")
            else:
                label_text = f"{int.from_bytes(label, 'little'):08X}"
            group = {"group_type": group_type, "label": label_text, "label_raw_hex": label.hex()}
            yield from walk(data, pos + 24, pos + size, (*groups, group))
            pos += size
            continue

        if pos + 24 + size > limit:
            raise PluginFormatError(f"record exceeds group at offset 0x{pos:X}")
        flags, form_id = struct.unpack_from("<II", data, pos + 8)
        record_signature = signature.decode("ascii", "strict")
        payload = bytes(data[pos + 24:pos + 24 + size])
        fields = list(_subrecords(payload, flags))
        match = record_signature == "REFR" and form_id in {TARGET_BOOT_REFERENCE, TARGET_VENDOR_REFERENCE}
        if record_signature == "ACHR":
            base = next((value for name, value in fields if name == "NAME" and len(value) == 4), None)
            match = base is not None and struct.unpack("<I", base)[0] == TARGET_ACTOR
        if match:
            selected = []
            for name, value in fields:
                if name not in INTERESTING_FIELDS:
                    continue
                decoded = value.hex()
                if name in {"NAME", "XLCN", "XOWN", "XTEL"} and len(value) == 4:
                    decoded = f"{struct.unpack('<I', value)[0]:08X}"
                elif name == "XESP" and len(value) == 8:
                    decoded = {
                        "parent_form_id": f"{struct.unpack_from('<I', value, 0)[0]:08X}",
                        "flags_u8": value[4],
                        "raw_tail_hex": value[5:].hex(),
                    }
                selected.append({"signature": name, "length": len(value), "decoded": decoded})
            yield {
                "signature": record_signature,
                "form_id": f"{form_id:08X}",
                "record_flags_hex": f"{flags:08X}",
                "record_offset_hex": f"0x{pos:X}",
                "group_ancestry": list(groups),
                "fields": selected,
            }
        pos += 24 + size


def main() -> int:
    config = read_local_config(ROOT)
    configured = config.get("SKYRIM_DATA", "").strip()
    if not configured:
        raise RuntimeError("SKYRIM_DATA is not configured")
    path = _native_path(configured) / "Skyrim.esm"
    if not path.is_file():
        raise FileNotFoundError("configured Skyrim.esm is unavailable")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    matches = []
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        matches = list(walk(data))
    print(json.dumps({
        "source_plugin": "Skyrim.esm",
        "source_sha256": digest.hexdigest(),
        "matches": matches,
        "scope": "Read-only TES4 group ancestry from exact Skyrim.esm bytes; no profile winner, quest-state, or runtime inference.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
