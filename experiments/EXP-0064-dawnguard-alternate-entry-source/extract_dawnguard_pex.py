#!/usr/bin/env python3
"""Probe the narrow validated PEX stream reader against Dawnguard.bsa."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.papyrus_pex import configured_data_dir, extract_pex_from_bsa, parse_pex

TX = ROOT / ".local/alignment/transactions/TX-20261017-0010"
OUT = TX / "dawnguard-pex-probe"
BASE_SCRIPTS = [
    "defaultsetstagealiasscript",
    "DLC1VQ01BookScript",
    "DLC1VQ01SeranaScript",
    "DLC1VQ01TolanScript",
    "DLC1_QF_DLC1VQ00ChangeLocatio_0100D90B",
    "QF_DLC01VQ01_0100352A",
    "DLC1_QF_DLC1VQ01MiscObjective_0100D06C",
    "DLC1_QF_DLC1VQ00_0100D90E",
    "DLC1_QF_DLC1VQCastleGuard_0101A415",
]
TARGET_QUESTS = {"0200352A", "0200D06C", "0200D90E", "0201A415"}


def linked_scripts() -> list[str]:
    names = set(BASE_SCRIPTS)
    callback_map = TX / "dawnguard-vq-topic-callbacks.json"
    if not callback_map.is_file():
        raise FileNotFoundError("run trace_dawnguard_topics.py before extracting linked callbacks")
    data = json.loads(callback_map.read_text(encoding="utf-8"))
    for topic in data["topics"]:
        if topic["quest_form_id"] not in TARGET_QUESTS:
            continue
        for info in topic["info_children"]:
            names.update(name for name in info["scripts"] if name.casefold().startswith("dlc1_tif_"))
    return sorted(names)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data_dir = configured_data_dir()
    requested_archive = data_dir / "Dawnguard.bsa"
    archive = requested_archive if requested_archive.is_file() else data_dir / "Skyrim - Misc.bsa"
    archive_present = requested_archive.is_file()
    archive_size = archive.stat().st_size
    archive_bytes = archive.read_bytes()
    header = archive_bytes[:36]
    if len(header) < 36 or header[:4] != b"BSA\0":
        raise ValueError("selected BSA has no complete BSA header")
    version, offset, flags, folder_count, file_count, folder_names, file_names = struct.unpack_from("<7I", header, 4)
    file_flags = struct.unpack_from("<H", header, 32)[0]
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    script_names = linked_scripts()

    results = []
    for script in script_names:
        row = {"script": script}
        try:
            payload, meta = extract_pex_from_bsa(archive, script)
            parsed = parse_pex(payload)
            output = OUT / (script + ".pex")
            output.write_bytes(payload)
            disassembly = OUT / (script + ".txt")
            disassembly.write_text("\n".join(parsed["lines"]) + "\n", encoding="utf-8")
            row.update({
                "status": "extracted",
                "archive_relative_name": meta["archive"],
                "archive_sha256": meta["archive_sha256"],
                "source": meta["source"],
                "source_string_offset": meta["source_string_offset"],
                "pex_offset": meta["pex_offset"],
                "pex_end_offset": meta["pex_end_offset"],
                "pex_size": meta["pex_size"],
                "parsed_bytes": meta["parsed_bytes"],
                "trailing_bytes": meta["trailing_bytes"],
                "output": output.relative_to(ROOT).as_posix(),
                "output_sha256": hashlib.sha256(payload).hexdigest(),
                "disassembly": disassembly.relative_to(ROOT).as_posix(),
                "pex_version": f"{parsed['major']}.{parsed['minor']}",
                "game_id": parsed["game_id"],
                "compiled_timestamp": parsed["compiled"],
                "object_count": parsed["object_count"],
                "disassembly_lines": len(parsed["lines"]),
            })
        except (FileNotFoundError, ValueError, OSError, struct.error) as exc:
            row.update({"status": "probe_miss_or_unsupported", "error_type": type(exc).__name__, "error": str(exc)})
        row["tested_archive"] = archive.name
        results.append(row)

    result = {
        "scope": "Narrow byte-string PEX stream extractor experiment. Dawnguard.bsa is tested if present; otherwise the validated Skyrim - Misc.bsa route is probed only as a possible alternate container. Misses are not negatives on script existence or behavior.",
        "archive": {
            "name": archive.name,
            "requested_dawnguard_bsa_present": archive_present,
            "size_bytes": archive_size,
            "sha256": archive_hash,
            "bsa_version": version,
            "archive_offset": offset,
            "archive_flags": flags,
            "folder_count": folder_count,
            "file_count": file_count,
            "folder_name_bytes": folder_names,
            "file_name_bytes": file_names,
            "file_flags": file_flags,
        },
        "extractor": "tools.papyrus_pex.extract_pex_from_bsa + tools.papyrus_pex.parse_pex",
        "requested_scripts": script_names,
        "results": results,
    }
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": manifest.relative_to(ROOT).as_posix(),
        "archive": {key: value for key, value in result["archive"].items() if key != "sha256"} | {"sha256": result["archive"]["sha256"]},
        "results": [{"script": row["script"], "status": row["status"], "error": row.get("error"), "output": row.get("output"), "output_sha256": row.get("output_sha256")} for row in results],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
