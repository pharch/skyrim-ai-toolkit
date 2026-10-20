#!/usr/bin/env python3
"""Print a compact, stage-focused view of the captured Dawnguard callbacks."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-callbacks.json"
FOCUS = {"0200352A", "0200D06C", "0200D90E", "0201A415"}


def brief(items: list[dict]) -> list[dict]:
    keep = []
    for item in items:
        name = item.get("function_name", "")
        if name in {"GetLevel", "GetStage", "GetStageDone"} or item.get("function_index") == 72:
            keep.append({key: item.get(key) for key in (
                "function_index", "function_name", "comparison", "operand_float",
                "operand_global", "param1", "param2", "run_on",
            )})
    return keep


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    for topic in data["topics"]:
        if topic["quest_form_id"] not in FOCUS:
            continue
        for info in topic["info_children"]:
            if not info["scripts"]:
                continue
            rows.append({
                "quest": topic["quest_editor_id"],
                "dial": topic["dial_editor_id"],
                "dial_form_id": topic["dial_form_id"],
                "info_form_id": info["info_form_id"],
                "scripts": info["scripts"],
                "conditions": brief(info["conditions"]),
            })
    print(json.dumps({"scripted_info_count": len(rows), "rows": rows}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
