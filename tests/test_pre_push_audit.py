from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.pre_push_audit import audit


class PrePushAuditTests(unittest.TestCase):
    def test_ignored_local_tree_is_verified_without_recursive_walk(self):
        with patch.object(Path, "rglob", side_effect=AssertionError("private tree was traversed")):
            result = audit()

        self.assertTrue(result["local_root_ignored"])
        self.assertEqual(result["ignored_local_heavy_inventory"], "not_scanned_private_ignored_tree")
        self.assertIsNone(result["ignored_local_heavy_file_count"])
        self.assertTrue(result["pass"])


if __name__ == "__main__":
    unittest.main()
