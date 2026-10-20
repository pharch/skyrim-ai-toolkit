#!/usr/bin/env python3
"""Decode the captured Q89 selector-0x55 PERK rows and bounded effect links."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CAPTURE_DIR = ROOT / ".local/alignment/transactions/TX-20261020-0008/q89"
PERK_CAPTURE = CAPTURE_DIR / "skyrim-esm-perk-entrypoints-20261020T052517Z.json"
LINK_CAPTURE = CAPTURE_DIR / "zeroing-perk-effect-chain.json"
OUT = CAPTURE_DIR / "q89-selector-analysis.json"
XEDIT_RESULTS = {
    "Dragonhide": ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T053708.253619Z/native-result.json",
    "EarthStone": ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T054328.751963Z/native-result.json",
}

FUNCTION_NAMES = {1: "SetValue", 3: "Multiply"}
DATA_TYPE_NAMES = {1: "OneValue"}
CTDA_FUNCTIONS = {214: "HasMagicEffect"}
COMPARISONS = {0x0: "=", 0x2: "!=", 0x4: ">", 0x6: ">=", 0x8: "<", 0xA: "<="}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_ctda(hex_value: str) -> dict[str, object]:
    raw = bytes.fromhex(hex_value)
    if len(raw) != 32:
        return {"raw_hex": hex_value, "length": len(raw), "decoded": False}
    flags = raw[0]
    function_index = struct.unpack_from("<H", raw, 8)[0]
    use_global = bool(flags & 0x04)
    param1 = struct.unpack_from("<I", raw, 12)[0]
    param2 = struct.unpack_from("<I", raw, 16)[0]
    run_on = struct.unpack_from("<I", raw, 20)[0]
    reference = struct.unpack_from("<I", raw, 24)[0]
    cmp_code = (flags >> 4) & 0x0F
    return {
        "raw_hex": hex_value,
        "operator": COMPARISONS.get(cmp_code, f"unknown:0x{cmp_code:X}"),
        "or_flag": bool(flags & 1),
        "use_global": use_global,
        "comparison_float": None if use_global else struct.unpack_from("<f", raw, 4)[0],
        "function_index": function_index,
        "function_name_from_schema": CTDA_FUNCTIONS.get(function_index, f"unknown:{function_index}"),
        "param1_u32": param1,
        "param1_form_id": f"{param1:08X}",
        "param2_u32": param2,
        "run_on": run_on,
        "reference_form_id": f"{reference:08X}",
    }


def decode_entry(row: dict[str, object]) -> dict[str, object]:
    data = bytes.fromhex(str(row["data_hex"]))
    handler = data[1] if len(data) > 1 else None
    epft_hex = row.get("entry_function_type_hex")
    epfd_hex = row.get("entry_function_data_hex")
    epft = int(str(epft_hex), 16) if epft_hex else None
    epfd_raw = bytes.fromhex(str(epfd_hex)) if epfd_hex else b""
    epfd_float = struct.unpack("<f", epfd_raw)[0] if len(epfd_raw) == 4 else None
    conditions = [
        decode_ctda(item["value_hex"])
        for item in row.get("entry_subrecords", [])
        if item.get("signature") == "CTDA"
    ]
    return {
        "plugin": row["plugin"],
        "form_id": row["file_form_id"],
        "editor_id": row["editor_id"],
        "entry_data_hex": row["data_hex"],
        "selector_id": data[0] if data else None,
        "handler_id_data_byte_1": handler,
        "handler_name_from_prior_gog_capture": FUNCTION_NAMES.get(handler, f"unknown:{handler}"),
        "entry_data_tail_hex": data[2:].hex(),
        "entry_function_type_hex": epft_hex,
        "entry_function_type": DATA_TYPE_NAMES.get(epft, f"unknown:{epft}"),
        "entry_function_data_hex": epfd_hex,
        "entry_function_data_float": epfd_float,
        "conditions": conditions,
    }


def main() -> int:
    perk_raw = PERK_CAPTURE.read_bytes()
    perk = json.loads(perk_raw)
    link_raw = LINK_CAPTURE.read_bytes()
    links = json.loads(link_raw)
    entries = [decode_entry(row) for row in perk["entries"]]
    zero_rows = [row for row in entries if row["handler_id_data_byte_1"] == 1]
    multiplier_rows = [row for row in entries if row["handler_id_data_byte_1"] == 3]
    values = [row["entry_function_data_float"] for row in multiplier_rows]
    direct_ref_map = {
        "DragonhideSpellPerk": {"mgef": "000CDB75", "spell": "000CDB70", "scroll": "000E0CD6"},
        "DLC2StandingStoneEarthPerk": {"mgef": "0201DFA0", "spell": "0201DF9F"},
        "dlc2BBDrunkenMaster": {"five_master_raw_form_id_references": 0},
    }
    ref_mges = {
        match["record_form_id"]: match
        for match in links["matches"]
        if match["record_signature"] == "MGEF" and match["subrecord_signature"] == "DATA"
    }
    xedit_mgefs = {}
    for label, path in XEDIT_RESULTS.items():
        native = json.loads(path.read_text(encoding="utf-8"))
        record = native["record"]
        if native.get("loader_status") != "Background Loader: finished":
            raise SystemExit(f"native xEdit loader incomplete for {label}")
        if record.get("signature") != "MGEF":
            raise SystemExit(f"native xEdit record signature mismatch for {label}")
        if record.get("source_plugin") != ("Skyrim.esm" if label == "Dragonhide" else "Dragonborn.esm"):
            raise SystemExit(f"native xEdit source plugin mismatch for {label}")
        if record.get("editor_id") != (
            "ArmorFFSelf100" if label == "Dragonhide" else "DLC2StandingStonesEarthEffect"
        ):
            raise SystemExit(f"native xEdit EditorID mismatch for {label}")
        key_fields = [
            field for field in native.get("fields", [])
            if field.get("field_path", "").endswith((":Archtype", ":Actor Value", ":Perk to Apply"))
        ]
        xedit_mgefs[label] = {
            "record": record,
            "loaded_plugins": native["plugins"],
            "loaded_files": native["loaded_files"],
            "native_master_hashes": native["native_data_files"],
            "field_count": native["field_count"],
            "fields": key_fields,
            "native_result_sha256": digest(path),
            "native_tsv_sha256": digest(path.parent / "native-records.tsv"),
            "native_tsv_path": (path.parent / "native-records.tsv").relative_to(ROOT).as_posix(),
        }
    result = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "Complete PERK record parse across configured official five masters; source-file rows only, not profile winners, Creation Club, or runtime behavior.",
        "input_artifacts": {
            "perk_capture": {"path": str(PERK_CAPTURE.relative_to(ROOT)), "sha256": digest(PERK_CAPTURE)},
            "effect_link_capture": {"path": str(LINK_CAPTURE.relative_to(ROOT)), "sha256": digest(LINK_CAPTURE)},
        },
        "official_master_sha256": perk["plugin_sha256"],
        "coverage": perk["coverage"],
        "decoded_row_count": len(entries),
        "handler_id_counts": {"1_SetValue": len(zero_rows), "3_Multiply": len(multiplier_rows)},
        "entry_function_type_counts": {
            "1_OneValue": sum(row["entry_function_type_hex"] == "01" for row in entries),
            "other": sum(row["entry_function_type_hex"] != "01" for row in entries),
        },
        "zero_setting_rows": zero_rows,
        "multiplier_data_summary": {
            "count": len(values),
            "all_finite": all(value is not None for value in values),
            "all_positive": all(value is not None and value > 0.0 for value in values),
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None,
        },
        "direct_effect_chain_screen": {
            "record_capture_sha256": digest(LINK_CAPTURE),
            "identified_source_rows": direct_ref_map,
            "mgef_records_with_perk_form_id_in_DATA": ref_mges,
            "limitation": "Raw FormID references plus direct record identities; this summary does not claim active-effect lifetime, player availability, or profile-specific winners.",
        },
        "native_xedit_mgef_schema_crosscheck": {
            "route": "SSEView 4.1.5f native read-only five-master view; not a profile override query",
            "records": xedit_mgefs,
            "load_order_scope": ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"],
        },
        "all_decoded_rows": entries,
        "schema_sources": {
            "selector_0x55": "CommonLibSSE source commit b93280e832f263dbef44e44cbe2936622a02f91a, include/RE/B/BGSEntryPoint.h line 98: kModArmorRating (capture preserved separately in commonlib-entrypoint-selector.stdout.raw).",
            "condition_index_214": "TES5Edit dev-4.1.6 Core/wbDefinitionsTES5.pas line 2786: HasMagicEffect, ParamType1=ptMagicEffect; source URL https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas#L2786.",
            "condition_decode_limit": "The Earth Stone selector-0x55 SetValue row encodes HasMagicEffect(MGEF 000CDB75) == 0.0; the paired selector-0x24 multiplier row also has one matching CTDA. Interpreting equality with zero as effect absence relies on the condition function's boolean semantics and is not a runtime observation.",
        },
        "negative_numeric_scope": "No negative handler-3 EPFD values occur in the 28 matching official source rows; three handler-1 rows carry SetValue 0.0. This says nothing about third-party plugins, dynamic entries, unscanned packages, or runtime float state.",
    }
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    OUT.write_text(encoded, encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "output": str(OUT.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "coverage": result["coverage"],
        "handler_id_counts": result["handler_id_counts"],
        "multiplier_data_summary": result["multiplier_data_summary"],
        "zero_setting_rows": [
            {"plugin": row["plugin"], "form_id": row["form_id"], "editor_id": row["editor_id"],
             "conditions": row["conditions"]}
            for row in zero_rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
