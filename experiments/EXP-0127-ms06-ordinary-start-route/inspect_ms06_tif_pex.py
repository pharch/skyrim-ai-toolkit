#!/usr/bin/env python3
"""Extract joined MS06 INFO TIF scripts from the supported base Misc BSA route."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.papyrus_pex import configured_data_dir, extract_pex_from_bsa, parse_pex


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--join", type=Path, required=True, help="captured EXP-0127 DIAL/INFO JSON")
    parser.add_argument("--output-dir", type=Path, required=True, help="capture directory under ignored .local/")
    args = parser.parse_args()
    join_path = args.join if args.join.is_absolute() else ROOT / args.join
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    local = (ROOT / ".local").resolve()
    out_dir = out_dir.resolve()
    if out_dir != local and local not in out_dir.parents:
        raise SystemExit("output directory must remain below ignored .local/")
    join = json.loads(join_path.read_text(encoding="utf-8"))
    join_hash = digest(join_path.read_bytes())
    scripts = sorted({name for copies in join["info_copies"].values()
                      for row in copies[-1:]
                      for name in row.get("tif_names", [])})

    archive = configured_data_dir() / "Skyrim - Misc.bsa"
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for script_name in scripts:
        item = {"script": script_name, "status": "unresolved"}
        try:
            payload, metadata = extract_pex_from_bsa(archive, script_name + ".psc")
            parsed = parse_pex(payload)
            pex_path = out_dir / (script_name + ".pex")
            pex_path.write_bytes(payload)
            disassembly = {
                "script": script_name,
                "archive": metadata["archive"],
                "archive_sha256": metadata["archive_sha256"],
                "source": parsed["source"],
                "pex_sha256": digest(payload),
                "pex_size": len(payload),
                "object_count": parsed["object_count"],
                "consumed_bytes": parsed["consumed_bytes"],
                "trailing_bytes": parsed["trailing_bytes"],
                "lines": parsed["lines"],
            }
            raw_path = out_dir / (script_name + ".disassembly.json")
            raw_path.write_text(json.dumps(disassembly, indent=2) + "\n", encoding="utf-8")
            interesting = [line for line in parsed["lines"]
                           if any(token in line.casefold() for token in
                                  ("setstage", "setcurrentstage", "startquest", "stop(", "callmethod [('id', 'start'"))]
            item.update({
                "status": "extracted",
                "metadata": metadata,
                "pex_path": str(pex_path.relative_to(ROOT)),
                "pex_sha256": digest(payload),
                "disassembly_path": str(raw_path.relative_to(ROOT)),
                "disassembly_sha256": digest(raw_path.read_bytes()),
                "interesting_call_lines": interesting,
                "object_count": parsed["object_count"],
                "trailing_bytes": parsed["trailing_bytes"],
            })
        except (OSError, ValueError, UnicodeError) as exc:
            item["status"] = "not_available_by_supported_base_misc_route"
            item["error"] = f"{type(exc).__name__}: {exc}"
        results.append(item)

    output = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "join_path": str(join_path.relative_to(ROOT)),
        "join_sha256": join_hash,
        "archive": archive.name,
        "archive_size": archive.stat().st_size,
        "archive_sha256": archive_hash,
        "route": "tools.papyrus_pex.extract_pex_from_bsa and parse_pex; base Skyrim - Misc.bsa only; classic PEX 3.2 subset",
        "script_count": len(scripts),
        "results": results,
        "coverage_limit": "A missing entry means only that this supported uncompressed-stream route did not recover it from Skyrim - Misc.bsa. It does not establish absence from other archives, loose files, source packages, or the active profile.",
    }
    manifest = out_dir / "ms06-tif-pex-index.json"
    manifest.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest.relative_to(ROOT)),
                      "sha256": digest(manifest.read_bytes()),
                      "archive_sha256": archive_hash,
                      "script_count": len(scripts),
                      "extracted": sum(r["status"] == "extracted" for r in results),
                      "unavailable_by_route": sum(r["status"] != "extracted" for r in results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
