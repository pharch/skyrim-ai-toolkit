#!/usr/bin/env python3
"""Capture the five-master AVIF skill-use coefficients and source declarations."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    cfg = read_local_config(ROOT)
    source_root = _native_path(cfg.get("COMMONLIBSSE_ROOT", "").strip())
    data_root = _native_path(cfg.get("SKYRIM_DATA", "").strip())
    if not source_root.is_dir() or not data_root.is_dir():
        raise SystemExit("configured CommonLibSSE root or Skyrim Data directory is unavailable")
    commit = subprocess.run(["git", "-C", str(source_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if commit != "b93280e832f263dbef44e44cbe2936622a02f91a":
        raise SystemExit(f"unexpected CommonLib source commit: {commit}")

    header_paths = {
        "actor_values": source_root / "include/RE/A/ActorValues.h",
        "actor_value_info": source_root / "include/RE/A/ActorValueInfo.h",
    }
    headers = {}
    for name, path in header_paths.items():
        if not path.is_file():
            raise SystemExit(f"missing primary source header: {name}")
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if name == "actor_values":
            selected = [(i + 1, line.strip()) for i, line in enumerate(lines) if any(needle.lower() in line.lower() for needle in ("kHeavyArmor =", "kLightArmor =", "kHeavyArmorSkillAdvance", "kLightArmorSkillAdvance", "SkillUse"))]
        else:
            selected = [(i + 1, line.strip()) for i, line in enumerate(lines) if any(needle in line for needle in ("struct Skill", "float useMult", "float offsetMult", "float improveMult", "float improveOffset", "Skill* skill"))]
        headers[name] = {
            "source_relative_path": path.relative_to(source_root).as_posix(),
            "sha256": digest(path),
            "selected_lines": [{"line": line, "text": text} for line, text in selected],
        }

    plugin_hashes = {}
    avif_counts: Counter[str] = Counter()
    records = []
    for plugin in PLUGINS:
        path = data_root / plugin
        if not path.is_file():
            raise SystemExit(f"official master missing: {plugin}")
        plugin_hashes[plugin] = digest(path)
        for record in read_plugin(path, include_subrecords=True):
            if record.get("signature") != "AVIF":
                continue
            avif_counts[plugin] += 1
            subrecords = []
            skill = None
            for sub in record.get("subrecords", []):
                signature = sub.get("signature")
                raw = bytes.fromhex(sub.get("value_hex", ""))
                if signature == "AVSK":
                    skill = {
                        "raw_hex": raw.hex(),
                        "length": len(raw),
                        "decoded_four_floats": list(struct.unpack("<4f", raw)) if len(raw) == 16 else None,
                    }
                subrecords.append({"signature": signature, "value_hex": raw.hex()})
            records.append({
                "plugin": plugin,
                "file_form_id": record.get("file_form_id"),
                "editor_id": record.get("editor_id"),
                "AVSK": skill,
                "subrecords": subrecords,
            })

    matching = [row for row in records if any(token in (row.get("editor_id") or "").lower() for token in ("heavyarmor", "lightarmor"))]
    result = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": commit,
        "source_headers": headers,
        "plugin_sha256": plugin_hashes,
        "official_five_master_scope": list(PLUGINS),
        "AVIF_record_count_by_plugin": dict(avif_counts),
        "AVIF_total": len(records),
        "HeavyLight_EditorID_candidates": matching,
        "all_AVIF_records": records,
        "limits": "Source-file records only. AVSK is decoded as four floats according to CommonLib ActorValueInfo::Skill; no runtime mutation, profile winner, or player-reachable AVIF edit is inferred.",
    }
    out = ROOT / ".local/alignment/transactions/TX-20261020-0011/q92/skill-avif-records.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": out.relative_to(ROOT).as_posix(),
        "sha256": digest(out),
        "source_commit": commit,
        "plugin_sha256": plugin_hashes,
        "AVIF_record_count_by_plugin": dict(avif_counts),
        "AVIF_total": len(records),
        "HeavyLight_EditorID_candidates": [{"plugin": row["plugin"], "form_id": row["file_form_id"], "editor_id": row["editor_id"], "AVSK": row["AVSK"]} for row in matching],
        "limits": result["limits"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
