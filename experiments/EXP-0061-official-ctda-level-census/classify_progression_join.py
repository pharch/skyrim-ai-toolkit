#!/usr/bin/env python3
"""Classify captured QUST/PACK GetLevel conditions by their source position."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
ALIAS_STARTS = {"ALST", "ALLS"}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")
    base = ROOT / ".local/alignment/transactions" / args.transaction_id
    joined = json.loads((base / "EV-0321-progression-record-join.json").read_text(encoding="utf-8"))
    classified = []
    for record in joined["records"]:
        markers = record["structural_markers"]
        for condition in record["getlevel_conditions"]:
            index = condition["subrecord_index"]
            before = [marker for marker in markers if marker["index"] < index]
            last_next = max((m["index"] for m in before if m["signature"] == "NEXT"), default=-1)
            last_stage = max((m["index"] for m in before if m["signature"] == "INDX"), default=-1)
            last_alias = max((m["index"] for m in before if m["signature"] in ALIAS_STARTS), default=-1)
            alias_name = None
            if last_alias >= 0:
                alias_id = next((m["value_hex"] for m in before if m["index"] == last_alias), None)
                names = [m for m in before if last_alias < m["index"] < index and m["signature"] == "ALID"]
                alias_name = bytes.fromhex(names[-1]["value_hex"]).rstrip(b"\0").decode("cp1252", "replace") if names else None
            if record["record_signature"] == "QUST":
                if last_alias > last_stage:
                    scope = "alias-fill condition region"
                elif last_stage > last_next:
                    scope = "post-stage-marker condition region"
                elif last_next >= 0:
                    scope = "pre-stage record-level condition region"
                else:
                    scope = "record-level region; marker context unresolved"
            else:
                scope = "package condition region; execution context unresolved"
            decoded = condition["condition"]
            classified.append({
                "plugin": record["plugin"],
                "signature": record["record_signature"],
                "form_id": record["form_id"],
                "editor_id": record["editor_id"],
                "scope_from_order": scope,
                "alias_id_hex": alias_id if last_alias >= 0 else None,
                "alias_name": alias_name,
                "last_stage_marker_hex": next((m["value_hex"] for m in before if m["index"] == last_stage), None),
                "last_next_index": last_next,
                "condition_position": index,
                "comparison": decoded["comparison"],
                "level_operand": decoded["operand_float"],
                "run_on": decoded["run_on"],
                "condition_raw": decoded["raw"],
            })
    out = {
        "source_capture": "EV-0321-progression-record-join.json",
        "classification_basis": "Subrecord ordering and exact CTDA operands only. Region labels are structural; quest-start semantics still require schema/script corroboration.",
        "condition_count": len(classified),
        "conditions": classified,
    }
    out_path = base / "EV-0321-progression-condition-classification.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "condition_count": len(classified),
        "scope_counts": {
            scope: sum(1 for row in classified if row["scope_from_order"] == scope)
            for scope in sorted({row["scope_from_order"] for row in classified})
        },
        "conditions": [
            {key: row[key] for key in (
                "plugin", "signature", "form_id", "editor_id", "scope_from_order",
                "alias_name", "comparison", "level_operand", "condition_position",
            )}
            for row in classified
        ],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
