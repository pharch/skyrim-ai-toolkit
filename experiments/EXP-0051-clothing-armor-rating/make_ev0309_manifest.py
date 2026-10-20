#!/usr/bin/env python3
"""Hash EV-0309 private captures and reproducibility inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE_DIR = ROOT / ".local/alignment/transactions/TX-20261016-0044"
PRIVATE_FILES = (
    "armor-five-master-armo.stdout.raw",
    "clothing-armor-screen.stdout.raw",
    "clothing-armature-link-screen-v3.stdout.raw",
    "clothes-beggar-robes-reference-screen.stdout.raw",
    "beggar-outfit-reference-screen.stdout.raw",
    "brenuin-actor-reference-screen.stdout.raw",
    "brenuin-achr-record.stdout.raw",
    "cloth-beggar-armature.stdout.raw",
    "armor-factor-address-library-vtable-actor.stdout.raw",
    "armor-factor-address-library-vtable-playercharacter.stdout.raw",
    "armor-factor-vtable-query.stdout.raw",
    "armor-factor-playercharacter-vtable-query.stdout.raw",
    "EV-0309-note.md",
)
GHIDRA_FILES = (
    ".local/ghidra/gog-query-20261016T195321Z.meta.json",
    ".local/ghidra/gog-query-20261016T195321Z.stdout.raw",
    ".local/ghidra/gog-query-20261016T195524Z.meta.json",
    ".local/ghidra/gog-query-20261016T195524Z.stdout.raw",
)
PREPARED_MASTERS = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}
RESEARCH_INPUTS = (
    "experiments/EXP-0051-clothing-armor-rating/README.md",
    "experiments/EXP-0051-clothing-armor-rating/hypothesis.md",
    "experiments/EXP-0051-clothing-armor-rating/expected-discriminants.md",
    "experiments/EXP-0051-clothing-armor-rating/protocol.md",
    "experiments/EXP-0051-clothing-armor-rating/results.md",
    "experiments/EXP-0051-clothing-armor-rating/screen_clothing_armor.py",
    "experiments/EXP-0051-clothing-armor-rating/join_clothing_armature.py",
    "experiments/EXP-0051-clothing-armor-rating/scan_clothing_item_refs.py",
    "experiments/EXP-0051-clothing-armor-rating/make_ev0309_manifest.py",
    "tools/plugin_reader.py",
    "tools/ghidra_probe.py",
    "tools/address_library_probe.py",
    "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
    "scripts/python_env.py",
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def describe(path: Path) -> dict[str, object]:
    return {
        "artifact": path.relative_to(ROOT).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": digest(path),
    }


def main() -> int:
    private = []
    for relative in PRIVATE_FILES:
        path = CAPTURE_DIR / relative
        if path.is_file():
            private.append(describe(path))
    for relative in GHIDRA_FILES:
        path = ROOT / relative
        if path.is_file():
            private.append(describe(path))
    inputs = []
    for relative in RESEARCH_INPUTS:
        path = ROOT / relative
        if path.is_file():
            inputs.append({"artifact": relative, "sha256": digest(path)})
    manifest = {
        "evidence_id": "EV-0309",
        "transaction_id": "TX-20261016-0044",
        "source_scope": "five prepared official-master ARMO/ARMA and Outfit/NPC/reference screens plus read-only GOG AE 1.6.1179.0 vtable queries; no profile winner or live test",
        "prepared_master_sha256": PREPARED_MASTERS,
        "external_schema": {
            "url": "https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas",
            "revision": "TES5Edit dev-4.1.6",
            "lines": "2143-2147, 2220-2241, 2235-2276, 3879-3920",
        },
        "gog_analysis_binary": {
            "product_version": "1.6.1179.0",
            "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
            "address_library": "GOG-matched vtable IDs 207511 and 208040; slot 0xE7 queries",
        },
        "private_capture_files": private,
        "research_input_hashes": inputs,
        "not_included": [
            "machine-specific configured paths",
            "game save/co-save or live process data",
            "active plugin order or profile winner",
            "installed-Steam native mapping or runtime measurement",
        ],
    }
    destination = CAPTURE_DIR / "EV-0309-capture-manifest.json"
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": destination.relative_to(ROOT).as_posix(),
        "private_capture_count": len(private),
        "research_input_count": len(inputs),
        "manifest_sha256": digest(destination),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
