import unittest

from tools.domain_doctor import _synthetic_cosave_response


class DomainDoctorTests(unittest.TestCase):
    def test_skse_co_save_python_probe_returns_complete_fixture(self):
        result = _synthetic_cosave_response()
        self.assertTrue(result["response_ok"])
        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(result["coverage_pct"], 100.0)
        self.assertTrue(result["fixture_only"])


if __name__ == "__main__":
    unittest.main()
