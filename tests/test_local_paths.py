from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.local_paths import _native_path, doctor


class LocalPathDoctorTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "config").mkdir()
        return temporary, root

    def test_doctor_reads_only_local_env_and_hides_bound_paths(self):
        temporary, root = self._root()
        self.addCleanup(temporary.cleanup)
        local = root / ".local"
        local.mkdir()
        project = root / "external-project"
        project.mkdir()
        (project / "skyrim-gog.gpr").touch()
        (project / "skyrim-gog.rep").mkdir()
        gog = root / "external" / "GOG" / "SkyrimSE.exe"
        gog.parent.mkdir(parents=True)
        gog.touch()
        commonlib = root / "external" / "CommonLibSSE-NG"
        (commonlib / "include" / "RE").mkdir(parents=True)
        (commonlib / "include" / "RE" / "Offsets.h").touch()
        java = root / "external" / "Java" / "bin"
        java.mkdir(parents=True)
        (java / "java.exe").touch()
        (local / "research-paths.toml").write_text(
            '[configured_paths]\nghidra_home = "wrong-old-registry"\n', encoding="utf-8"
        )
        (root / "config" / "local.env").write_text(
            f"GHIDRA_PROJECT_REP_PATH='{(project / 'skyrim-gog.rep').as_posix()}'\n"
            "GHIDRA_PROJECT_PROGRAM='SkyrimSE.exe'\n"
            f"GHIDRA_ANALYSIS_EXE_GOG='{gog.as_posix()}'\n"
            f"COMMONLIBSSE_ROOT='{commonlib.as_posix()}'\n"
            f"JAVA_HOME='{java.parent.as_posix()}'\n"
            "MO2_PROFILE_DIR=\nPLUGINS_TXT=\n",
            encoding="utf-8",
        )

        status = doctor(root)
        encoded = json.dumps(status)
        self.assertEqual(status["canonical_registry"], "config/local.env")
        self.assertFalse(status["legacy_toml_registry_read"])
        self.assertTrue(status["existing_ghidra_project_files_present"])
        self.assertTrue(status["gog_analysis_executable_exists"])
        self.assertTrue(status["commonlibsse_source_exists"])
        self.assertTrue(status["java_home_executable_exists"])
        self.assertFalse(status["explicit_plugins_txt_configured_exists"])
        self.assertFalse(status["mo2_profile_dir_configured_exists"])
        self.assertNotIn(str(project), encoded)
        self.assertNotIn(str(gog), encoded)
        self.assertNotIn("wrong-old-registry", encoded)

    def test_doctor_relative_index_paths_resolve_from_checkout(self):
        temporary, root = self._root()
        self.addCleanup(temporary.cleanup)
        (root / ".local").mkdir()
        (root / ".local" / "uesp.sqlite3").touch()
        (root / ".local" / "apocrypha.sqlite3").touch()
        (root / "config" / "local.env").write_text(
            "UESP_INDEX_PATH=.local/uesp.sqlite3\nAPOCRYPHA_INDEX_PATH=.local/apocrypha.sqlite3\n",
            encoding="utf-8",
        )
        status = doctor(root)
        self.assertTrue(status["uesp_index_exists"])
        self.assertTrue(status["apocrypha_index_exists"])

    def test_verify_target_separates_executable_identity_from_full_order(self):
        temporary, root = self._root()
        self.addCleanup(temporary.cleanup)
        (root / "config" / "local.env").write_text("SKYRIM_EDITION=AE\n", encoding="utf-8")
        with (
            patch("tools.ae_target.assert_ae_target", return_value={"edition": "AE", "version": "1.6.1170"}),
            patch("tools.ae_target.preflight", side_effect=ValueError("set PLUGINS_TXT to selected MO2 profile")),
        ):
            status = doctor(root, verify_target=True)
        self.assertTrue(status["product_version_verified"])
        self.assertEqual(status["runtime"], "1.6.1170")
        self.assertFalse(status["full_active_order_verified"])
        self.assertIn("PLUGINS_TXT", status["active_order_error"])

    def test_windows_paths_map_to_mounted_drive_without_losing_spaces(self):
        self.assertEqual(str(_native_path(r"C:\Program Files\GOG Galaxy")),
                         "/mnt/c/Program Files/GOG Galaxy")


if __name__ == "__main__":
    unittest.main()
