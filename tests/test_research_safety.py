from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import research_safety as safety


class ResearchSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_check_write_rejects_binary_and_save_targets(self):
        paths = [
            r"C:\Games\Skyrim Special Edition\Data\MyMod.esp",
            "/tmp/fixture.esm",
            "test.ess",
            "test.skse",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertIsNotNone(safety.check_write(path, []))

    def test_check_write_rejects_configured_game_roots_case_insensitively(self):
        target = r"c:\games\skyrim special edition\Data\Scripts\probe.pex"
        self.assertIsNotNone(safety.check_write(target, [r"C:\Games\Skyrim Special Edition"]))

    def test_check_write_rejects_game_shaped_paths_without_local_config(self):
        self.assertIsNotNone(safety.check_write("Data/Scripts/Probe.psc", []))
        self.assertIsNotNone(safety.check_write("Documents/My Games/Skyrim Special Edition/Skyrim.ini", []))

    def test_check_write_allows_research_workspace_text_files(self):
        self.assertIsNone(safety.check_write("research/CLAIMS.md", []))

    def test_snapshot_copies_exact_files_and_records_hashes(self):
        root = self.tmp_path / "repo"
        source = root / "research" / "notes.md"
        source.parent.mkdir(parents=True)
        source.write_text("raw evidence\n", encoding="utf-8")
        backup_root = root / ".research-backups"
        with patch.object(safety, "ROOT", root), patch.object(safety, "BACKUP_ROOT", backup_root):
            self.assertEqual(safety.snapshot(["research/notes.md"]), 0)
        snapshots = list(backup_root.iterdir())
        self.assertEqual(len(snapshots), 1)
        manifest = json.loads((snapshots[0] / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["files"][0]["path"], "research/notes.md")
        self.assertEqual((snapshots[0] / "research/notes.md").read_text(encoding="utf-8"), "raw evidence\n")

    def test_snapshot_rejects_path_escape_and_save_files(self):
        root = self.tmp_path / "repo"
        root.mkdir()
        with patch.object(safety, "ROOT", root), patch.object(safety, "BACKUP_ROOT", root / ".research-backups"):
            outside = self.tmp_path / "outside.md"
            outside.write_text("private\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                safety._safe_snapshot_source("../outside.md")
            (root / "save.ess").write_bytes(b"protected")
            with self.assertRaises(ValueError):
                safety._safe_snapshot_source("save.ess")


if __name__ == "__main__":
    unittest.main()
