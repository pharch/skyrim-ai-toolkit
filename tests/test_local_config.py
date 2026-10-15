from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.local_config import LocalConfigError, parse_local_config, read_local_config


class LocalConfigTests(unittest.TestCase):
    def test_comments_quoted_values_and_empty_values(self):
        result = parse_local_config(
            "# note\nSKYRIM_EDITION=AE\nGAME_ROOT='C:\\\\Games\\\\Skyrim'\nOPTIONAL=\"\"\n"
        )
        self.assertEqual(result["SKYRIM_EDITION"], "AE")
        self.assertEqual(result["GAME_ROOT"], "C:\\\\Games\\\\Skyrim")
        self.assertEqual(result["OPTIONAL"], "")

    def test_malformed_line_is_rejected(self):
        with self.assertRaisesRegex(LocalConfigError, "expected KEY=VALUE"):
            parse_local_config("SKYRIM_EDITION=AE\nnot-a-binding\n")

    def test_invalid_key_is_rejected(self):
        with self.assertRaisesRegex(LocalConfigError, "invalid configuration key"):
            parse_local_config("lowercase=value\n")

    def test_duplicate_key_is_rejected(self):
        with self.assertRaisesRegex(LocalConfigError, "duplicate key SKYRIM_EDITION"):
            parse_local_config("SKYRIM_EDITION=AE\nSKYRIM_EDITION=SE\n")

    def test_unmatched_quote_is_rejected(self):
        with self.assertRaisesRegex(LocalConfigError, "unmatched quote"):
            parse_local_config("GAME_ROOT='C:\\Games\n")

    def test_malformed_local_file_is_reported_instead_of_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config" / "local.env"
            config.parent.mkdir()
            config.write_text("SKYRIM_EDITION=AE\nBAD LINE\n", encoding="utf-8")
            with self.assertRaises(LocalConfigError):
                read_local_config(root)


if __name__ == "__main__":
    unittest.main()
