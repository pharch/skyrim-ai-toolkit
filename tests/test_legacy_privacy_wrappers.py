from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class LegacyPrivacyWrapperTests(unittest.TestCase):
    def test_apocrypha_compatibility_wrappers_emit_no_private_fields(self) -> None:
        local = REPO / ".local"
        local.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=local) as tmp:
            root = Path(tmp)
            source = root / "synthetic.json"
            database = root / "synthetic.sqlite3"
            private_values = [
                "PRIVATE_SENTINEL_BODY_7df4",
                "PRIVATE_SENTINEL_AUTHOR_9b21",
                "PRIVATE_SENTINEL_CHANNEL_30c8",
                "PRIVATE_SENTINEL_MESSAGE_45a0",
            ]
            export = {
                "guild": {"id": "guild-id", "name": "PRIVATE_SENTINEL_GUILD"},
                "channel": {"id": private_values[2], "name": private_values[2]},
                "messageCount": 1,
                "messages": [
                    {
                        "id": private_values[3],
                        "timestamp": "2026-10-14T00:00:00Z",
                        "author": {"id": "author-id", "name": private_values[1]},
                        "content": private_values[0] + " armor XP blocked hit",
                    }
                ],
            }
            source.write_text(json.dumps(export), encoding="utf-8")
            indexed = subprocess.run(
                [sys.executable, "scripts/index_apocrypha.py", str(source), "--db", str(database)],
                cwd=REPO,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertNotIn("PRIVATE_SENTINEL", indexed.stdout)
            self.assertIn('"message_count": 1', indexed.stdout)
            searched = subprocess.run(
                [sys.executable, "scripts/search_apocrypha.py", "armor XP", "--db", str(database)],
                cwd=REPO,
                capture_output=True,
                text=True,
                check=True,
            )
            report = json.loads(searched.stdout)
            self.assertEqual(report["match_count"], 1)
            self.assertFalse(report["private_fields_emitted"])
            self.assertTrue(report["source_text_is_untrusted"])
            for value in private_values:
                self.assertNotIn(value, searched.stdout)

    def test_apocrypha_compatibility_wrapper_rejects_database_outside_local_storage(self) -> None:
        local = REPO / ".local"
        local.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=local) as tmp:
            root = Path(tmp)
            source = root / "synthetic.json"
            source.write_text(json.dumps({"messages": []}), encoding="utf-8")
            with tempfile.TemporaryDirectory() as public_tmp:
                public_db = Path(public_tmp) / "public.sqlite3"
                result = subprocess.run(
                    [sys.executable, "scripts/index_apocrypha.py", str(source), "--db", str(public_db)],
                    cwd=REPO,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("outside ignored .local/", result.stderr)


if __name__ == "__main__":
    unittest.main()
