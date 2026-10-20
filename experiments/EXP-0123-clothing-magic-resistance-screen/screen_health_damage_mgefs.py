#!/usr/bin/env python3
"""Screen exact official-five-master MGEFs for Health effects with resistance AVs."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin, resolve_record_winner

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
RESIST_AVS = {40, 41, 42, 43, 44, 45}
HEALTH_AV = 24


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def source_root() -> Path:
    config = read_local_config(ROOT)
    value = config.get("SKYRIM_DATA", "").strip()
    if not value:
        raise RuntimeError("SKYRIM_DATA is not configured")
    path = _native_path(value)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_dir():
        raise RuntimeError("configured official data directory is unavailable")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write capture below ignored .local")
    args = parser.parse_args()

    data_root = source_root()
    paths = {name: data_root / name for name in PLUGINS}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise RuntimeError("configured official source is unavailable for: " + ", ".join(missing))
    manifest = [
        {"plugin": name, "sha256": digest(path), "size_bytes": path.stat().st_size}
        for name, path in paths.items()
    ]
    grouped: dict[tuple[str, str], list[dict]] = {}
    source_counts = {}
    for plugin, path in paths.items():
        rows = list(read_plugin(path, "MGEF", include_subrecords=True))
        source_counts[plugin] = len(rows)
        for row in rows:
            key = (row["origin_plugin"].casefold(), row["local_form_id"].upper())
            grouped.setdefault(key, []).append(row)
    winners = {
        key: resolve_record_winner(rows, list(PLUGINS))
        for key, rows in grouped.items()
    }

    matching = []
    values = Counter()
    for (origin, local_id), row in sorted(winners.items()):
        data_rows = [item for item in row.get("subrecords", []) if item["signature"] == "DATA"]
        raw = bytes.fromhex(data_rows[-1]["value_hex"]) if data_rows else b""
        if len(raw) < 72:
            continue
        resist = struct.unpack_from("<i", raw, 16)[0]
        archetype = struct.unpack_from("<I", raw, 64)[0]
        primary = struct.unpack_from("<i", raw, 68)[0]
        if primary != HEALTH_AV or resist not in RESIST_AVS:
            continue
        values[resist] += 1
        matching.append({
            "record_id": f"{origin}:{local_id}",
            "winning_source_plugin": row["plugin"],
            "file_form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "mgef_data_length": len(raw),
            "mgef_data_hex": raw.hex(),
            "flags_u32": struct.unpack_from("<I", raw, 0)[0],
            "resist_value_s32": resist,
            "archetype_u32": archetype,
            "primary_actor_value_s32": primary,
        })

    result = {
        "tool": "tools/plugin_reader.py read-only exact-five-master MGEF resolver",
        "schema_reference": "TES5Edit dev-4.1.6 Core/wbDefinitionsTES5.pas; MGEF DATA field layout",
        "read_only": True,
        "source_files": manifest,
        "record_counts_by_plugin": source_counts,
        "winning_unique_mgef_count": len(winners),
        "health_primary_with_resistance_av_count": len(matching),
        "counts_by_resist_actor_value": dict(sorted(values.items())),
        "health_damage_effects": matching,
        "scope": "official five masters only; source winners, not active profile winners; no game state inspected",
    }

    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output = output.resolve()
        try:
            output.relative_to((ROOT / ".local").resolve())
        except ValueError as exc:
            raise ValueError("output capture must remain below ignored .local/") from exc
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        result["capture"] = output.relative_to(ROOT).as_posix()
        result["capture_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
