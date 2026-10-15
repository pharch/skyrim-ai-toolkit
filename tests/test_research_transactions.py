import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.research_state import read_json, ready_items
from scripts.research_transactions import (
    begin_transaction,
    block_transaction,
    complete_transaction,
    recover_transaction,
    resume_transaction,
    validate_transaction_ledger,
    update_transaction,
)

ROOT = Path(__file__).resolve().parents[1]


class ResearchTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        research = self.root / "research"
        research.mkdir()
        (self.root / "raw").mkdir()
        (self.root / "bounties").mkdir()
        (self.root / "raw/observation.txt").write_text("test artifact\n", encoding="utf-8")
        (self.root / "bounties/BOUNTY.md").write_text("status: active\n", encoding="utf-8")
        (research / "SESSION_LOG.md").write_text("# Session log\n", encoding="utf-8")
        (research / "CLAIMS.md").write_text(
            "| CL-0001 | Fixture claim | supported | [EV-0001] | test scope |\n",
            encoding="utf-8",
        )
        (research / "MECHANISMS.md").write_text(
            "## M-0001 — Fixture mechanism\n",
            encoding="utf-8",
        )
        (research / "KNOWLEDGE_GRAPH.md").write_text(
            "M-0001 connects to CL-0001 [EV-0001].\n",
            encoding="utf-8",
        )
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
            "next_frontier_id": "Q-0001",
            "last_transaction_id": None,
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
        frontier, recovery, ledger = self.states()
        self.assertEqual(
            validate_transaction_ledger(
                ledger, recovery, {"EV-0001", "EV-0002"},
                frontier=frontier, root=self.root,
            ),
            [],
        )

    def start_and_update(self, transaction_id="TX-20261014-0001", frontier_id="Q-0001"):
        tx = begin_transaction(
            self.root, frontier_id, "Inspect the first source.",
            transaction_id=transaction_id,
        )
        update_transaction(
            self.root, tx["id"],
            action_key="read-source", outcome="captured one revision-cited observation",
            next_action="Compare the rival model against the same source.",
            evidence_ids=["EV-0001"], artifacts=["raw/observation.txt"],
        )
        return tx["id"]

    def complete(self, transaction_id, **kwargs):
        return complete_transaction(
            self.root, transaction_id,
            summary="The source supports a scoped threshold statement.",
            cross_domain_assessment="No shared engine primitive is established by this source alone.",
            knowledge_graph_action="No new causal edge is justified by this bounded evidence.",
            **kwargs,
        )

    def test_complete_resolves_frontier_and_records_synthesis_links(self):
        transaction_id = self.start_and_update()
        bounty_before = (self.root / "bounties/BOUNTY.md").read_bytes()
        result = self.complete(
            transaction_id,
            synthesis_claim_ids=["CL-0001"],
            synthesis_mechanism_ids=["M-0001"],
        )
        self.assertEqual(result["transaction"]["status"], "completed")
        self.assertEqual(result["transaction"]["closure_scope"], "frontier_resolved")
        self.assertEqual(result["transaction"]["frontier_resolution"]["status"], "completed")
        self.assertEqual(result["transaction"]["synthesis_claim_ids"], ["CL-0001"])
        self.assertEqual(result["transaction"]["synthesis_mechanism_ids"], ["M-0001"])
        self.assertEqual(result["next_item"]["id"], "Q-0002")
        frontier, recovery, _ = self.states()
        resolved = next(item for item in frontier["items"] if item["id"] == "Q-0001")
        self.assertEqual(resolved["status"], "completed")
        self.assertIn("EV-0001", resolved["decision"]["evidence"])
        self.assertIn("CL-0001", resolved["linked_claims"])
        self.assertEqual(resolved["successors"], [])
        self.assertEqual(recovery["status"], "idle")
        self.assertEqual(recovery["next_frontier_id"], "Q-0002")
        self.assertEqual((self.root / "bounties/BOUNTY.md").read_bytes(), bounty_before)
        self.assertNotIn("Q-0001", {item["id"] for item in ready_items(frontier)})
        self.assert_valid_ledger()

    def test_claim_must_link_transaction_evidence_and_knowledge_graph(self):
        transaction_id = self.start_and_update()
        graph = self.root / "research/KNOWLEDGE_GRAPH.md"
        graph.write_text("M-0001 only.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not linked in research/KNOWLEDGE_GRAPH"):
            self.complete(transaction_id, synthesis_claim_ids=["CL-0001"])
        self.assertEqual(self.states()[1]["status"], "running")

    def test_complete_can_falsify_question_without_claiming_bounty_solved(self):
        transaction_id = self.start_and_update()
        result = self.complete(transaction_id, frontier_status="falsified")
        frontier, recovery, _ = self.states()
        item = next(item for item in frontier["items"] if item["id"] == "Q-0001")
        self.assertEqual(item["status"], "falsified")
        self.assertEqual(result["transaction"]["frontier_resolution"]["status"], "falsified")
        self.assertEqual(recovery["status"], "idle")
        self.assertEqual((self.root / "bounties/BOUNTY.md").read_text(encoding="utf-8"), "status: active\n")
        self.assert_valid_ledger()

    def test_complete_with_no_ready_successor_closes_cleanly(self):
        frontier, _, _ = self.states()
        for item in frontier["items"]:
            if item["id"] != "Q-0001":
                item["status"] = "blocked_environment"
        (self.root / "research/FRONTIER.json").write_text(json.dumps(frontier), encoding="utf-8")
        transaction_id = self.start_and_update()
        result = self.complete(transaction_id)
        frontier, recovery, _ = self.states()
        self.assertIsNone(result["next_item"])
        self.assertEqual(recovery["status"], "idle")
        self.assertIsNone(recovery["next_frontier_id"])
        self.assertIn("No independent frontier item", recovery["next_action"])
        self.assertEqual(ready_items(frontier), [])
        self.assert_valid_ledger()

    def test_completed_frontier_cannot_be_reopened_as_ready(self):
        transaction_id = self.start_and_update()
        self.complete(transaction_id)
        with self.assertRaisesRegex(ValueError, "not actionable"):
            begin_transaction(
                self.root, "Q-0001", "Repeat closed question.",
                transaction_id="TX-NEW-0001",
            )

    def test_block_operation_marks_line_and_selects_independent_item(self):
        transaction_id = self.start_and_update("TX-20261014-0002")
        result = block_transaction(
            self.root, transaction_id,
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

    def test_block_final_ready_item_closes_to_valid_exhausted_state(self):
        frontier, _, _ = self.states()
        for item in frontier["items"]:
            if item["id"] != "Q-0001":
                item["status"] = "blocked_tool"
        (self.root / "research/FRONTIER.json").write_text(json.dumps(frontier), encoding="utf-8")
        transaction_id = self.start_and_update("TX-20261014-0007")
        result = block_transaction(
            self.root, transaction_id, blocker="fixture blocker",
            blocker_status="blocked_tool", evidence_ids=["EV-0002"],
        )
        _, recovery, _ = self.states()
        self.assertIsNone(result["next_item"])
        self.assertEqual(recovery["status"], "idle")
        self.assertIsNone(recovery["next_frontier_id"])
        self.assert_valid_ledger()

    def test_duplicate_action_without_new_evidence_or_discriminant_is_rejected(self):
        transaction_id = self.start_and_update("TX-20261014-0003")
        with self.assertRaisesRegex(ValueError, "new evidence or a new predicted discriminant"):
            update_transaction(
                self.root, transaction_id,
                action_key="read-source", outcome="repeated the same query",
                next_action="Continue.",
            )
        self.assert_valid_ledger()

    def test_interrupted_investigation_resumes_without_id_and_blocks_duplicates(self):
        transaction_id = self.start_and_update("TX-20261014-0004")
        recovered = recover_transaction(self.root)
        self.assertEqual(recovered["status"], "interrupted")
        with self.assertRaisesRegex(ValueError, "active or interrupted transaction"):
            begin_transaction(self.root, "Q-0003", "Start a duplicate.", transaction_id="TX-DUP-0001")
        resumed = resume_transaction(self.root)
        self.assertEqual(resumed["id"], transaction_id)
        _, recovery, ledger = self.states()
        self.assertEqual(recovery["status"], "running")
        self.assertEqual(ledger["transactions"][0]["status"], "running")
        self.assert_valid_ledger()

    def test_transaction_ids_are_generated_uniquely_and_never_reused(self):
        first = begin_transaction(self.root, "Q-0001", "Inspect first source.")
        self.assertRegex(first["id"], r"^TX-\d{8}-\d{4}$")
        update_transaction(
            self.root, first["id"], action_key="observe", outcome="observed fixture",
            next_action="Close first fixture.", evidence_ids=["EV-0001"],
        )
        self.complete(first["id"])
        with self.assertRaisesRegex(ValueError, "transaction ID already exists"):
            begin_transaction(
                self.root, "Q-0003", "Try reusing a completed ID.",
                transaction_id=first["id"],
            )
        second = begin_transaction(self.root, "Q-0003", "Inspect second source.")
        self.assertNotEqual(first["id"], second["id"])

    def test_complete_requires_update_and_known_evidence(self):
        transaction = begin_transaction(self.root, "Q-0001", "Inspect evidence.", transaction_id="TX-20261014-0005")
        with self.assertRaisesRegex(ValueError, "requires at least one validated update"):
            self.complete(transaction["id"], evidence_ids=["EV-0001"])

    def test_artifact_paths_and_synthesis_records_are_validated(self):
        transaction_id = begin_transaction(
            self.root, "Q-0001", "Inspect the source.", transaction_id="TX-20261014-0006",
        )["id"]
        with self.assertRaisesRegex(ValueError, "artifact does not exist"):
            update_transaction(
                self.root, transaction_id, action_key="inspect",
                outcome="captured an observation", next_action="Continue.",
                evidence_ids=["EV-0001"], artifacts=["raw/missing.txt"],
            )
        update_transaction(
            self.root, transaction_id, action_key="inspect-valid",
            outcome="captured an observation with a valid fixture artifact",
            next_action="Close after checking claim links.", evidence_ids=["EV-0002"],
            artifacts=["raw/observation.txt"],
        )
        with self.assertRaisesRegex(ValueError, "does not cite this transaction's evidence"):
            self.complete(transaction_id, synthesis_claim_ids=["CL-0001"])

    def test_python_cli_uses_generated_id_and_autonomously_reselects(self):
        command = [sys.executable, str(ROOT / "scripts" / "research_transactions.py"), "--root", str(self.root)]
        begin = subprocess.run(
            [*command, "begin", "Q-0001", "--next-action", "Read the fixture."],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(begin.returncode, 0, begin.stderr)
        tx_id = json.loads(begin.stdout)["id"]
        update = subprocess.run(
            [*command, "update", tx_id, "--action-key", "fixture-source",
             "--outcome", "Recorded the fixture observation.",
             "--next-action", "Close the fixture transaction.", "--evidence", "EV-0001"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(update.returncode, 0, update.stderr)
        complete = subprocess.run(
            [*command, "complete", tx_id, "--summary", "Fixture transaction completed.",
             "--cross-domain-assessment", "No cross-domain model is supported by this fixture.",
             "--graph-action", "No graph edge is justified by fixture evidence.", "--evidence", "EV-0001"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(complete.returncode, 0, complete.stderr)
        result = json.loads(complete.stdout)
        self.assertEqual(result["transaction"]["status"], "completed")
        self.assertEqual(result["transaction"]["frontier_resolution"]["status"], "completed")
        self.assertEqual(result["next_item"]["id"], "Q-0002")
        validate = subprocess.run(
            [*command, "validate"], capture_output=True, text=True, check=False,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertTrue(json.loads(validate.stdout)["ok"])

        # Simulate a later cold start in separate processes: the next item is
        # generated from the persisted recovery pointer, and an interrupted
        # investigation is resumed without a caller-supplied transaction ID.
        begin_next = subprocess.run(
            [*command, "begin", "Q-0002", "--next-action", "Read the second fixture source."],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(begin_next.returncode, 0, begin_next.stderr)
        second_id = json.loads(begin_next.stdout)["id"]
        self.assertNotEqual(second_id, tx_id)
        update_next = subprocess.run(
            [*command, "update", second_id, "--action-key", "second-fixture-source",
             "--outcome", "Recorded the second fixture observation.",
             "--next-action", "Close the second fixture transaction.", "--evidence", "EV-0002"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(update_next.returncode, 0, update_next.stderr)
        recover = subprocess.run(
            [*command, "recover"], capture_output=True, text=True, check=False,
        )
        self.assertEqual(recover.returncode, 0, recover.stderr)
        self.assertEqual(json.loads(recover.stdout)["status"], "interrupted")
        resume = subprocess.run(
            [*command, "resume"], capture_output=True, text=True, check=False,
        )
        self.assertEqual(resume.returncode, 0, resume.stderr)
        self.assertEqual(json.loads(resume.stdout)["id"], second_id)
        complete_next = subprocess.run(
            [*command, "complete", second_id, "--summary", "Second fixture resolved.",
             "--cross-domain-assessment", "The second fixture supports no shared mechanism.",
             "--graph-action", "No graph edge is supported by the second fixture.", "--evidence", "EV-0002"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(complete_next.returncode, 0, complete_next.stderr)
        self.assertEqual(json.loads(complete_next.stdout)["next_item"]["id"], "Q-0003")
        final_validate = subprocess.run(
            [*command, "validate"], capture_output=True, text=True, check=False,
        )
        self.assertEqual(final_validate.returncode, 0, final_validate.stderr)
        self.assertTrue(json.loads(final_validate.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
