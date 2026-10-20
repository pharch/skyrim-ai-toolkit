#!/usr/bin/env python3
"""Summarize winning official-master QUST/PACK GetLevel conditions."""
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
    winners = json.loads((base / "EV-0321-official-winner-resolution.json").read_text(encoding="utf-8"))
    joined = json.loads((base / "EV-0321-progression-record-join.json").read_text(encoding="utf-8"))
    join_by_key = {
        (row["plugin"], row["record_signature"], row["form_id"]): row
        for row in joined["records"]
    }

    rows = []
    for record in winners["winning_records"]:
        if record["signature"] not in {"QUST", "PACK"}:
            continue
        joined_record = join_by_key.get((record["plugin"], record["signature"], record["file_form_id"]))
        if joined_record is None:
            raise RuntimeError(f"winning QUST/PACK not found in condition join: {record['file_form_id']}")
        markers = joined_record["structural_markers"]
        for condition_row in record["getlevel_conditions"]:
            index = condition_row["subrecord_index"]
            before = [m for m in markers if m["index"] < index]
            last_next = max((m["index"] for m in before if m["signature"] == "NEXT"), default=-1)
            last_stage = max((m["index"] for m in before if m["signature"] == "INDX"), default=-1)
            last_alias = max((m["index"] for m in before if m["signature"] in ALIAS_STARTS), default=-1)
            alias_name = None
            if last_alias >= 0:
                names = [m for m in before if last_alias < m["index"] < index and m["signature"] == "ALID"]
                alias_name = bytes.fromhex(names[-1]["value_hex"]).rstrip(b"\0").decode("cp1252", "replace") if names else None
            if record["signature"] == "QUST":
                if last_alias > last_stage:
                    scope = "alias Match Conditions"
                elif last_stage > last_next:
                    scope = "stage/log condition region"
                elif last_next >= 0:
                    scope = "Story Manager Conditions"
                else:
                    scope = "unresolved QUST condition region"
            else:
                scope = "PACK conditions"
            condition = condition_row["condition"]
            rows.append({
                "plugin": record["plugin"],
                "signature": record["signature"],
                "form_id": record["file_form_id"],
                "editor_id": record["editor_id"],
                "scope": scope,
                "alias_name": alias_name,
                "comparison": condition["comparison"],
                "operand_float": condition["operand_float"],
                "operand_global": condition["operand_global"],
                "use_global": condition["use_global"],
                "run_on": condition["run_on"],
                "condition_position": index,
                "condition_raw": condition["raw"],
            })
    global_ids = sorted({row["operand_global"] for row in rows if row["operand_global"]})
    from collections import Counter

    scope_counts = Counter(row["scope"] for row in rows)
    signature_scope_counts = Counter((row["signature"], row["scope"]) for row in rows)
    summary = {
        "source_winner_capture": "EV-0321-official-winner-resolution.json",
        "schema_basis": "TES5Edit dev-4.1.6 QUST field order: Quest Dialogue Conditions, NEXT, Story Manager Conditions, Stages, aliases.",
        "winning_qust_pack_condition_count": len(rows),
        "scope_counts": dict(sorted(scope_counts.items())),
        "signature_scope_counts": [
            {"signature": signature, "scope": scope, "conditions": count}
            for (signature, scope), count in sorted(signature_scope_counts.items())
        ],
        "global_operand_ids": global_ids,
        "conditions": rows,
    }
    (base / "EV-0321-winning-qust-pack-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "winning_qust_pack_condition_count": len(rows),
        "scope_counts": summary["scope_counts"],
        "signature_scope_counts": summary["signature_scope_counts"],
        "global_operand_ids": global_ids,
        "conditions": [
            {key: row[key] for key in (
                "plugin", "signature", "form_id", "editor_id", "scope", "alias_name",
                "comparison", "operand_float", "operand_global", "use_global",
            )}
            for row in rows
        ],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
