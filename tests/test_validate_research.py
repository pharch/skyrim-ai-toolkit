from __future__ import annotations

import json

from scripts.validate_research import validate


def test_repository_frontier_and_empty_evidence_register_validate():
    from conftest import REPO

    assert validate(REPO) == []


def test_validator_rejects_dangling_evidence_and_dependencies(tmp_path):
    research = tmp_path / "research"
    research.mkdir()
    (research / "FRONTIER.json").write_text(json.dumps({
        "schema_version": 2,
        "target": {
            "edition": "AE",
            "runtime_minimum": "1.6.318",
            "runtime_verified": False,
        },
        "items": [{
            "id": "Q-0001", "objective": "OBJ-1", "kind": "baseline",
            "status": "open", "question": "question", "methods": ["records"],
            "blocked_by": ["Q-0002"], "evidence": ["EV-0001"],
            "priority": 1, "next_action": "Check the record.",
        }],
    }), encoding="utf-8")
    (research / "EVIDENCE.json").write_text(json.dumps({
        "schema_version": 1, "items": [],
    }), encoding="utf-8")

    errors = validate(tmp_path)

    assert any("unknown evidence ID EV-0001" in error for error in errors)
    assert any("unknown dependency Q-0002" in error for error in errors)


def test_validator_rejects_absolute_artifact_paths(tmp_path):
    research = tmp_path / "research"
    research.mkdir()
    (research / "FRONTIER.json").write_text(json.dumps({
        "schema_version": 2,
        "target": {
            "edition": "AE",
            "runtime_minimum": "1.6.318",
            "runtime_verified": False,
        },
        "items": [{
            "id": "Q-0001", "objective": "OBJ-1", "kind": "baseline",
            "status": "open", "question": "question", "methods": ["records"],
            "blocked_by": [], "evidence": ["EV-0001"],
            "priority": 1, "next_action": "Check the record.",
        }],
    }), encoding="utf-8")
    (research / "EVIDENCE.json").write_text(json.dumps({
        "schema_version": 1,
        "items": [{
            "id": "EV-0001", "kind": "record", "source": "test source",
            "artifact": "/private/raw.json", "sha256": "0" * 64,
            "captured_utc": "2026-10-13T00:00:00Z", "edition": "AE",
            "runtime": "unknown", "modified_state": False,
            "lane": "offline", "tools": ["fixture"], "coverage": "1 fixture",
            "result": "test",
        }],
    }), encoding="utf-8")

    errors = validate(tmp_path)

    assert any("artifact must be relative or private-local" in error for error in errors)
