#!/usr/bin/env python3
"""Refresh local hashes after applying the validator-required H1/H2 labels."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
MANIFEST = ROOT / ".local/alignment/transactions/TX-20261017-0011/EV-0363-capture-manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    hypothesis = EXP / "hypothesis.md"
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hashes = manifest.setdefault("registered_local_hashes", {})
    hashes[hypothesis.relative_to(ROOT).as_posix()] = sha(hypothesis)
    hashes[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    item = next(row for row in evidence["items"] if row.get("id") == "EV-0363")
    item.setdefault("local_hashes", {})[hypothesis.relative_to(ROOT).as_posix()] = sha(hypothesis)
    item["local_hashes"][Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    item["local_hashes"][MANIFEST.relative_to(ROOT).as_posix()] = sha(MANIFEST)
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("refreshed EV-0363 experiment and manifest hashes")


if __name__ == "__main__":
    main()
