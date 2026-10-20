#!/usr/bin/env python3
"""Summarize bounded direct-parser captures for the DA04 entry-path screen."""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path


DEFAULT_DIR = Path(".local/alignment/transactions/TX-20261016-0036")
CAPTURES = (
    "smqn-da04-node",
    "qust-da04",
    "qust-mq205",
    "qust-elder-knowledge",
    "dial-septimus",
    "info-septimus",
    "book-ruminations",
    "dial-da04",
    "info-da04",
    "dial-mq205",
    "info-mq205",
    "book-all",
)
INTERESTING = {
    "CTDA", "DNAM", "ENAM", "FNAM", "FULL", "INDX", "NNAM",
    "PNAM", "QNAM", "QSDT", "SNAM", "VMAD",
}


def records_for(path: Path) -> tuple[dict, list[dict]]:
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    lines = wrapper.get("records_jsonl", "").splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    return wrapper, records


def selected_subrecords(record: dict) -> list[tuple[str, str]]:
    selected = []
    for subrecord in record.get("subrecords", []):
        signature = subrecord.get("signature", "")
        if signature not in INTERESTING:
            continue
        hex_value = subrecord.get("hex", "")
        if signature == "VMAD":
            value = f"<{len(hex_value) // 2} bytes>"
        else:
            value = hex_value
        selected.append((signature, value))
    return selected


def full_string_id(record: dict) -> str:
    for subrecord in record.get("subrecords", []):
        if subrecord.get("signature") == "FULL":
            raw = bytes.fromhex(subrecord.get("hex", ""))
            if len(raw) == 4:
                return f"StringID:{struct.unpack('<I', raw)[0]:08X}"
            return f"raw:{raw.hex()}"
    return "none"


def vmad_names(record: dict) -> list[str]:
    values = []
    for subrecord in record.get("subrecords", []):
        if subrecord.get("signature") != "VMAD":
            continue
        raw = bytes.fromhex(subrecord.get("hex", ""))
        for match in re.findall(rb"[A-Za-z_][A-Za-z0-9_]{3,}", raw):
            value = match.decode("ascii", errors="ignore")
            if any(key in value.casefold() for key in ("da04", "septimus", "rumination", "mq205", "elder")):
                values.append(value)
    return list(dict.fromkeys(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transaction-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    for name in CAPTURES:
        path = args.transaction_dir / f"{name}.json"
        if not path.exists():
            print(f"{name}: missing")
            continue
        wrapper, records = records_for(path)
        print(
            f"{name}: route={wrapper.get('query_route')} "
            f"record_count={wrapper.get('record_count')} parsed={len(records)}"
        )
        if name == "book-all":
            matches = [
                record for record in records
                if "rumination" in record.get("editor_id", "").casefold()
            ]
            print(f"  editor_id_matches={len(matches)}")
            for record in matches:
                print(
                    "  BOOK "
                    f"form={record.get('file_form_id')} "
                    f"editor_id={record.get('editor_id')} "
                    f"flags={record.get('flags')} "
                    f"FULL={full_string_id(record)} "
                    f"DATA={[s.get('hex') for s in record.get('subrecords', []) if s.get('signature') == 'DATA']}"
                )
            continue
        for record in records:
            print(
                f"  {record.get('signature')} form={record.get('file_form_id')} "
                f"editor_id={record.get('editor_id')} flags={record.get('flags')}"
            )
            for signature, value in selected_subrecords(record):
                if signature == "CTDA":
                    raw = bytes.fromhex(value)
                    function_index = int.from_bytes(raw[8:10], "little") if len(raw) >= 10 else None
                    comparison = struct.unpack("<f", raw[4:8])[0] if len(raw) >= 8 else None
                    print(
                        f"    CTDA function_index={function_index} "
                        f"comparison_float={comparison} type_byte={raw[0]:02x} raw={value}"
                    )
                else:
                    print(f"    {signature} {value}")
            names = vmad_names(record)
            if names:
                print(f"    VMAD_NAMES {' | '.join(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
