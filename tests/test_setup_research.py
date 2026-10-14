from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import setup_research


class SetupResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_initialize_copies_private_config_once(self):
        config = self.tmp_path / "config"
        config.mkdir()
        example = config / "local.env.example"
        example.write_text("SKYRIM_EDITION=AE\n", encoding="utf-8")

        self.assertTrue(setup_research.initialize(self.tmp_path))
        local = config / "local.env"
        self.assertEqual(local.read_text(encoding="utf-8"), "SKYRIM_EDITION=AE\n")
        self.assertFalse(setup_research.initialize(self.tmp_path))

    def test_initialize_never_overwrites_existing_configuration(self):
        config = self.tmp_path / "config"
        config.mkdir()
        (config / "local.env.example").write_text("template\n", encoding="utf-8")
        local = config / "local.env"
        local.write_text("private user settings\n", encoding="utf-8")

        self.assertFalse(setup_research.initialize(self.tmp_path))
        self.assertEqual(local.read_text(encoding="utf-8"), "private user settings\n")

    def test_initialize_requires_template_and_does_not_create_fallback(self):
        with self.assertRaises(FileNotFoundError):
            setup_research.initialize(self.tmp_path)
        self.assertFalse((self.tmp_path / "config" / "local.env").exists())


if __name__ == "__main__":
    unittest.main()
