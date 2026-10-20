#!/usr/bin/env python3
"""Summarize the private EV-0321 five-master GetLevel source capture."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
KNOWN_SIGNATURES = {"DIAL", "INFO", "SMQN"}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")
    base = ROOT / ".local/alignment/transactions" / args.transaction_id
    capture_path = base / "EV-0321-getlevel-census.json"
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    if not capture.get("scan_complete"):
        raise RuntimeError("the five-master source scan is incomplete")

    by_signature: Counter[str] = Counter()
    by_plugin_signature: Counter[tuple[str, str]] = Counter()
    for row in capture["getlevel_hits"]:
        by_signature[row["record_signature"]] += 1
        by_plugin_signature[(row["source_plugin"], row["record_signature"])] += 1
    novel_hits = [row for row in capture["getlevel_hits"] if row["record_signature"] not in KNOWN_SIGNATURES]
    summary = {
        "capture_complete": capture.get("condition_census_complete", False),
        "target_product_version": capture["target_identity"]["product_version"],
        "target_sha256": capture["target_identity"]["sha256"],
        "master_hashes": {row["plugin"]: row["sha256"] for row in capture["source_files"]},
        "counts_by_signature": dict(sorted(by_signature.items())),
        "counts_by_plugin_and_signature": [
            {"plugin": plugin, "signature": signature, "hits": count}
            for (plugin, signature), count in sorted(by_plugin_signature.items())
        ],
        "known_family_hits": sum(
            count for signature, count in by_signature.items() if signature in KNOWN_SIGNATURES
        ),
        "outside_known_families_count": len(novel_hits),
        "outside_known_families": novel_hits,
    }
    output_path = base / "EV-0321-getlevel-summary.json"
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    novel_groups: dict[str, dict] = {}
    for row in novel_hits:
        signature = row["record_signature"]
        group = novel_groups.setdefault(signature, {"condition_count": 0, "records": {}})
        group["condition_count"] += 1
        group["records"].setdefault(
            (row["source_plugin"], row["record_form_id"]),
            {"plugin": row["source_plugin"], "form_id": row["record_form_id"], "editor_id": row["record_editor_id"]},
        )
    print(json.dumps({
        "capture_complete": summary["capture_complete"],
        "counts_by_signature": summary["counts_by_signature"],
        "counts_by_plugin_and_signature": summary["counts_by_plugin_and_signature"],
        "known_family_hits": summary["known_family_hits"],
        "outside_known_families_count": summary["outside_known_families_count"],
        "outside_known_families": {
            signature: {
                "condition_count": group["condition_count"],
                "unique_record_count": len(group["records"]),
                "records": list(group["records"].values())[:12],
                "record_sample_truncated": len(group["records"]) > 12,
            }
            for signature, group in sorted(novel_groups.items())
        },
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
