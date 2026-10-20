#!/usr/bin/env python3
"""Find exact raw FormID candidates for the DA05 Grotto helper in five masters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".local/xedit-data/official-ae-v1"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261018-0005/da05-helper-reference-screen.json"
EXPECTED = {
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
}
TARGET = 0x000955CF

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    target_bytes = TARGET.to_bytes(4, "little")
    source_rows: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    record_count = 0

    for plugin_name, expected_sha in EXPECTED.items():
        path = SOURCE_DIR / plugin_name
        actual_sha = file_sha256(path)
        if actual_sha != expected_sha:
            raise SystemExit(f"{plugin_name} SHA-256 mismatch: {actual_sha}")
        plugin_records = 0
        for row in read_plugin(path, include_subrecords=True):
            plugin_records += 1
            for sub in row["subrecords"]:
                value = bytes.fromhex(sub["value_hex"])
                start = 0
                while (at := value.find(target_bytes, start)) >= 0:
                    hits.append({
                        "plugin": plugin_name,
                        "signature": row["signature"],
                        "form_id": row["file_form_id"],
                        "origin_plugin": row["origin_plugin"],
                        "editor_id": row["editor_id"],
                        "record_offset": row["offset"],
                        "subrecord": sub["signature"],
                        "offset_in_subrecord": at,
                        "raw_window_hex": value[max(0, at - 8):at + 12].hex(),
                    })
                    start = at + 1
        record_count += plugin_records
        source_rows.append({"plugin": plugin_name, "sha256": actual_sha, "records_walked": plugin_records})

    unique_records = {
        (hit["plugin"], hit["form_id"], hit["signature"])
        for hit in hits
    }
    output = {
        "scope": "fixed official five-master files under .local/xedit-data/official-ae-v1; not a profile winner or runtime query",
        "parser": "tools.plugin_reader.read_plugin full subrecord parser; exact little-endian FormID byte scan",
        "target": {"signature": "QUST", "plugin": "Skyrim.esm", "form_id": "000955CF", "editor_id": "DA05_dunBloatedMansGrottoQST"},
        "sources": source_rows,
        "record_count": record_count,
        "raw_reference_match_count": len(hits),
        "unique_candidate_record_count": len(unique_records),
        "raw_reference_candidates": hits,
        "warning": "A FormID byte match is a source candidate, not proof that the field is a quest reference or that its caller executes. String/opaque/binary payload matches require schema or script validation.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "sources": source_rows,
        "record_count": record_count,
        "raw_reference_match_count": len(hits),
        "unique_candidate_record_count": len(unique_records),
        "output": OUTPUT.relative_to(ROOT).as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
