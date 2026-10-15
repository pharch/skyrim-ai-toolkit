from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from conftest import REPO

sys.path.insert(0, str(REPO / "tools"))
import skyrim_paths  # noqa: E402


class SkyrimPathTests(unittest.TestCase):
    def test_discovery_targets_only_the_ae_profile_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "My Games"
            (root / "Skyrim VR" / "SKSE").mkdir(parents=True)
            (root / "Skyrim" / "SKSE").mkdir(parents=True)
            ae = root / "Skyrim Special Edition" / "SKSE"
            ae.mkdir(parents=True)

            chosen, others = skyrim_paths.find_game_dir("SKSE", base=root)

            self.assertEqual(chosen, ae)
            self.assertEqual(others, [])

    def test_missing_ae_profile_does_not_fall_back_to_another_edition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "My Games"
            (root / "Skyrim VR" / "SKSE").mkdir(parents=True)

            chosen, others = skyrim_paths.find_game_dir("SKSE", base=root)

            self.assertEqual(chosen, root / "Skyrim Special Edition" / "SKSE")
            self.assertFalse(chosen.exists())
            self.assertEqual(others, [])

    def test_explicit_tool_path_override_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            override = Path(temporary) / "explicit" / "Papyrus"
            with patch.object(skyrim_paths, "read_local_config", return_value={"PAPYRUS_LOG_DIR": str(override)}):
                chosen, others = skyrim_paths.resolve_dir("PAPYRUS_LOG_DIR", "Logs/Script")

            self.assertEqual(chosen, override)
            self.assertEqual(others, [])

    def test_default_path_requires_canonical_local_config(self):
        with patch.object(skyrim_paths, "read_local_config", return_value={}):
            with self.assertRaisesRegex(ValueError, "SKYRIM_CONFIG_DIR"):
                skyrim_paths.resolve_dir("PAPYRUS_LOG_DIR", "Logs/Script")

    def test_ambiguous_game_folders_never_change_the_ae_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "My Games"
            for edition in ("Skyrim", "Skyrim VR", "Skyrim Special Edition"):
                (root / edition / "Logs" / "Script").mkdir(parents=True)

            chosen, others = skyrim_paths.find_game_dir("Logs/Script", base=root)

            self.assertEqual(chosen, root / "Skyrim Special Edition" / "Logs" / "Script")
            self.assertEqual(others, [])
