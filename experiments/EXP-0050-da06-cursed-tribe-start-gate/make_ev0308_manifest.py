#!/usr/bin/env python3
"""Hash EV-0308 private captures and reproducibility inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_ROOTS = (
    ROOT / ".local/alignment/transactions/TX-20261016-0043",
    ROOT / ".local/TX0043",
)
PREPARED_MASTERS = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}
RESEARCH_INPUTS = (
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/README.md",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/hypothesis.md",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/predicted-outcomes.md",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/protocol.md",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/join_da06_dialogue.py",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/decode_da06_vmad.py",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/inspect_trigger_references.py",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/make_ev0308_manifest.py",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/summarize_da06_aliases.py",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/summarize_reference_scan.py",
    ROOT / "experiments/EXP-0050-da06-cursed-tribe-start-gate/summarize_trigger_context.py",
    ROOT / "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py",
    ROOT / "experiments/EXP-0049-da13-dialogue-start-gate/scan_formids.py",
    ROOT / "tools/plugin_reader.py",
    ROOT / "scripts/python_env.py",
)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    private_files = []
    for root in PRIVATE_ROOTS:
        if not root.is_dir():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            private_files.append({
                "artifact": path.relative_to(ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
            })
    inputs = []
    for path in RESEARCH_INPUTS:
        if path.is_file():
            inputs.append({
                "artifact": path.relative_to(ROOT).as_posix(),
                "sha256": digest(path),
            })
    manifest = {
        "evidence_id": "EV-0308",
        "transaction_id": "TX-20261016-0043",
        "source_scope": "prepared five official master records plus Skyrim - Misc.bsa classic PEX extracts; no profile winner",
        "prepared_master_sha256": PREPARED_MASTERS,
        "private_capture_files": private_files,
        "research_input_hashes": inputs,
        "not_included": [
            "machine-specific configured paths",
            "game save/co-save or live process data",
            "active plugin order or profile winner",
        ],
    }
    destination = ROOT / ".local/alignment/transactions/TX-20261016-0043/EV-0308-capture-manifest.json"
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": destination.relative_to(ROOT).as_posix(),
        "private_capture_count": len(private_files),
        "research_input_count": len(inputs),
        "manifest_sha256": digest(destination),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
