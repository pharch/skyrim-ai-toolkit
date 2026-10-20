#!/usr/bin/env python3
"""Screen official-master PERK entrypoint rows for Q89 selector 0x55."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin

OFFICIAL_PLUGINS = (
    "Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm",
)
SELECTORS = {
    0x55: "unresolved_selector_0x55",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise SystemExit("SKYRIM_DATA is not bound in ignored config/local.env")
    data_path = _native_path(data_value)
    plugin_hashes: dict[str, str] = {}
    matched: list[dict[str, object]] = []
    total_perks: Counter[str] = Counter()
    total_entrypoint_rows = 0
    entrypoint_selector_counts: Counter[int] = Counter()
    format_samples: list[dict[str, object]] = []
    for plugin_name in OFFICIAL_PLUGINS:
        plugin_path = data_path / plugin_name
        if not plugin_path.is_file():
            raise SystemExit(f"configured official master is missing or inaccessible: {plugin_name}")
        plugin_hashes[plugin_name] = sha256(plugin_path)
        for row in read_plugin(plugin_path, "PERK", include_subrecords=True):
            total_perks[row["plugin"]] += 1
            subrecords = row.get("subrecords", [])
            for index, subrecord in enumerate(subrecords):
                if subrecord["signature"] != "PRKE":
                    continue
                header = bytes.fromhex(subrecord["value_hex"])
                entry_end = next(
                    (i + 1 for i in range(index + 1, len(subrecords)) if subrecords[i]["signature"] == "PRKF"),
                    len(subrecords),
                )
                entry = subrecords[index:entry_end]
                if not header or header[0] != 2:
                    continue
                data_sub = next((item for item in entry if item["signature"] == "DATA"), None)
                if data_sub is None:
                    continue
                data_raw = bytes.fromhex(data_sub["value_hex"])
                if not data_raw:
                    continue
                total_entrypoint_rows += 1
                selector = data_raw[0]
                entrypoint_selector_counts[selector] += 1
                if len(format_samples) < 16:
                    format_samples.append({
                        "plugin": row["plugin"], "editor_id": row["editor_id"],
                        "header_hex": subrecord["value_hex"], "data_hex": data_sub["value_hex"],
                        "selector_id_from_DATA_first_byte": selector,
                    })
                if selector not in SELECTORS:
                    continue
                epft = next((item for item in entry if item["signature"] == "EPFT"), None)
                epfd = next((item for item in entry if item["signature"] == "EPFD"), None)
                matched.append({
                    "plugin": row["plugin"],
                    "origin_plugin": row["origin_plugin"],
                    "file_form_id": row["file_form_id"],
                    "local_form_id": row["local_form_id"],
                    "editor_id": row["editor_id"],
                    "entry_header_hex": subrecord["value_hex"],
                    "data_hex": data_sub["value_hex"],
                    "selector_id": selector,
                    "selector_name": SELECTORS[selector],
                    "entry_function_type_hex": None if epft is None else epft["value_hex"],
                    "entry_function_data_hex": None if epfd is None else epfd["value_hex"],
                    "entry_subrecords": [
                        {"signature": item["signature"], "value_hex": item["value_hex"]}
                        for item in entry
                    ],
                })

    captured = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "configured official five masters, read-only direct TES4 parser",
        "plugin_sha256": plugin_hashes,
        "record_signature": "PERK",
        "coverage": {
            "total_perk_records_by_plugin": dict(total_perks),
            "total_entrypoint_rows_with_DATA": total_entrypoint_rows,
            "entrypoint_selector_counts": {str(key): value for key, value in sorted(entrypoint_selector_counts.items())},
            "entrypoint_format_samples": format_samples,
            "matching_entry_rows": len(matched),
            "selector_ids": {str(key): value for key, value in SELECTORS.items()},
            "profile_winner_resolution": False,
            "runtime_behavior_tested": False,
        },
        "entries": matched,
    }
    raw = json.dumps(captured, indent=2, ensure_ascii=False) + "\n"
    capture_dir = ROOT / ".local" / "alignment" / "transactions" / "TX-20261020-0008" / "q89"
    capture_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact = capture_dir / f"skyrim-esm-perk-entrypoints-{stamp}.json"
    artifact.write_text(raw, encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "artifact": str(artifact.relative_to(ROOT)),
        "artifact_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "plugin_sha256": plugin_hashes,
        "coverage": captured["coverage"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
