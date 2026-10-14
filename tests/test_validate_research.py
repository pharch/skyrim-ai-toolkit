from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_research import _validate_markdown_entities, validate


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


def test_validator_accepts_explicit_unknown_edition_for_legacy_evidence(tmp_path):
    from scripts.validate_research import _validate_evidence

    register = {
        "schema_version": 1,
        "items": [{
            "id": "EV-0001", "kind": "legacy", "source": "legacy snapshot report",
            "artifact": "private-local:legacy-repo/report.md", "sha256": "0" * 64,
            "captured_utc": "2026-10-14T00:00:00Z", "edition": "unknown",
            "runtime": "unknown", "modified_state": False,
            "lane": "mechanism_inference", "tools": ["unknown version"],
            "coverage": "one historical report; not re-run", "result": "historical static report",
        }],
    }

    errors, ids = _validate_evidence(register, tmp_path)

    assert errors == []
    assert ids == {"EV-0001"}


def _write_entity_fixture(root):
    research = root / "research"
    research.mkdir(parents=True, exist_ok=True)
    (research / "CLAIMS.md").write_text(
        "| ID | Claim | Status | Evidence IDs | Scope and open limit |\n"
        "|---|---|---|---|---|\n"
        "| CL-T001 | Claim summary | supported | [EV-0001] | Scope limit |\n",
        encoding="utf-8",
    )
    (research / "MECHANISMS.md").write_text("## M-0001 — Mechanism\n\nSummary [EV-0001].\n", encoding="utf-8")
    (research / "GLITCHES.md").write_text("## G-0001 — Glitch\n\nSummary [EV-0001].\n", encoding="utf-8")
    (research / "CONTRADICTIONS.md").write_text(
        "## C-LEG-0001 — Competing models\n\n"
        "- **Model A:** first account.\n- **Model B:** second account.\n"
        "- **Source:** [EV-0001].\n- **Discriminant:** compare the outcomes.\n",
        encoding="utf-8",
    )
    experiment = root / "experiments" / "EXP-0001-test"
    experiment.mkdir(parents=True)
    (experiment / "README.md").write_text("Pilot [EV-0001].\n", encoding="utf-8")
    (experiment / "hypothesis.md").write_text("H1 predicts A. H2 predicts B.\n", encoding="utf-8")
    (experiment / "protocol.md").write_text("Compare controlled cases.\n", encoding="utf-8")
    (experiment / "expected-discriminants.md").write_text("Observe the outcome.\n", encoding="utf-8")
    (experiment / "results.md").write_text("No result yet.\n", encoding="utf-8")
    return research


def test_markdown_entity_schemas_validate_and_resolve_evidence(tmp_path):
    _write_entity_fixture(tmp_path)
    assert _validate_markdown_entities(tmp_path, {"EV-0001"}) == []


def test_markdown_entity_schema_rejects_missing_discriminant_and_unknown_evidence(tmp_path):
    research = _write_entity_fixture(tmp_path)
    contradiction = research / "CONTRADICTIONS.md"
    contradiction.write_text(
        contradiction.read_text(encoding="utf-8").replace("Discriminant:", "Test:"),
        encoding="utf-8",
    )
    errors = _validate_markdown_entities(tmp_path, {"EV-0002"})
    assert any("requires Discriminant" in error for error in errors)
    assert any("unknown evidence ID EV-0001" in error for error in errors)


class MarkdownEntitySchemaTests(unittest.TestCase):
    def test_markdown_entity_schema_validates_and_rejects_bad_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            research = _write_entity_fixture(root)
            self.assertEqual(_validate_markdown_entities(root, {"EV-0001"}), [])
            contradiction = research / "CONTRADICTIONS.md"
            contradiction.write_text(
                contradiction.read_text(encoding="utf-8").replace("Discriminant:", "Test:"),
                encoding="utf-8",
            )
            errors = _validate_markdown_entities(root, {"EV-0002"})
            self.assertTrue(any("requires Discriminant" in error for error in errors))
            self.assertTrue(any("unknown evidence ID EV-0001" in error for error in errors))
