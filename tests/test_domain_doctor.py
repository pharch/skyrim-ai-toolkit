import unittest
import tempfile
from pathlib import Path

from tools.domain_doctor import _sseedit_status, _synthetic_cosave_response, _tool_paths


class DomainDoctorTests(unittest.TestCase):
    def test_skse_co_save_python_probe_returns_complete_fixture(self):
        result = _synthetic_cosave_response()
        self.assertTrue(result["response_ok"])
        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(result["coverage_pct"], 100.0)
        self.assertTrue(result["fixture_only"])

    def test_domain_paths_use_canonical_gog_project_binding_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            headless = root / "Ghidra" / "support" / "analyzeHeadless.bat"
            headless.parent.mkdir(parents=True)
            headless.touch()
            project = root / "legacy" / "data" / "ghidra_project"
            project.mkdir(parents=True)
            (project / "skyrim-gog.gpr").touch()
            (project / "skyrim-gog.rep").mkdir()
            gog = root / "GOG" / "SkyrimSE.exe"
            gog.parent.mkdir()
            gog.touch()
            commonlib = root / "CommonLibSSE-NG"
            (commonlib / "include" / "RE").mkdir(parents=True)
            (commonlib / "include" / "RE" / "Offsets.h").touch()
            java_bin = root / "Java" / "bin"
            java_bin.mkdir(parents=True)
            (java_bin / "java.exe").touch()
            config = {
                "GHIDRA_HEADLESS_EXE": str(headless),
                "GHIDRA_PROJECT_DIR": str(project),
                "GHIDRA_PROJECT_NAME": "skyrim-gog",
                "GHIDRA_PROJECT_PROGRAM": "SkyrimSE.exe",
                "GHIDRA_ANALYSIS_EXE_GOG": str(gog),
                "JAVA_HOME": str(java_bin.parent),
                "COMMONLIBSSE_ROOT": str(commonlib),
            }
            paths = _tool_paths(config)
        self.assertTrue(paths["ghidra_headless_configured_exists"])
        self.assertTrue(paths["ghidra_project_present"])
        self.assertTrue(paths["gog_analysis_executable_exists"])
        self.assertTrue(paths["commonlibsse_offsets_header_present"])
        self.assertTrue(paths["java_home_configured_exists"])
        self.assertNotIn("ghidra_standard_launcher_exists", paths)

    def test_sseedit_status_labels_runtime_identity_separately(self):
        result = _sseedit_status(
            {"MO2_PROFILE_DIR": ""},
            {
                "sseedit_executable_configured_exists": True,
                "explicit_plugins_txt_configured_exists": False,
            },
            {"verified": False, "error": "PowerShell bridge unavailable"},
        )
        self.assertTrue(result["configured_executable_exists"])
        self.assertFalse(result["runtime_target"]["product_version_verified"])
        self.assertEqual(result["runtime_target"]["error"], "PowerShell bridge unavailable")
        self.assertNotIn("product_version_verified", result)
        self.assertFalse(result["selected_mo2_profile_configured"])
        self.assertFalse(result["full_active_order_verified"])
        self.assertFalse(result["xedit_call"])


if __name__ == "__main__":
    unittest.main()
