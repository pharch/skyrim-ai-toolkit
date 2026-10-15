import unittest

from scripts.harness_doctor import _overall_exit, _status_for_failure


class HarnessDoctorTests(unittest.TestCase):
    def test_overall_exit_distinguishes_pass_blocked_and_failure(self):
        self.assertEqual(_overall_exit([{"status": "PASS"}]), 0)
        self.assertEqual(_overall_exit([{"status": "PASS"}, {"status": "BLOCKED_EXTERNAL"}]), 2)
        self.assertEqual(_overall_exit([{"status": "BLOCKED_EXTERNAL"}, {"status": "FAIL"}]), 1)

    def test_unverified_optional_live_capabilities_do_not_block_static_readiness(self):
        self.assertEqual(_overall_exit([
            {"status": "PASS"},
            {"status": "NOT_CONFIGURED"},
            {"status": "NOT_VERIFIED"},
        ]), 0)

    def test_native_identity_bridge_errors_are_blocked_not_negative_findings(self):
        self.assertEqual(_status_for_failure("could not read GOG executable ProductVersion"), "BLOCKED_EXTERNAL")
        self.assertEqual(_status_for_failure("PowerShell did not return a Skyrim ProductVersion"), "BLOCKED_EXTERNAL")
        self.assertEqual(_status_for_failure("record was not found in a verified export"), "FAIL")


if __name__ == "__main__":
    unittest.main()

