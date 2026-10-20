#!/usr/bin/env python3
"""Inspect schema-relevant official records found by the Q-0075 reference scan."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import PluginFormatError, read_plugin

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
TARGETS = {
    "Skyrim.esm": {
        "ARMO": {"0007C92E", "0010DFC8"},
        "CELL": {"000CAB92"},
        "CONT": {"00078C0C", "000C2CD7", "000C2CD8"},
        "LVLI": {
            "00101069", "0010106A", "0010106B", "0010106C", "0010106D",
            "00101071", "00101072", "00101074", "00100E85", "00100E8A", "0010DFCE",
        },
        "OTFT": {"0007EAB5", "000FBA59"},
        "REFR": {"00077D05"},
    },
    "Dawnguard.esm": {
        "OTFT": {"02011BE4", "02015CCD", "02016904"},
        "REFR": {"02009A55"},
    },
    "Dragonborn.esm": {
        "FLST": {"0203D290"},
        "OTFT": {"020285C4"},
    },
}
TARGET_IDS_BY_SIGNATURE = {
    signature: set().union(*(plugin_targets.get(signature, set()) for plugin_targets in TARGETS.values()))
    for signature in {signature for plugin_targets in TARGETS.values() for signature in plugin_targets}
}


def main() -> int:
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("SKYRIM_DATA is not configured")
    data_root = _native_path(data_value)
    sources = []
    selected = []
    for plugin in PLUGINS:
        path = data_root / plugin
        if not path.is_file():
            raise FileNotFoundError(f"configured official source is unavailable: {plugin}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        source_hash = digest.hexdigest()
        counts = {"record_count": 0, "subrecord_count": 0}
        for row in read_plugin(path, include_subrecords=True):
            counts["record_count"] += 1
            counts["subrecord_count"] += len(row.get("subrecords", []))
            wanted = TARGET_IDS_BY_SIGNATURE.get(row["signature"], set())
            if row["file_form_id"] not in wanted:
                if not (plugin == "Skyrim.esm" and row["signature"] == "NPC_"
                        and "savosaren" in row["editor_id"].casefold()):
                    continue
            selected.append({"source_sha256": source_hash, **row})
        sources.append({"plugin": plugin, "sha256": source_hash, **counts})
    print(json.dumps({
        "sources": sources,
        "record_count": len(selected),
        "records": selected,
        "scope": "Read-only direct plugin-reader output; exact official five masters, no profile winner or runtime state.",
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
