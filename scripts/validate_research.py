#!/usr/bin/env python3
"""Validate the durable research frontier and evidence register."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"open", "in_progress", "blocked", "awaiting-user-data", "resolved"}
LANES = {
    "offline", "diagnostic_intervention", "vanilla_candidate",
    "vanilla_reproduction", "mechanism_inference",
}
EVIDENCE_KINDS = {"record", "native", "runtime", "save", "log", "wiki", "discord", "tool", "legacy"}


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        frontier = json.loads((root / "research/FRONTIER.json").read_text(encoding="utf-8"))
        register = json.loads((root / "research/EVIDENCE.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read frontier/evidence JSON: {exc}"]

    if frontier.get("schema_version") != 2:
        errors.append("frontier schema_version must be 2")
    target = frontier.get("target", {})
    if target.get("edition") != "AE" or target.get("runtime_minimum") != "1.6.318":
        errors.append("frontier target must be Skyrim AE runtime 1.6.318+")
    if target.get("runtime_verified") is not False and not isinstance(target.get("runtime_verified"), str):
        errors.append("runtime_verified must be false or a verified runtime string")

    evidence_items = register.get("items")
    if register.get("schema_version") != 1 or not isinstance(evidence_items, list):
        errors.append("evidence register must have schema_version 1 and an items array")
        evidence_items = []
    evidence_by_id: dict[str, dict] = {}
    for item in evidence_items:
        if not isinstance(item, dict):
            errors.append("evidence entries must be objects")
            continue
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not re.fullmatch(r"EV-\d{4,}", evidence_id):
            errors.append(f"invalid evidence ID: {evidence_id!r}")
            continue
        if evidence_id in evidence_by_id:
            errors.append(f"duplicate evidence ID: {evidence_id}")
        evidence_by_id[evidence_id] = item
        for field in (
            "source", "artifact", "sha256", "captured_utc", "edition",
            "runtime", "modified_state", "lane", "tools", "coverage", "result",
        ):
            if field not in item:
                errors.append(f"{evidence_id}: missing {field}")
        if item.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{evidence_id}: invalid evidence kind")
        if item.get("lane") not in LANES:
            errors.append(f"{evidence_id}: invalid evidence lane")
        if not isinstance(item.get("modified_state"), bool):
            errors.append(f"{evidence_id}: modified_state must be boolean")
        if not isinstance(item.get("tools"), list) or not item["tools"]:
            errors.append(f"{evidence_id}: tools must be a non-empty list")
        try:
            timestamp = datetime.fromisoformat(str(item.get("captured_utc", "")).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                errors.append(f"{evidence_id}: captured_utc must include a timezone")
        except ValueError:
            errors.append(f"{evidence_id}: captured_utc must be ISO-8601")
        artifact = item.get("artifact", "")
        if isinstance(artifact, str) and not artifact.startswith("private-local:"):
            artifact_path = Path(artifact)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                errors.append(f"{evidence_id}: artifact must be relative or private-local")
            elif not (root / artifact_path).is_file():
                errors.append(f"{evidence_id}: artifact does not exist: {artifact}")
        digest = item.get("sha256", "")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{evidence_id}: sha256 must be 64 lowercase hex characters")

    items = frontier.get("items")
    if not isinstance(items, list) or not items:
        errors.append("frontier must contain at least one research item")
        return errors
    item_by_id: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            errors.append("frontier entries must be objects")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not re.fullmatch(r"[A-Z]+-\d{4,}", item_id):
            errors.append(f"invalid frontier ID: {item_id!r}")
            continue
        if item_id in item_by_id:
            errors.append(f"duplicate frontier ID: {item_id}")
        item_by_id[item_id] = item
        for field in ("objective", "kind", "status", "question", "methods", "blocked_by", "evidence", "priority", "next_action"):
            if field not in item:
                errors.append(f"{item_id}: missing {field}")
        if item.get("status") not in STATUSES:
            errors.append(f"{item_id}: invalid status")
        if not isinstance(item.get("methods"), list) or not item["methods"]:
            errors.append(f"{item_id}: methods must be a non-empty list")
        if not isinstance(item.get("next_action"), str) or not item["next_action"].strip():
            errors.append(f"{item_id}: next_action must be actionable text")
        priority = item.get("priority")
        if not isinstance(priority, (int, float)) or not 0 <= priority <= 1:
            errors.append(f"{item_id}: priority must be between 0 and 1")
        if not isinstance(item.get("evidence"), list):
            errors.append(f"{item_id}: evidence must be a list")
        else:
            for evidence_id in item["evidence"]:
                if evidence_id not in evidence_by_id:
                    errors.append(f"{item_id}: unknown evidence ID {evidence_id}")
        if not isinstance(item.get("blocked_by"), list):
            errors.append(f"{item_id}: blocked_by must be a list")

    for item_id, item in item_by_id.items():
        for dependency in item.get("blocked_by", []):
            if dependency not in item_by_id:
                errors.append(f"{item_id}: unknown dependency {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(item_id: str) -> None:
        if item_id in visiting:
            errors.append(f"cyclic frontier dependency at {item_id}")
            return
        if item_id in visited:
            return
        visiting.add(item_id)
        for dependency in item_by_id[item_id].get("blocked_by", []):
            if dependency in item_by_id:
                visit(dependency)
        visiting.remove(item_id)
        visited.add(item_id)

    for item_id in item_by_id:
        visit(item_id)

    return errors


if __name__ == "__main__":
    problems = validate()
    print("RESEARCH DATA " + ("FAIL" if problems else "PASS"))
    for problem in problems:
        print(f" - {problem}")
    raise SystemExit(bool(problems))
