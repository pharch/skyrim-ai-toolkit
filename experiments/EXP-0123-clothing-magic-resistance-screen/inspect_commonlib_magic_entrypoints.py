#!/usr/bin/env python3
"""Locate source-verified CommonLib declarations for a GOG magic-damage trace."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path

KEYWORDS = (
    "MagicTarget",
    "ActiveEffect",
    "MagicEffect",
    "MagicItem",
    "ActorValueOwner",
    "ActorValueInfo",
)
VTABLE_TERMS = (
    "VTABLE_MagicTarget",
    "VTABLE_ActiveEffect",
    "VTABLE_ValueModifierEffect",
    "VTABLE_PeakValueModifierEffect",
    "VTABLE_AccumulatingValueModifierEffect",
    "VTABLE_Actor{",
    "VTABLE_PlayerCharacter",
)
HEADER_FILES = {
    "ActiveEffect.h",
    "ActorValueOwner.h",
    "Effect.h",
    "MagicTarget.h",
    "ValueModifierEffect.h",
    "PeakValueModifierEffect.h",
    "AccumulatingValueModifierEffect.h",
    "Actor.h",
    "PlayerCharacter.h",
}
HEADER_TERMS = (
    "class Actor :",
    "class PlayerCharacter :",
    "class MagicTarget :",
    "CheckResistance(",
    "IsCausingHealthDamage(",
    "GetActorValue(",
    "ModActorValue(",
    "ModifyActorValue(",
    "ModifyOnStart(",
    "ShouldModifyOnStart(",
    "baseEffect",
    "Effect*",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    config = read_local_config(ROOT)
    value = config.get("COMMONLIBSSE_ROOT", "").strip()
    if not value:
        raise RuntimeError("COMMONLIBSSE_ROOT is not configured")
    root = _native_path(value)
    if not root.is_dir():
        raise RuntimeError("configured CommonLib source is unavailable")
    include = root / "include" / "RE"
    if not include.is_dir():
        raise RuntimeError("configured CommonLib include/RE directory is unavailable")

    selected = []
    class_contexts = []
    source_hashes = {}
    offset_files = [include / "Offsets.h", include / "Offsets_VTABLE.h"]
    for path in offset_files:
        if not path.is_file():
            continue
        rel = path.relative_to(include).as_posix()
        source_hashes[rel] = sha256(path)
        terms = VTABLE_TERMS if path.name == "Offsets_VTABLE.h" else KEYWORDS
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(key.casefold() in line.casefold() for key in terms):
                selected.append({"file": rel, "line": number, "source": line.strip()})

    for path in include.rglob("*.h"):
        if path.name not in HEADER_FILES:
            continue
        rel = path.relative_to(include).as_posix()
        source_hashes[rel] = sha256(path)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            if line.strip().startswith(("class Actor :", "class PlayerCharacter :", "class MagicTarget :")):
                start = max(0, number - 1)
                end = min(len(lines), number + 7)
                class_contexts.append({
                    "file": rel,
                    "start_line": start + 1,
                    "source": lines[start:end],
                })
        for number, line in enumerate(lines, 1):
            if any(term.casefold() in line.casefold() for term in HEADER_TERMS):
                selected.append({"file": rel, "line": number, "source": line.strip()})

    print(json.dumps({
        "read_only": True,
        "source": "configured CommonLibSSE-NG headers; paths omitted",
        "source_header_sha256": source_hashes,
        "class_contexts": class_contexts,
        "matching_declarations": selected,
        "matching_declaration_count": len(selected),
        "truncated": False,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
