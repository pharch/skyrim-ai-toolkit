#!/usr/bin/env python3
"""Validate durable Skyrim AE evidence records and research-state links."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from .research_state import validate_frontier
except ImportError:
    from research_state import validate_frontier

ROOT = Path(__file__).resolve().parents[1]
LANES = {
    "offline", "diagnostic_intervention", "vanilla_candidate",
    "vanilla_reproduction", "mechanism_inference",
}
EVIDENCE_KINDS = {"record", "native", "runtime", "save", "log", "wiki", "discord", "tool", "legacy"}
EVIDENCE_ID = re.compile(r"EV-\d{4,}")


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _validate_evidence(register: dict[str, Any], root: Path) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    items = register.get("items")
    if register.get("schema_version") != 1 or not isinstance(items, list):
        return ["evidence register must have schema_version 1 and an items array"], set()
    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            errors.append("evidence entries must be objects")
            continue
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID.fullmatch(evidence_id):
            errors.append(f"invalid evidence ID: {evidence_id!r}")
            continue
        if evidence_id in by_id:
            errors.append(f"duplicate evidence ID: {evidence_id}")
        by_id[evidence_id] = item
        fields = (
            "kind", "source", "artifact", "sha256", "captured_utc",
            "edition", "runtime", "modified_state", "lane", "tools",
            "coverage", "result",
        )
        for field in fields:
            if field not in item:
                errors.append(f"{evidence_id}: missing {field}")
        if item.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{evidence_id}: invalid evidence kind")
        if item.get("lane") not in LANES:
            errors.append(f"{evidence_id}: invalid evidence lane")
        if item.get("edition") != "AE":
            errors.append(f"{evidence_id}: edition must be AE")
        if not isinstance(item.get("runtime"), str) or not item["runtime"].strip():
            errors.append(f"{evidence_id}: runtime must be a version or explicit unknown")
        if not isinstance(item.get("modified_state"), bool):
            errors.append(f"{evidence_id}: modified_state must be boolean")
        if not isinstance(item.get("tools"), list) or not item["tools"] or any(not isinstance(tool, str) or not tool.strip() for tool in item["tools"]):
            errors.append(f"{evidence_id}: tools must be a non-empty list of names/versions")
        for field in ("source", "coverage", "result"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{evidence_id}: {field} must be non-empty text")
        try:
            timestamp = datetime.fromisoformat(str(item.get("captured_utc", "")).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                errors.append(f"{evidence_id}: captured_utc must include a timezone")
        except ValueError:
            errors.append(f"{evidence_id}: captured_utc must be ISO-8601")
        artifact = item.get("artifact")
        if not isinstance(artifact, str) or not artifact:
            errors.append(f"{evidence_id}: artifact must be a path or private-local reference")
        elif artifact.startswith("private-local:"):
            if not artifact.removeprefix("private-local:").strip():
                errors.append(f"{evidence_id}: private-local artifact must name a local artifact")
        else:
            artifact_path = Path(artifact)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                errors.append(f"{evidence_id}: artifact must be relative or private-local")
            else:
                source = root / artifact_path
                if not source.is_file():
                    errors.append(f"{evidence_id}: artifact does not exist: {artifact}")
                elif isinstance(item.get("sha256"), str):
                    actual = hashlib.sha256(source.read_bytes()).hexdigest()
                    if actual != item["sha256"]:
                        errors.append(f"{evidence_id}: artifact SHA-256 mismatch")
        digest = item.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{evidence_id}: sha256 must be 64 lowercase hex characters")
    return errors, set(by_id)


def validate(root: Path = ROOT) -> list[str]:
    try:
        frontier = _read(root / "research/FRONTIER.json")
        register = _read(root / "research/EVIDENCE.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot read frontier/evidence JSON: {exc}"]
    errors, evidence_ids = _validate_evidence(register, root)
    errors.extend(validate_frontier(frontier, evidence_ids))
    return errors


if __name__ == "__main__":
    problems = validate()
    print("RESEARCH DATA " + ("FAIL" if problems else "PASS"))
    for problem in problems:
        print(f" - {problem}")
    raise SystemExit(bool(problems))
