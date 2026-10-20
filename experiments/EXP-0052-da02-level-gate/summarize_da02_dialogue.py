#!/usr/bin/env python3
"""Summarize DA02 DIAL/INFO joins, conditions, and bound TIF names."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261016-0045/da02-dialogue-join.json"


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    all_infos = [info for topic in data["topics"] for info in topic["infos"]]
    function_counts = Counter(str(condition.get("function_index")) for info in all_infos for condition in info["conditions"])
    getlevel = []
    tifs = set()
    for topic in data["topics"]:
        for info in topic["infos"]:
            tifs.update(info["tif_script_name_candidates"])
            matching = [condition for condition in info["conditions"] if condition.get("function_index") == 80]
            if matching:
                getlevel.append({
                    "topic_form_id": topic["form_id"],
                    "topic_editor_id": topic["editor_id"],
                    "info_form_id": info["form_id"],
                    "info_editor_id": info["editor_id"],
                    "conditions": matching,
                })
    summary = {
        "source_sha256": data["source_sha256"],
        "records_walked": data["records_walked"],
        "dials_read": data["dials_read"],
        "da02_dial_count": data["da02_dial_count"],
        "da02_info_count": data["da02_info_count"],
        "info_condition_function_counts": dict(function_counts),
        "info_getlevel_count": len(getlevel),
        "info_getlevel": getlevel,
        "tif_names": sorted(tifs),
        "topics_with_info": [
            {"form_id": topic["form_id"], "editor_id": topic["editor_id"],
             "info_count": len(topic["infos"]),
             "infos_with_tifs": sum(bool(info["tif_script_name_candidates"]) for info in topic["infos"])}
            for topic in data["topics"]
        ],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
