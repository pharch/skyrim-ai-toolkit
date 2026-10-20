#!/usr/bin/env python3
"""Resolve only candidate GLOB/QUST records from the prepared vanilla files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import mmap
import struct
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.plugin_reader import _records, _subrecords

EXPECTED_SHA256 = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}
ORDER = list(EXPECTED_SHA256)


def text(value: bytes) -> str:
    return value.rstrip(b"\0").decode("cp1252", "replace")


def plugin_masters(path: Path) -> list[str]:
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for signature, flags, form_id, offset, payload in _records(data):
            if signature == "TES4":
                parts = list(_subrecords(payload, flags))
                return [text(value) for name, value in parts if name == "MAST"]
    raise ValueError(f"missing TES4 header in {path.name}")


def resolve_form_id(raw_form_id: str, source_plugin: str, masters_by_plugin: dict[str, list[str]]) -> dict[str, str]:
    value = int(raw_form_id, 16)
    origin_index = value >> 24
    masters = masters_by_plugin[source_plugin]
    if origin_index < len(masters):
        origin = masters[origin_index]
    elif origin_index == len(masters):
        origin = source_plugin
    else:
        origin = "UNRESOLVED"
    return {"raw_form_id": raw_form_id.upper(), "origin_plugin": origin, "local_form_id": f"{value & 0x00FFFFFF:06X}"}


def scan_plugin(path: Path, wanted_keys: set[tuple[str, str]]) -> tuple[str, list[dict[str, Any]], dict[str, int]]:
    plugin = path.name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = EXPECTED_SHA256[plugin]
    if digest != expected:
        raise ValueError(f"prepared official master hash mismatch for {plugin}")
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        header_parts = None
        for signature, flags, form_id, offset, payload in _records(data):
            if signature == "TES4":
                header_parts = list(_subrecords(payload, flags))
                break
        if header_parts is None:
            raise ValueError(f"missing TES4 header in {plugin}")
        masters = [text(value) for name, value in header_parts if name == "MAST"]
        rows: list[dict[str, Any]] = []
        signature_counts = {"QUST": 0, "GLOB": 0, "SMBN": 0}
        with path.open("rb") as stream2, mmap.mmap(stream2.fileno(), 0, access=mmap.ACCESS_READ) as data2:
            for signature, flags, form_id, offset, payload in _records(data2):
                if signature in signature_counts:
                    signature_counts[signature] += 1
                origin_index = form_id >> 24
                origin = (masters + [plugin])[origin_index] if origin_index <= len(masters) else "UNRESOLVED"
                local_form_id = f"{form_id & 0x00FFFFFF:06X}"
                if signature not in {"GLOB", "QUST", "SMBN"} and (origin, local_form_id) not in wanted_keys:
                    continue
                parts = list(_subrecords(payload, flags))
                editor_id = next((text(value) for name, value in parts if name == "EDID"), "")
                row = {
                    "signature": signature,
                    "plugin": plugin,
                    "origin_plugin": origin,
                    "file_form_id": f"{form_id:08X}",
                    "local_form_id": local_form_id,
                    "offset": f"0x{offset:X}",
                    "flags": f"{flags:08X}",
                    "editor_id": editor_id,
                    "subrecords": [
                        {"signature": name, "length": len(value), "hex": value.hex(), "text": text(value)}
                        for name, value in parts
                        if name in {"FLTV", "DNAM", "DATA", "ALST", "ALUA", "ENAM", "CTDA", "QNAM", "NNAM", "FULL", "EDID"}
                    ],
                }
                rows.append(row)
        return digest, rows, signature_counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--candidate-analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis = json.loads(args.candidate_analysis.read_text(encoding="utf-8"))
    masters_by_plugin = {plugin: plugin_masters(args.data_dir / plugin) for plugin in ORDER}
    references = []
    for candidate in analysis["getlevel_observations_after_local_override_comparison"]:
        source_plugin = candidate["source_plugin"]
        node = {"node_form_id": candidate["file_form_id"], "node_editor_id": candidate["editor_id"],
                "condition_index": candidate["condition_index"]}
        for raw in candidate.get("children", []):
            references.append({**node, "kind": "child", "expected_signature": "QUST", "source_plugin": source_plugin,
                               **resolve_form_id(raw, source_plugin, masters_by_plugin)})
        if candidate.get("parent_form_id"):
            raw = candidate["parent_form_id"]
            references.append({**node, "kind": "parent", "expected_signature": None, "source_plugin": source_plugin,
                               **resolve_form_id(raw, source_plugin, masters_by_plugin)})
        global_id = candidate["condition"].get("operand_global_form_id")
        if global_id:
            references.append({**node, "kind": "threshold_global", "expected_signature": "GLOB", "source_plugin": source_plugin,
                               **resolve_form_id(global_id, source_plugin, masters_by_plugin)})
    wanted_keys = {(row["origin_plugin"], row["local_form_id"]) for row in references}

    matches: list[dict[str, Any]] = []
    branch_nodes: list[dict[str, Any]] = []
    source_hashes = {}
    signature_counts = {}
    for plugin in ORDER:
        digest, rows, counts = scan_plugin(args.data_dir / plugin, wanted_keys)
        source_hashes[plugin] = digest
        signature_counts[plugin] = counts
        branch_nodes.extend(row for row in rows if row["signature"] == "SMBN")
        matches.extend(row for row in rows if (row["origin_plugin"], row["local_form_id"]) in wanted_keys)

    winners: dict[tuple[str, str], dict[str, Any]] = {}
    for row in matches:
        winners[(row["signature"], row["origin_plugin"], row["local_form_id"])] = row
    branch_winners: dict[tuple[str, str], dict[str, Any]] = {}
    for row in branch_nodes:
        branch_winners[(row["origin_plugin"], row["local_form_id"])] = row
    result = {
        "route": "read-only targeted scan with the repository plugin_reader TES4 parser against the hash-verified prepared five-master copy; no native xEdit",
        "official_order": ORDER,
        "source_hashes": source_hashes,
        "parsed_record_counts": signature_counts,
        "story_manager_branch_nodes_all_source_files": branch_nodes,
        "story_manager_branch_nodes_after_local_override_comparison": list(branch_winners.values()),
        "candidate_references_resolved_in_source_plugin_context": references,
        "matching_records_all_source_files": matches,
        "matching_records_after_local_override_comparison": list(winners.values()),
        "interpretation_limits": [
            "These are source-record observations and a simple last-file same-FormID comparison, not native xEdit winning-field data or a profile-specific winner.",
            "Only candidate child QUST, operand GLOB, and parent records were retained; this is not a full QUST/GLOB census.",
            "Quest subrecord bytes are preserved for later schema interpretation; their mere presence does not establish startup or a low-level route.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "target_reference_count": len(references),
        "matching_record_count": len(matches),
        "source_hashes_verified": source_hashes,
        "parsed_record_counts": signature_counts,
        "output": args.output.as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
