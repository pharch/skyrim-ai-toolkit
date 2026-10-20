#!/usr/bin/env python3
"""Register the revision-pinned TES5Edit CTDA Type decoder source."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research/EVIDENCE.json"
NOTE = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-ctda-type-schema-note.json"
SOURCE = "https://github.com/TES5Edit/TES5Edit/blob/f8b209cb5bc9efcb2cd8c4aa8694de3227c3d783/Core/wbDefinitionsCommon.pas#L3254-L3332"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    evidence = json.loads((ROOT / "research/EVIDENCE.json").read_text(encoding="utf-8"))
    known = {item["id"] for item in evidence["items"]}
    if not {"EV-0657", "EV-0665"} <= known:
        raise SystemExit("native and direct raw condition evidence must be registered first")
    note = {
        "source_url": SOURCE,
        "repository_revision": "TES5Edit/TES5Edit commit f8b209cb5bc9efcb2cd8c4aa8694de3227c3d783 on dev-4.1.6",
        "accessed_utc": datetime.now(timezone.utc).isoformat(),
        "source_function": "wbConditionTypeToStr",
        "decoder_summary": {
            "operator_bits": "aInt & 0xE0",
            "0x60": "Greater Than Or Equal To",
            "flag_bit_0": "Or",
            "xedit_native_type_11010000": "operator GE plus flag bit 0",
        },
        "paired_record_bytes": {"evidence_id": "EV-0665", "GetLevel_type_byte": "0x61", "comparison": 25.0, "GetInCurrentLoc_type_byte": "0x01", "comparison_location_row": 1.0},
        "scope_note": "TES5Edit source schema cross-check; the captured native reader was SSEView 4.1.5f and no claim is made that this source file is the binary's exact build source. The decoder resolves Type encoding, not runtime CTDA list grouping.",
    }
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    NOTE.write_text(json.dumps(note, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if "EV-0666" in known:
        raise SystemExit("EV-0666 already exists; refusing duplicate registration")
    evidence["items"].append({
        "id": "EV-0666", "kind": "source",
        "source": "TES5Edit/TES5Edit TES5 condition type decoder, revision-pinned to commit f8b209cb5bc9efcb2cd8c4aa8694de3227c3d783, function wbConditionTypeToStr.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261019-0002/q81-ctda-type-schema-note.json",
        "sha256": digest(NOTE), "captured_utc": datetime.now(timezone.utc).isoformat(),
        "edition": "AE", "runtime": "External TES5Edit source schema at the linked commit; not an in-game runtime or an exact SSEView 4.1.5f source checkout.",
        "modified_state": False, "lane": "offline",
        "tools": ["web open of TES5Edit/TES5Edit Core/wbDefinitionsCommon.pas at commit f8b209cb5bc9efcb2cd8c4aa8694de3227c3d783", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0666_tes5edit_ctda_type_schema.py"],
        "coverage": "The TES5-specific xEdit callback masks CTDA operator bits with 0xE0 and decodes 0x60 as Greater Than Or Equal To; low bit 0 is the Or flag. Paired with EV-0665 raw byte 0x61 and EV-0657's native Type rendering, this decodes GetLevel as >=25 with Or set and the following location predicate as Or-set. This source resolves encoding, not the engine's condition-list grouping/evaluation.",
        "result": "PASS for source-backed CTDA Type decoding. The threshold operator is GE and the OR flag is present; actual list semantics and quest-start behavior remain under investigation.",
        "related_evidence": ["EV-0657", "EV-0665"],
    })
    LEDGER.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0666", "artifact_sha256": digest(NOTE), "source": SOURCE, "decoded": note["decoder_summary"]}, indent=2))


if __name__ == "__main__":
    main()
