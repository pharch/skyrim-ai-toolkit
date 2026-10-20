#!/usr/bin/env python3
"""Attest the College INFO and quest PEX sources used for the door-key route."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.papyrus_pex import configured_data_dir, extract_pex_from_bsa, parse_pex

EXPECTED_ARCHIVE_SHA256 = "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d"
SCRIPT_EXPECTATIONS = {
    "TIF__00107E3D": {
        "path": ROOT / ".local/alignment/transactions/TX-20261018-0010/TIF__00107E3D.pex",
        "sha256": "3caa0b429854825eae4ccffb6ea53e3175c0b585689e50929a8e762b12469e52",
    },
    "DialogueWinterholdCollegeQuestScript": {
        "path": ROOT / ".local/alignment/transactions/TX-20261018-0010/DialogueWinterholdCollegeQuestScript.pex",
        "sha256": "6a68c6fe40cbbd03dd7fae556f837a5f0e539948b76feb545a0e3d975811157e",
    },
    "QF_MG01_0001F251": {
        "path": ROOT / ".local/alignment/transactions/TX-20261018-0010/QF_MG01_0001F251.pex",
        "sha256": "7b5d5dd127752bb2ff34f8bec924ce3a58d6b65aacbea3dc8ae40360467e897d",
    },
    "QF_MG02_0001F252": {
        "path": ROOT / ".local/alignment/transactions/TX-20261018-0010/QF_MG02_0001F252.pex",
        "sha256": "3f4206bd0b690849d6f28f7b72262c507c34ba3a451a1f7fbe18385ba16fdcc4",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data_dir = configured_data_dir()
    archive = data_dir / "Skyrim - Misc.bsa"
    archive_hash = sha256(archive)
    if archive_hash != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("configured Skyrim - Misc.bsa hash differs from the extraction source")
    with archive.open("rb") as stream:
        header = stream.read(8)
    if header[:4] != b"BSA\0":
        raise ValueError("configured source does not have a BSA header")
    archive_version = struct.unpack_from("<I", header, 4)[0]

    scripts: dict[str, object] = {}
    loose_overrides: dict[str, object] = {}
    for name, expected in SCRIPT_EXPECTATIONS.items():
        pex_path: Path = expected["path"]  # type: ignore[assignment]
        pex_bytes = pex_path.read_bytes()
        pex_hash = hashlib.sha256(pex_bytes).hexdigest()
        if pex_hash != expected["sha256"]:
            raise ValueError(f"captured PEX hash changed for {name}")
        extracted, extraction = extract_pex_from_bsa(archive, name)
        if extracted != pex_bytes or extraction["archive_sha256"] != archive_hash:
            raise ValueError(f"captured PEX is not byte-identical to the stream in the verified archive: {name}")
        parsed = parse_pex(pex_bytes)
        getlevel_calls = [line for line in parsed["lines"] if "GetLevel" in line]
        scripts[name] = {
            "source": parsed["source"],
            "sha256": pex_hash,
            "size_bytes": pex_path.stat().st_size,
            "major": parsed["major"],
            "minor": parsed["minor"],
            "game_id": parsed["game_id"],
            "consumed_bytes": parsed["consumed_bytes"],
            "trailing_bytes": parsed["trailing_bytes"],
            "archive_stream": extraction,
            "getlevel_method_call_lines": getlevel_calls,
            "disassembly": parsed["lines"],
        }
        loose = data_dir / "Scripts" / f"{name}.pex"
        loose_overrides[name] = {
            "present": loose.is_file(),
            "size_bytes": loose.stat().st_size if loose.is_file() else None,
            "sha256": sha256(loose) if loose.is_file() else None,
        }

    result = {
        "capture": "exact configured-source attestation for the two PEX files linked by the College key INFO/owning quest",
        "archive": {
            "filename": archive.name,
            "private_source_path": str(archive),
            "size_bytes": archive.stat().st_size,
            "sha256": archive_hash,
            "bsa_version_header": archive_version,
        },
        "loose_overrides": loose_overrides,
        "scripts": scripts,
        "scope_limits": [
            "The archive is the configured base Skyrim - Misc.bsa source; no active-profile winner is established.",
            "The PEX reader is a bounded classic PEX 3.2 disassembler, not a complete decompiler.",
            "No runtime dialogue, quest-stage transition, inventory state, or physical door entry was observed.",
        ],
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    local_root = (ROOT / ".local").resolve()
    if output != local_root and local_root not in output.parents:
        raise ValueError("capture output must remain below ignored .local/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "archive_filename": archive.name,
        "archive_size_bytes": archive.stat().st_size,
        "archive_sha256": archive_hash,
        "bsa_version_header": archive_version,
        "loose_overrides": {name: value["present"] for name, value in loose_overrides.items()},
        "scripts": {
            name: {
                "source": value["source"],
                "size_bytes": value["size_bytes"],
                "sha256": value["sha256"],
                "archive_pex_offset": value["archive_stream"]["pex_offset"],
                "getlevel_method_call_count": len(value["getlevel_method_call_lines"]),
            }
            for name, value in scripts.items()
        },
        "output": output.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
