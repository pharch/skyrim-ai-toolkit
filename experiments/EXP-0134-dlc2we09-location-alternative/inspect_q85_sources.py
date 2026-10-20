#!/usr/bin/env python3
"""Inspect preserved Q85 TES4 captures without resolving winner records."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261020-0004"

def records(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("records_jsonl", "")
    return [json.loads(line) for line in raw.splitlines() if line.strip()]

def sub(record, sig):
    return [bytes.fromhex(x["hex"]) for x in record.get("subrecords", []) if x.get("signature") == sig]

def main():
    for file in ("gjalund-dialogue-topics.raw.json", "dragonborn-info-all.raw.json"):
        rows = records(TX / file)
        print(f"FILE {file} count={len(rows)}")
        for row in rows:
            if row.get("signature") == "DIAL":
                t = sub(row, "TIFC")
                print("DIAL", row.get("file_form_id"), row.get("editor_id"), int.from_bytes(t[0], "little") if t else None)
            elif row.get("signature") == "INFO":
                tpic = sub(row, "TPIC")
                ctdas = sub(row, "CTDA")
                # Output all INFOs in the source-ID interval near Gjalund's dialogue groups,
                # plus any whose subrecords point at a captured Gjalund DIAL topic.
                fid = int(row.get("file_form_id", "0"), 16)
                if 0x02018FD0 <= fid <= 0x02018FFF or 0x0203A100 <= fid <= 0x0203A180 or 0x0202ADC0 <= fid <= 0x0202AE10:
                    print("INFO", row.get("file_form_id"), row.get("editor_id"), "subrecords", [x.get("signature") for x in row.get("subrecords", [])], "TPIC", [x.hex() for x in tpic], "CTDA_count", len(ctdas), "CTDA", [x.hex() for x in ctdas])
    for file in ("dlc2we09.raw.json", "dlc2we-priority.raw.json", "dlc2wenode.raw.json", "world-script-event.raw.json"):
        rows = records(TX / file)
        print(f"FILE {file} count={len(rows)}")
        for row in rows:
            print("RECORD", row.get("signature"), row.get("file_form_id"), row.get("editor_id"), "subrecords", [(x.get("signature"), x.get("hex")) for x in row.get("subrecords", []) if x.get("signature") in {"EDID", "CTDA", "VMAD", "SPIT", "SCTX", "SCRI", "NAME", "QNAM"}])

if __name__ == "__main__":
    main()
