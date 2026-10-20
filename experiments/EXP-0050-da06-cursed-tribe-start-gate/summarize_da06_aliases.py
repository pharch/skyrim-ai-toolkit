#!/usr/bin/env python3
"""Decode DA06 QUST alias subrecord groups from the retained parser output."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261016-0043/da06-qust-plugin-reader.stdout.raw"


def text_value(raw: str) -> str:
    return bytes.fromhex(raw).rstrip(b"\0").decode("cp1252", "replace")


def main() -> int:
    row = json.loads(SOURCE.read_text(encoding="utf-8"))
    aliases: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for field in row.get("subrecords", []):
        sig = field["signature"]
        raw = field["value_hex"]
        if sig == "ALST":
            if current is not None:
                aliases.append(current)
            current = {"alias_id": int.from_bytes(bytes.fromhex(raw), "little"), "fields": []}
        if current is not None:
            current["fields"].append({"signature": sig, "hex": raw})
    if current is not None:
        aliases.append(current)
    for alias in aliases:
        for field in alias["fields"]:
            if field["signature"] == "ALID":
                alias["alias_name"] = text_value(field["hex"])
                break
    print(json.dumps({"plugin": row["plugin"], "source_form_id": row["file_form_id"], "editor_id": row["editor_id"], "aliases": aliases}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
