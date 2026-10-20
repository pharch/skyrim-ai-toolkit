#!/usr/bin/env python3
"""Decode the captured DA03Start QUST VMAD with the existing schema reader."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/xedit-bridge/20261017T190659.316267Z/stdout.raw"
DECODER = ROOT / "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-vmad.json"


def main() -> int:
    spec = importlib.util.spec_from_file_location("qust_vmad_decoder", DECODER)
    if spec is None or spec.loader is None:
        raise SystemExit("existing schema-ordered QUST VMAD decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = json.loads(SOURCE.read_text(encoding="utf-8"))
    if record.get("signature") != "QUST" or record.get("file_form_id") != "000D7939" or record.get("editor_id") != "DA03Start":
        raise ValueError("captured record is not the expected DA03Start source record")
    vmad_hex = next(item["hex"] for item in record["subrecords"] if item["signature"] == "VMAD")
    decoded = module.decode_vmad(vmad_hex)
    alias_names: dict[int, str] = {}
    quest_aliases: list[dict] = []
    current_alias: int | None = None
    current: dict | None = None
    for subrecord in record["subrecords"]:
        signature = subrecord["signature"]
        raw = bytes.fromhex(subrecord["hex"])
        if signature in {"ALST", "ALLS"}:
            if current is not None:
                quest_aliases.append(current)
            current_alias = int.from_bytes(bytes.fromhex(subrecord["hex"]), "little")
            current = {
                "alias_id": current_alias,
                "alias_kind": "reference" if signature == "ALST" else "location",
                "alias_name": "",
                "fields": [],
            }
        if current is not None:
            field = {"signature": signature, "hex": raw.hex(), "length": len(raw)}
            if signature == "ALID":
                field["text_cp1252"] = raw.rstrip(b"\0").decode("cp1252", "replace")
                current["alias_name"] = field["text_cp1252"]
                alias_names[current_alias] = field["text_cp1252"]
            if signature in {"ALUA", "ALFR", "ALCO", "ALPC", "ALFE", "ALFD", "ALFL", "ALCA", "ALCL", "ALNA", "ALNT", "ALDN"} and len(raw) == 4:
                field["value_u32"] = int.from_bytes(raw, "little")
                field["value_hex_u32"] = f"{field['value_u32']:08X}"
            current["fields"].append(field)
    if current is not None:
        quest_aliases.append(current)
    result = {
        "source_capture": ".local/alignment/xedit-bridge/20261017T190659.316267Z/stdout.raw",
        "source_sha256": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
        "form_id": record["file_form_id"],
        "editor_id": record["editor_id"],
        "decoder": "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py / TES5Edit dev-4.1.6 VMAD schema order",
        "version": decoded["version"],
        "object_format": decoded["object_format"],
        "file_name": decoded["file_name"],
        "fragments": decoded["fragments"],
        "aliases": [
            {"alias_id": alias["alias_id"], "alias_name": alias_names.get(alias["alias_id"], ""),
             "form_id": f"{alias['form_id']:08X}", "scripts": alias["scripts"]}
            for alias in decoded["aliases"]
        ],
        "quest_aliases": quest_aliases,
        "scripts": decoded["scripts"],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "fragment_count": len(result["fragments"]),
        "vmad_alias_script_count": len(result["aliases"]),
        "fragment_links": result["fragments"],
        "quest_aliases": [{"alias_id": alias["alias_id"], "alias_name": alias["alias_name"], "alias_kind": alias["alias_kind"]} for alias in quest_aliases],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
