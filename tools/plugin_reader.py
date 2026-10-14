#!/usr/bin/env python3
"""Read-only TES4 plugin record inventory and field-signature inspection."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import mmap
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ae_target import TargetError, parse_active_plugins


class PluginFormatError(ValueError):
    pass


def resolve_record_winner(candidates: list[dict], active_order: list[str]) -> dict:
    """Select the last active file row for one logical FormID.

    This small resolver supports explicit, already validated order data. It is
    not an xEdit replacement and must not be used with an incomplete profile.
    """
    if not candidates:
        raise PluginFormatError("no record candidates were supplied")
    try:
        order = parse_active_plugins("\n".join("*" + name for name in active_order))
    except (TypeError, TargetError) as exc:
        raise PluginFormatError(f"active order is not a complete AE plugin list: {exc}") from exc
    ranks = {name.casefold(): index for index, name in enumerate(order)}
    keys = set()
    for row in candidates:
        plugin = str(row.get("plugin", ""))
        origin = str(row.get("origin_plugin", ""))
        if plugin.casefold() not in ranks:
            raise PluginFormatError(f"candidate plugin is absent from active order: {plugin or 'unknown'}")
        if not origin or origin == "UNRESOLVED":
            raise PluginFormatError("candidate has an unresolved FormID origin")
        keys.add((row.get("signature"), origin.casefold(), str(row.get("local_form_id", "")).upper()))
    if len(keys) != 1:
        raise PluginFormatError("candidate rows do not identify the same logical record")
    return max(candidates, key=lambda row: ranks[str(row["plugin"]).casefold()])


def _records(data: mmap.mmap, start: int = 0, end: int | None = None):
    limit = len(data) if end is None else end
    pos = start
    while pos < limit:
        if limit - pos < 24:
            raise PluginFormatError(f"truncated record header at offset 0x{pos:X}")
        signature, size = struct.unpack_from("<4sI", data, pos)
        if signature == b"GRUP":
            if size < 24 or pos + size > limit:
                raise PluginFormatError(f"invalid record group at offset 0x{pos:X}")
            yield from _records(data, pos + 24, pos + size)
            pos += size
            continue
        if pos + 24 + size > limit:
            raise PluginFormatError(f"record exceeds containing group at offset 0x{pos:X}")
        flags, form_id = struct.unpack_from("<II", data, pos + 8)
        yield signature.decode("ascii", "strict"), flags, form_id, pos, bytes(data[pos + 24:pos + 24 + size])
        pos += 24 + size


def _subrecords(payload: bytes, flags: int):
    if flags & 0x00040000:
        if len(payload) < 4:
            raise PluginFormatError("compressed record has no size prefix")
        expected = struct.unpack_from("<I", payload)[0]
        try:
            payload = zlib.decompress(payload[4:])
        except zlib.error as exc:
            raise PluginFormatError("compressed record payload is invalid") from exc
        if len(payload) != expected:
            raise PluginFormatError("compressed record size does not match its prefix")
    pos = 0
    extended_size: int | None = None
    while pos < len(payload):
        if len(payload) - pos < 6:
            raise PluginFormatError("truncated subrecord header")
        raw_sig, short_size = struct.unpack_from("<4sH", payload, pos)
        pos += 6
        if raw_sig == b"XXXX":
            if short_size != 4 or pos + 4 > len(payload):
                raise PluginFormatError("invalid extended subrecord size")
            extended_size = struct.unpack_from("<I", payload, pos)[0]
            pos += 4
            continue
        size = short_size if extended_size is None else extended_size
        extended_size = None
        if pos + size > len(payload):
            raise PluginFormatError("subrecord exceeds its containing record")
        yield raw_sig.decode("ascii", "strict"), payload[pos:pos + size]
        pos += size
    if extended_size is not None:
        raise PluginFormatError("record ends after an XXXX size marker")


def read_plugin(path: str | Path, signature: str | None = None, *, include_subrecords: bool = False):
    plugin_path = Path(path).expanduser()
    if not plugin_path.is_file():
        raise FileNotFoundError("plugin file is missing or inaccessible")
    if plugin_path.stat().st_size == 0:
        raise PluginFormatError("plugin file is empty")
    with plugin_path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        masters: list[str] = []
        for sig, flags, form_id, offset, payload in _records(data):
            fields = list(_subrecords(payload, flags))
            if sig == "TES4":
                masters = [value.rstrip(b"\0").decode("cp1252") for sub_sig, value in fields if sub_sig == "MAST"]
            if signature and sig != signature:
                continue
            origin_index = form_id >> 24
            origin = (masters + [plugin_path.name])[origin_index] if origin_index <= len(masters) else "UNRESOLVED"
            editor_id = next((value.rstrip(b"\0").decode("cp1252") for sub_sig, value in fields if sub_sig == "EDID"), "")
            row = {
                "signature": sig,
                "plugin": plugin_path.name,
                "origin_plugin": origin,
                "file_form_id": f"{form_id:08X}",
                "local_form_id": f"{form_id & 0x00FFFFFF:06X}",
                "offset": f"0x{offset:X}",
                "flags": f"{flags:08X}",
                "editor_id": editor_id,
                "subrecord_signatures": [sub_sig for sub_sig, _ in fields],
            }
            if include_subrecords:
                row["subrecords"] = [
                    {
                        "signature": sub_sig,
                        "length": len(value),
                        "value_hex": value.hex(),
                        "text_cp1252": value.rstrip(b"\0").decode("cp1252", "replace")[:512],
                    }
                    for sub_sig, value in fields
                ]
            yield row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="report Python parser readiness without reading private game data")
    inventory = sub.add_parser("inventory", help="count record signatures in one plugin")
    inventory.add_argument("plugin")
    record = sub.add_parser("record", help="inspect one record by signature plus local FormID or EditorID")
    record.add_argument("plugin")
    record.add_argument("--signature", required=True)
    record.add_argument("--form-id", help="plugin-local hexadecimal FormID")
    record.add_argument("--editor-id", help="case-insensitive EditorID substring")
    record.add_argument("--include-subrecords", action="store_true", help="include raw subrecord bytes and bounded CP1252 view")
    args = parser.parse_args(argv)
    if args.command == "doctor":
        print(json.dumps({"tool": "plugin_reader", "status": "ready", "backend": "Python standard library", "read_only": True, "xedit_loaded": False}, indent=2))
        return 0
    try:
        if args.command == "inventory":
            counts = Counter(row["signature"] for row in read_plugin(args.plugin))
            print(json.dumps({"plugin": Path(args.plugin).name, "record_count": sum(counts.values()), "signature_counts": dict(sorted(counts.items()))}, indent=2))
            return 0
        if not args.form_id and not args.editor_id:
            parser.error("record requires --form-id and/or --editor-id")
        form_id = int(args.form_id.removeprefix("0x"), 16) if args.form_id else None
        matched = 0
        for row in read_plugin(args.plugin, args.signature, include_subrecords=args.include_subrecords):
            if form_id is not None and int(row["local_form_id"], 16) != form_id & 0x00FFFFFF:
                continue
            if args.editor_id and args.editor_id.casefold() not in row["editor_id"].casefold():
                continue
            print(json.dumps(row, ensure_ascii=False))
            matched += 1
        return 0 if matched else 3
    except (OSError, PluginFormatError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
