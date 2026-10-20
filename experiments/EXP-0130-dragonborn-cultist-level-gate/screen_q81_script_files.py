#!/usr/bin/env python3
"""Check only known loose Papyrus paths and capture Dragonborn.bsa identity."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.papyrus_pex import configured_data_dir

SCRIPT_STEMS = (
    "DLC2_QF_DLC2CultistAmbush_0203546D",
    "DLC2WE09ActorScript",
    "DLC2WECultistAmbushPlayerScript",
    "DLC2_QF_DLC2WE09_020331C0",
)
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-script-file-screen.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    data_dir = configured_data_dir()
    candidate_dirs = {
        "loose_pex": [data_dir / "Scripts"],
        "loose_source": [data_dir / "Source" / "Scripts", data_dir / "Scripts" / "Source"],
    }
    scripts: dict[str, dict[str, object]] = {}
    for stem in SCRIPT_STEMS:
        scripts[stem] = {}
        for category, suffix in (("loose_pex", ".pex"), ("loose_source", ".psc")):
            matches = [directory / f"{stem}{suffix}" for directory in candidate_dirs[category]
                       if (directory / f"{stem}{suffix}").is_file()]
            scripts[stem][category] = [
                {"relative": path.relative_to(data_dir).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in matches
            ]

    archive = data_dir / "Dragonborn.bsa"
    archive_info: dict[str, object] = {"filename": archive.name, "present": archive.is_file()}
    if archive.is_file():
        with archive.open("rb") as stream:
            header = stream.read(8)
        archive_info.update({
            "size_bytes": archive.stat().st_size,
            "sha256": sha256(archive),
            "magic": header[:4].decode("ascii", errors="replace"),
            "version_u32": struct.unpack("<I", header[4:8])[0] if len(header) == 8 else None,
        })

    result = {
        "scope": "configured Steam Skyrim AE Data directory; exact private path omitted",
        "query_script_stems": list(SCRIPT_STEMS),
        "loose_script_results": scripts,
        "archive": archive_info,
        "tool_route": "read-only path/hash inventory; no archive contents were extracted or modified",
        "interpretation_limit": "No loose PEX/source file does not imply absence from an archive. The documented papyrus_pex extractor targets Skyrim - Misc.bsa and is not a general BSA extractor.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
