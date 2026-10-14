import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.research_transactions import (
    begin_transaction,
    block_transaction,
    complete_transaction,
    validate_transaction_ledger,
    update_transaction,
)
from scripts.research_state import read_json

ROOT = Path(__file__).resolve().parents[1]


class ResearchTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        research = self.root / "research"
        research.mkdir()
        (self.root / "raw").mkdir()
        (self.root / "raw/observation.txt").write_text("test artifact\n", encoding="utf-8")
        (research / "SESSION_LOG.md").write_text("# Session log\n", encoding="utf-8")
        items = [
            self.item("Q-0001", "open", 1.0, []),
            self.item("Q-0002", "open", 0.95, ["Q-0001"]),
            self.item("Q-0003", "open", 0.8, []),
        ]
        (research / "FRONTIER.json").write_text(json.dumps({
            "schema_version": 3,
            "target": {"edition": "AE"},
            "items": items,
            "session_next_action": "Select a ready item.",
        }), encoding="utf-8")
        (research / "EVIDENCE.json").write_text(json.dumps({
            "schema_version": 1,
            "items": [{"id": "EV-0001"}, {"id": "EV-0002"}],
        }), encoding="utf-8")
        (research / "RECOVERY.json").write_text(json.dumps({
            "schema_version": 2,
            "status": "idle",
            "transaction_id": None,
            "frontier_id": None,
            "started_utc": None,
            "checkpoint_utc": "2026-01-01T00:00:00Z",
            "artifacts": [],
            "next_action": "Select a ready item.",
        }), encoding="utf-8")
        (research / "TRANSACTIONS.json").write_text(json.dumps({
            "schema_version": 1, "transactions": [], "events": [],
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def item(item_id, status, priority, blocked_by):
        return {
            "id": item_id,
            "objective": "OBJ-test",
            "kind": "hypothesis_test",
            "status": status,
            "question": f"Question for {item_id}?",
            "hypotheses": [
                {"id": "H1", "model": "first model", "predicted_discriminant": "first result", "status": "proposed"},
                {"id": "H2", "model": "rival model", "predicted_discriminant": "rival result", "status": "proposed"},
            ],
            "methods": ["offline inspection"],
            "blocked_by": blocked_by,
            "evidence": [],
            "priority": priority,
            "information_gain": 0.7,
            "next_action": f"Inspect {item_id} evidence.",
            "linked_claims": [],
            "successors": [],
            "attempts": [],
        }

    def states(self):
        research = self.root / "research"
        return (
            read_json(research / "FRONTIER.json"),
            read_json(research / "RECOVERY.json"),
            read_json(research / "TRANSACTIONS.json"),
        )

    def assert_valid_ledger(self):
        _, recovery, ledger = self.states()
        self.assertEqual(validate_transaction_ledger(ledger, recovery, {"EV-0001", "EV-0002"}), [])

    def start_and_update(self, transaction_id="TX-20261014-0001"):
        begin_transaction(self.root, transaction_id, "Q-0001", "Inspect the first source.")
        update_transaction(
            self.root, transaction_id,
            action_key="read-source", outcome="captured one revision-cited observation",
            next_action="Compare the rival model against the same source.",
            evidence_ids=["EV-0001"], artifacts=["raw/observation.txt"],
        )

    def test_complete_operation_reselects_next_ready_frontier_item(self):
        self.start_and_update()
        result = complete_transaction(
            self.root, "TX-20261014-0001",
            summary="The source supports a scoped threshold statement.",
            cross_domain_assessment="No shared engine primitive is established by this source alone.",
        )
        self.assertEqual(result["transaction"]["status"], "completed")
        self.assertEqual(result["next_item"]["id"], "Q-0003")
        frontier, recovery, _ = self.states()
        self.assertEqual(recovery["status"], "idle")
        self.assertEqual(recovery["next_frontier_id"], "Q-0003")
        self.assertEqual(frontier["items"][0]["status"], "in_progress")
        self.assertIn("EV-0001", frontier["items"][0]["evidence"])
        self.assert_valid_ledger()

    def test_block_operation_marks_line_and_selects_independent_item(self):
        self.start_and_update("TX-20261014-0002")
        result = block_transaction(
            self.root, "TX-20261014-0002",
            blocker="Selected profile load order is not available.",
            blocker_status="blocked_environment",
            evidence_ids=["EV-0002"], artifacts=["raw/observation.txt"],
        )
        self.assertEqual(result["transaction"]["status"], "blocked_environment")
        self.assertEqual(result["next_item"]["id"], "Q-0003")
        frontier, recovery, _ = self.states()
        self.assertEqual(frontier["items"][0]["status"], "blocked_environment")
        self.assertEqual(recovery["next_frontier_id"], "Q-0003")
        self.assertIn("independently selected Q-0003", (self.root / "research/SESSION_LOG.md").read_text(encoding="utf-8"))
        self.assert_valid_ledger()

    def test_duplicate_action_without_new_evidence_or_discriminant_is_rejected(self):
        self.start_and_update("TX-20261014-0003")
        with self.assertRaisesRegex(ValueError, "new evidence or a new predicted discriminant"):
            update_transaction(
                self.root, "TX-20261014-0003",
                action_key="read-source", outcome="repeated the same query",
                next_action="Continue.",
            )
        self.assert_valid_ledger()

    def test_running_transaction_recovers_and_resumes_in_fresh_processes(self):
        self.start_and_update("TX-20261014-0004")
        recover = subprocess.run(
            [sys.executable, "-m", "scripts.research_state", "recover", "--root", str(self.root)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(recover.returncode, 0, recover.stderr)
        self.assertIn("interrupted", recover.stdout)
        resume = subprocess.run(
            [sys.executable, "-m", "scripts.research_state", "resume", "--root", str(self.root), "--transaction-id", "TX-20261014-0004"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(resume.returncode, 0, resume.stderr)
        self.assertIn("resumed TX-20261014-0004", resume.stdout)
        _, recovery, ledger = self.states()
        self.assertEqual(recovery["status"], "running")
        self.assertEqual(ledger["transactions"][0]["status"], "running")
        self.assert_valid_ledger()

    def test_complete_requires_update_and_known_evidence(self):
        begin_transaction(self.root, "TX-20261014-0005", "Q-0001", "Inspect evidence.")
        with self.assertRaisesRegex(ValueError, "requires at least one validated update"):
            complete_transaction(
                self.root, "TX-20261014-0005", summary="No work.",
                cross_domain_assessment="No synthesis.", evidence_ids=["EV-0001"],
            )

    def test_transaction_ids_and_artifact_paths_are_validated(self):
        with self.assertRaisesRegex(ValueError, "transaction ID"):
            begin_transaction(self.root, "not-an-id", "Q-0001", "Inspect the source.")
        begin_transaction(self.root, "TX-20261014-0006", "Q-0001", "Inspect the source.")
        with self.assertRaisesRegex(ValueError, "artifact does not exist"):
            update_transaction(
                self.root, "TX-20261014-0006", action_key="inspect",
                outcome="captured an observation", next_action="Continue.",
                evidence_ids=["EV-0001"], artifacts=["raw/missing.txt"],
            )

    def test_python_cli_runs_begin_update_complete_on_isolated_root(self):
        command = [sys.executable, str(ROOT / "scripts" / "research_transactions.py"),
                   "--root", str(self.root)]
        begin = subprocess.run(
            [*command, "begin", "TX-CLI-0001", "Q-0001", "--next-action", "Read the fixture."],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(begin.returncode, 0, begin.stderr)
        update = subprocess.run(
            [*command, "update", "TX-CLI-0001", "--action-key", "fixture-source",
             "--outcome", "Recorded the fixture observation.",
             "--next-action", "Close the fixture transaction.", "--evidence", "EV-0001"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(update.returncode, 0, update.stderr)
        complete = subprocess.run(
            [*command, "complete", "TX-CLI-0001", "--summary", "Fixture transaction completed.",
             "--cross-domain-assessment", "No cross-domain model is supported by this fixture.",
             "--evidence", "EV-0001"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(complete.returncode, 0, complete.stderr)
        result = json.loads(complete.stdout)
        self.assertEqual(result["transaction"]["status"], "completed")
        self.assertEqual(result["next_item"]["id"], "Q-0003")
        validate = subprocess.run(
            [*command, "validate"], capture_output=True, text=True, check=False,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertTrue(json.loads(validate.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
