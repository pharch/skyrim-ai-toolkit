#!/usr/bin/env python3
"""Preserve the four attached Dragonborn Papyrus source files under .local."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.papyrus_pex import configured_data_dir

EXPECTED = {
    "DLC2_QF_DLC2CultistAmbush_0203546D.psc": (3049, "f8db4cafaedf0f4f270ac5662b5ad6505745b1f4a79e6712fe8611137ed848ae"),
    "DLC2WE09ActorScript.psc": (672, "21c787fe2e67e4f842afcc34a47f1a3ae22508bd11d899b10746ba9eecc342bb"),
    "DLC2WECultistAmbushPlayerScript.psc": (1253, "db724f3148c4f842cf1270b4cbbee5bce809416e79799f2b6502bd7a5a9bdd4d"),
    "DLC2_QF_DLC2WE09_020331C0.psc": (5033, "65d2bf1fa1dbd63b73a1483c52b55525d24cb72f8bdc1e61aad337666b545b95"),
}
OUTPUT_DIR = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-psc-source"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    source_dir = configured_data_dir() / "Source" / "Scripts"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for name, (expected_size, expected_hash) in EXPECTED.items():
        source = source_dir / name
        data = source.read_bytes()
        actual_hash = digest(data)
        if len(data) != expected_size or actual_hash != expected_hash:
            raise SystemExit(f"source changed since inventory capture: {name}")
        local = OUTPUT_DIR / name
        local.write_bytes(data)
        files.append({
            "archive_relative_source": f"Source/Scripts/{name}",
            "private_path_emitted": False,
            "size_bytes": len(data),
            "sha256": actual_hash,
            "capture": str(local.relative_to(ROOT)),
        })
    manifest = {
        "source_scope": "configured Steam Skyrim AE Data/Source/Scripts; exact private Data path omitted",
        "source_runtime_identity": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0 is independently verified by EV-0109; this does not prove the loose source matches active PEX bytes or a profile winner",
        "files": files,
        "capture_method": "read-only byte copy into ignored .local; no game source or plugin changed",
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
