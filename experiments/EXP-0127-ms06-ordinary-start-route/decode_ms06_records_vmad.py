#!/usr/bin/env python3
"""Decode retained MS06 QUST, REFR, and SCEN VMAD with the EXP-0043 reader."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
DECODER = ROOT / "experiments" / "EXP-0043-da04-helper-versus-main-start" / "decode_qust_vmad.py"
spec = importlib.util.spec_from_file_location("exp0043_vmad", DECODER)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
Reader = module.Reader
decode_qust_vmad = module.decode_vmad
read_script = module.read_script


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_ref_vmad(hex_data: str, *, allow_trailing: bool = False) -> dict:
    reader = Reader(bytes.fromhex(hex_data))
    version, object_format, count = reader.u16(), reader.u16(), reader.u16()
    scripts = [read_script(reader, object_format) for _ in range(count)]
    tail = reader.data[reader.offset:]
    if tail and not allow_trailing:
        raise ValueError(f"{len(reader.data) - reader.offset} unparsed reference VMAD bytes")
    return {
        "version": version,
        "object_format": object_format,
        "scripts": scripts,
        "unparsed_record_specific_tail_hex": tail.hex(),
    }


def records(path: Path) -> list[dict]:
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    return [json.loads(line) for line in wrapper.get("records_jsonl", "").splitlines() if line.strip()]


def decode_ctda(hex_data: str) -> dict:
    raw = bytes.fromhex(hex_data)
    if len(raw) != 32:
        return {"raw_hex": hex_data, "length": len(raw), "decoded": False}
    return {
        "raw_hex": hex_data,
        "flags_byte": raw[0],
        "operator_byte": raw[1],
        "comparison_float": struct.unpack_from("<f", raw, 4)[0],
        "function_index_u16": struct.unpack_from("<H", raw, 8)[0],
        "param1_u32": struct.unpack_from("<I", raw, 12)[0],
        "param2_u32": struct.unpack_from("<I", raw, 16)[0],
        "run_on_u32": struct.unpack_from("<I", raw, 20)[0],
        "reference_u32": struct.unpack_from("<I", raw, 24)[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    txdir = args.transaction_dir if args.transaction_dir.is_absolute() else ROOT / args.transaction_dir
    output = args.output if args.output.is_absolute() else ROOT / args.output
    local = (ROOT / ".local").resolve()
    output = output.resolve()
    if output != local and local not in output.parents:
        raise SystemExit("output must remain below ignored .local/")

    inputs = [
        "ms06-skyrim-qust.json",
        "ms06-update-qust.json",
        "ms06-start-helper-skyrim-qust.json",
        "ms06-start-helper-update-qust.json",
    ] + [f"ms06-ref-{form}.json" for form in
         ("00108A62", "00099D27", "00099D25", "00099D24", "00097E23")]
    inputs += [f"ms06-scen-{form}.json" for form in
               ("00096555", "0009655F", "00096560", "00098894",
                "0009DA27", "0009DA28", "00108A65")]
    decoded = []
    hashes = {}
    for name in inputs:
        path = txdir / name
        hashes[name] = digest(path)
        for record in records(path):
            vmads = [item["hex"] for item in record.get("subrecords", []) if item.get("signature") == "VMAD"]
            parsed = [
                decode_qust_vmad(raw) if record["signature"] == "QUST"
                else decode_ref_vmad(raw, allow_trailing=record["signature"] == "SCEN")
                for raw in vmads
            ]
            decoded.append({
                "capture": name,
                "capture_sha256": hashes[name],
                "signature": record["signature"],
                "plugin": record.get("plugin"),
                "origin_plugin": record.get("origin_plugin"),
                "form_id": record.get("file_form_id"),
                "editor_id": record.get("editor_id"),
                "record_offset": record.get("offset"),
                "conditions": [decode_ctda(item["hex"]) for item in record.get("subrecords", [])
                               if item.get("signature") == "CTDA"],
                "vmad": parsed,
            })
    result = {
        "decoder": str(DECODER.relative_to(ROOT)),
        "decoder_sha256": digest(DECODER),
        "coverage": "Four retained direct-parser QUST copies, five exact Skyrim.esm REFR records, and seven exact Skyrim.esm SCEN records; decode schema from EXP-0043/TES5Edit dev-4.1.6",
        "inputs": hashes,
        "records": decoded,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "sha256": digest(output),
                      "record_count": len(decoded), "input_hashes": hashes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
