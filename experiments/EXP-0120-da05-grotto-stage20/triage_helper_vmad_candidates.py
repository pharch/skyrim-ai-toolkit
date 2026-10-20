#!/usr/bin/env python3
"""Extract printable script/property names from helper FormID VMAD candidates."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / ".local/alignment/transactions/TX-20261018-0005/da05-helper-reference-screen.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261018-0005/da05-helper-vmad-triage.json"
SOURCE_DIR = ROOT / ".local/xedit-data/official-ae-v1"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def main() -> int:
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    targets = {
        (str(hit["plugin"]), str(hit["form_id"]), str(hit["signature"]))
        for hit in screen["raw_reference_candidates"]
        if hit["subrecord"] == "VMAD"
    }
    grouped: dict[str, set[tuple[str, str]]] = {}
    for plugin, form_id, signature in targets:
        grouped.setdefault(plugin, set()).add((form_id, signature))

    results: list[dict[str, object]] = []
    for plugin, wanted in sorted(grouped.items()):
        for row in read_plugin(SOURCE_DIR / plugin, include_subrecords=True):
            key = (str(row["file_form_id"]), str(row["signature"]))
            if key not in wanted:
                continue
            for sub in row["subrecords"]:
                if sub["signature"] != "VMAD":
                    continue
                data = bytes.fromhex(sub["value_hex"])
                strings = [part.decode("ascii") for part in re.findall(rb"[A-Za-z][A-Za-z0-9_]{2,}", data)]
                results.append({
                    "plugin": plugin,
                    "signature": row["signature"],
                    "form_id": row["file_form_id"],
                    "origin_plugin": row["origin_plugin"],
                    "editor_id": row["editor_id"],
                    "record_offset": row["offset"],
                    "vmad_printable_names": strings,
                    "vmad_hex": sub["value_hex"],
                })

    output = {
        "scope": "VMAD subrecords only from exact helper FormID-byte candidate records; printable strings are leads, not decoded Papyrus semantics",
        "candidate_vmad_count": len(results),
        "candidates": results,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_vmad_count": len(results),
        "candidate_records": [
            {k: row[k] for k in ("plugin", "signature", "form_id", "editor_id", "vmad_printable_names")}
            for row in results
        ],
        "output": OUTPUT.relative_to(ROOT).as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
