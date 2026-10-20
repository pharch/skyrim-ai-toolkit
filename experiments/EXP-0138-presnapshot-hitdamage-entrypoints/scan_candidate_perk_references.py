#!/usr/bin/env python3
"""Scan all official-master subrecords for exact zero-capable PERK FormID bytes."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
TARGETS = {
    "00107831": "DeftMovement",
    "000E863F": "MQ105PhantomFormPerk",
    "000EB24A": "InvulnerableActorZeroIncomingDamage",
    "0201E7F0": "DLC2BlackBookCompanionsSafePerk",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    cfg = read_local_config(ROOT)
    configured = cfg.get("SKYRIM_DATA", "").strip()
    if not configured:
        raise SystemExit("SKYRIM_DATA is not configured")
    data_path = _native_path(configured)
    needles = {form_id: bytes.fromhex(form_id)[::-1] for form_id in TARGETS}
    hashes = {}
    record_counts = Counter()
    subrecord_counts = Counter()
    matches = []
    for plugin_name in PLUGINS:
        plugin = data_path / plugin_name
        if not plugin.is_file():
            raise SystemExit(f"configured official master is missing: {plugin_name}")
        hashes[plugin_name] = digest(plugin)
        for record in read_plugin(plugin, include_subrecords=True):
            record_counts[plugin_name] += 1
            for sub in record.get("subrecords", []):
                subrecord_counts[plugin_name] += 1
                blob = bytes.fromhex(sub["value_hex"])
                found = [form_id for form_id, needle in needles.items() if needle in blob]
                if found:
                    matches.append({
                        "source_plugin": plugin_name,
                        "record_signature": record.get("signature"),
                        "record_form_id": record.get("file_form_id"),
                        "record_editor_id": record.get("editor_id"),
                        "subrecord_signature": sub.get("signature"),
                        "matching_target_perks": found,
                        "raw_subrecord_hex": sub["value_hex"],
                    })
    result = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Configured official five masters; read-only direct TES4 parser; exact FormID-byte occurrence scan.",
        "plugin_sha256": hashes,
        "record_counts": dict(record_counts),
        "subrecord_counts": dict(subrecord_counts),
        "target_perks": TARGETS,
        "match_count": len(matches),
        "matches_by_target": {form_id: sum(form_id in item["matching_target_perks"] for item in matches) for form_id in TARGETS},
        "matches": matches,
        "limit": "Raw exact FormID-byte occurrences include any coincidental numeric reuse and do not establish semantic ownership, active perk acquisition, or runtime state.",
    }
    target = ROOT / ".local/alignment/transactions/TX-20261020-0010/q91/candidate-perk-references.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": target.relative_to(ROOT).as_posix(),
        "sha256": digest(target),
        "plugin_sha256": hashes,
        "record_counts": dict(record_counts),
        "match_count": len(matches),
        "matches_by_target": result["matches_by_target"],
        "matches": [{k: v for k, v in match.items() if k != "raw_subrecord_hex"} for match in matches],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
