from pathlib import Path
import tempfile
import unittest

from scripts.markdown_policy_audit import markdown_files
from scripts.validate_overlay import _validate_markdown_links


class MarkdownPolicyAuditTests(unittest.TestCase):
    def test_prunes_local_storage_before_descent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".local" / "large-project").mkdir(parents=True)
            (root / ".local" / "large-project" / "private.md").write_text("private")
            (root / "docs").mkdir()
            (root / "docs" / "active.md").write_text("active")

            result = markdown_files(root)
            link_errors = _validate_markdown_links(root)

        self.assertEqual([path.name for path in result], ["active.md"])
        self.assertEqual(link_errors, [])


if __name__ == "__main__":
    unittest.main()
