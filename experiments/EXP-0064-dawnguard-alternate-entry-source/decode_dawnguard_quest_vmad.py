#!/usr/bin/env python3
"""Decode Dawnguard QUST VMAD fragment/alias tables with the pinned reader."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / ".local/alignment/transactions/TX-20261016-0033/dawnguard-vq-quests.json"
NEW = ROOT / ".local/alignment/transactions/TX-20261017-0010"
INPUTS = [OLD, NEW / "qust-00D06C.json", NEW / "qust-01A415.json"]
WANTED = {"0200D90E", "0200352A", "0200D06C", "0201A415"}
OUTPUT = NEW / "dawnguard-quest-vmad-summary.json"
DECODER = ROOT / "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py"

def load_decoder():
    spec = importlib.util.spec_from_file_location("dawnguard_qust_vmad_reader", DECODER)
    if spec is None or spec.loader is None:
        raise RuntimeError("pinned QUST VMAD reader is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_vmad

def records(path: Path):
    outer = json.loads(path.read_text(encoding="utf-8"))
    if "records_jsonl" in outer:
        yield from (json.loads(line) for line in outer["records_jsonl"].splitlines() if line.strip())
    else:
        yield outer

def main() -> int:
    decode_vmad = load_decoder()
    rows = {}
    for path in INPUTS:
        for row in records(path):
            if row.get("signature") == "QUST" and row.get("file_form_id") in WANTED:
                rows[row["file_form_id"]] = (path, row)
    missing = WANTED - rows.keys()
    if missing:
        raise SystemExit(f"missing QUST captures: {sorted(missing)}")
    results = []
    for form_id, (path, row) in sorted(rows.items()):
        vmad_hex = next(field["hex"] for field in row["subrecords"] if field["signature"] == "VMAD")
        vmad = decode_vmad(vmad_hex)
        stages = [int.from_bytes(bytes.fromhex(field["hex"]), "little") for field in row["subrecords"] if field["signature"] == "INDX" and len(field["hex"]) == 8]
        results.append({
            "form_id": form_id,
            "editor_id": row["editor_id"],
            "source_capture": path.relative_to(ROOT).as_posix(),
            "vmad_file_name": vmad["file_name"],
            "stage_table_ids": stages,
            "fragments": vmad["fragments"],
            "quest_scripts": [{"name": script["name"], "properties": script["properties"]} for script in vmad["scripts"]],
            "alias_scripts": [{"alias_id": alias["alias_id"], "target_form_id": f"{alias['form_id']:08X}", "scripts": [script["name"] for script in alias["scripts"]]} for alias in vmad["aliases"]],
            "parser_consumed_bytes": len(bytes.fromhex(vmad_hex)),
        })
    OUTPUT.write_text(json.dumps({"results": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "quests": [{
        "form_id": row["form_id"], "editor_id": row["editor_id"], "vmad": row["vmad_file_name"],
        "stages": row["stage_table_ids"], "fragments": row["fragments"],
        "alias_scripts": row["alias_scripts"]} for row in results]}, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
