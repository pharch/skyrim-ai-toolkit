import unittest

from scripts.research_state import recover_checkpoint, transition_item


class ResearchStateRecoveryTests(unittest.TestCase):
    def test_recover_running_checkpoint_records_interruption_and_resume_action(self):
        checkpoint = {
            "schema_version": 2,
            "status": "running",
            "next_action": "Inspect the raw output and compare the durable diff.",
        }

        recovered = recover_checkpoint(checkpoint)

        self.assertEqual(recovered["status"], "interrupted")
        self.assertEqual(recovered["next_action"], checkpoint["next_action"])
        self.assertTrue(recovered["interrupted_utc"])
        self.assertIn("Resume from next_action", recovered["resume_action"])

    def test_recover_checkpoint_rejects_running_state_without_next_action(self):
        with self.assertRaisesRegex(ValueError, "actionable next_action"):
            recover_checkpoint({"status": "running", "next_action": "  "})

    def test_terminal_decision_requires_successors(self):
        frontier = {"items": [
            {"id": "Q-0001", "status": "in_progress", "successors": []},
            {"id": "Q-0002", "status": "open", "successors": []},
        ]}
        with self.assertRaisesRegex(ValueError, "successors"):
            transition_item(
                frontier, "Q-0001", "completed", evidence_ids=["EV-0001"],
                decision={"summary": "done", "cross_domain_assessment": "checked", "successors": []},
                available_evidence={"EV-0001"},
            )

    def test_terminal_decision_links_a_successor_question(self):
        frontier = {"items": [
            {"id": "Q-0001", "status": "in_progress", "successors": []},
            {"id": "Q-0002", "status": "open", "successors": []},
        ]}
        transition_item(
            frontier, "Q-0001", "completed", evidence_ids=["EV-0001"],
            decision={"summary": "done", "cross_domain_assessment": "checked", "successors": ["Q-0002"]},
            available_evidence={"EV-0001"},
        )
        self.assertEqual(frontier["items"][0]["successors"], ["Q-0002"])
        self.assertEqual(frontier["items"][0]["decision"]["evidence"], ["EV-0001"])
