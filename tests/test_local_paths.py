from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.local_paths import doctor, sync
from scripts.local_config import read_local_config


class LocalPathRegistryTests(unittest.TestCase):
    def test_sync_fills_empty_values_and_doctor_hides_path_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local = root / ".local"
            config = root / "config"
            local.mkdir()
            config.mkdir()
            game = root / "game"
            game.mkdir()
            exe = game / "SkyrimSE.exe"
            exe.write_bytes(b"fixture")
            xedit = root / "xEdit.exe"
            xedit.write_bytes(b"fixture")
            source = root / "private_export.json"
            source.write_text('{"messages": []}', encoding="utf-8")
            registry = f'''\n[target]\nraw_uesp_dump = "{source.as_posix()}"\n[configured_paths]\nskyrim_exe = "{exe.as_posix()}"\nsseedit_exe = "{xedit.as_posix()}"\n[private_sources]\napocrypha_json = "{source.as_posix()}"\n'''
            (local / "research-paths.toml").write_text(registry, encoding="utf-8")
            (config / "local.env.example").write_text("SKYRIM_EDITION=AE\nGAME_ROOT=\nPLUGINS_TXT=\n", encoding="utf-8")
            (config / "local.env").write_text("SKYRIM_EDITION=AE\nGAME_ROOT=\nPLUGINS_TXT=\n", encoding="utf-8")

            report = sync(root)
            values = read_local_config(root)
            status = doctor(root)

            self.assertGreater(report["updated_values"], 0)
            self.assertEqual(values["GAME_ROOT"], game.as_posix())
            self.assertEqual(values["SKYRIM_EXE_PATH"], exe.as_posix())
            self.assertEqual(values["PLUGINS_TXT"], "")
            self.assertTrue(status["configured_executable_exists"])
            self.assertFalse(status["active_plugins_txt_configured"])
            self.assertFalse(status["product_version_verified"])
            encoded = json.dumps(status)
            self.assertNotIn(exe.as_posix(), encoded)
            self.assertNotIn(source.as_posix(), encoded)

    def test_sync_preserves_existing_nonempty_values_unless_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".local").mkdir()
            (root / "config").mkdir()
            exe = root / "candidate.exe"
            (root / ".local" / "research-paths.toml").write_text(
                f'[configured_paths]\nskyrim_exe = "{exe.as_posix()}"\n', encoding="utf-8"
            )
            (root / "config" / "local.env.example").write_text("", encoding="utf-8")
            (root / "config" / "local.env").write_text("GAME_ROOT='user-choice'\nPLUGINS_TXT='profile-choice'\n", encoding="utf-8")

            sync(root)
            values = read_local_config(root)
            self.assertEqual(values["GAME_ROOT"], "user-choice")
            self.assertEqual(values["PLUGINS_TXT"], "profile-choice")


if __name__ == "__main__":
    unittest.main()
