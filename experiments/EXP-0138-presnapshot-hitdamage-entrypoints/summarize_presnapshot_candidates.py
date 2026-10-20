#!/usr/bin/env python3
"""Summarize zero-capable pre-snapshot PERK rows and direct MGEF byte matches."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/transactions/TX-20261020-0010/q91"
SCREEN = CAPTURE / "presnapshot-perk-screen.json"
ENUM = CAPTURE / "commonlib-entrypoint-enum.json"
OUT = CAPTURE / "presnapshot-candidate-summary.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    enum = json.loads(ENUM.read_text(encoding="utf-8"))
    enum_lines = [row["text"] for block in enum.get("entrypoint_enum_blocks", []) for row in block.get("lines", [])]
    names = {}
    for line in enum_lines:
        text = line.strip()
        if not text.startswith("k") or "=" not in text:
            continue
        name, value = text.rstrip(",").split("=", 1)
        try:
            names[int(value.strip())] = name.strip()
        except ValueError:
            continue

    zero_rows = []
    for row in screen["selected_PERK_rows"]:
        value = row.get("EPFD_float_if_4_bytes")
        if value is None or value > 0.0:
            continue
        form_id = row["file_form_id"]
        links = [candidate for candidate in screen["raw_MGEF_subrecord_reference_candidates"] if form_id in candidate["matching_perk_ids"]]
        zero_rows.append({
            "plugin": row["plugin"], "form_id": form_id, "editor_id": row["editor_id"],
            "selector_id": row["selector_id"], "selector_name": names.get(row["selector_id"], "unknown"),
            "handler_id": row["handler_id_DATA_byte_1"], "EPFT_hex": row["EPFT_hex"],
            "EPFD_hex": row["EPFD_hex"], "EPFD_float": value, "CTDAs": row["CTDAs"],
            "raw_MGEF_reference_candidates": links,
        })

    result = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "screen_sha256": digest(SCREEN), "enum_sha256": digest(ENUM),
        "selector_names": {f"0x{value:02X}": names.get(value, "unknown") for value in sorted({0x1A, 0x1C, 0, 0x23, 0x24, 0x12, 1, 0x11, 2})},
        "all_nonpositive_EPFD_rows": zero_rows,
        "limit": "Float EPFD values and raw MGEF subrecord FormID-byte matches are source screens only; handler semantics, effect application, CTDA truth, level-one reachability, protection, and XP remain unverified.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "sha256": digest(OUT),
        "selector_names": result["selector_names"],
        "nonpositive_rows": [
            {"plugin": row["plugin"], "form_id": row["form_id"], "editor_id": row["editor_id"], "selector": f"0x{row['selector_id']:02X}/{row['selector_name']}", "handler": row["handler_id"], "EPFT": row["EPFT_hex"], "EPFD": row["EPFD_float"], "CTDA_count": len(row["CTDAs"]), "mgef_refs": len(row["raw_MGEF_reference_candidates"])}
            for row in zero_rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
