from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.ghidra_probe import GhidraProbeError, _normalize_windows_path, _windows_path, resolve_binding, run_query


class GhidraProbeTests(unittest.TestCase):
    def _fixture(self):
        temporary = tempfile.TemporaryDirectory()
        base = Path(temporary.name)
        root = base / "toolkit"
        root.mkdir()
        script_dir = root / "tools" / "ghidra_scripts"
        script_dir.mkdir(parents=True)
        (script_dir / "ReadOnlyTargetedQuery.java").write_text("// fixture", encoding="utf-8")
        legacy = base / "legacy-skyrim"
        project = legacy / "data" / "ghidra_project"
        project.mkdir(parents=True)
        (project / "skyrim-gog.gpr").write_bytes(b"existing project marker")
        (project / "skyrim-gog.rep").mkdir()
        ghidra = base / "ghidra"
        headless = ghidra / "support" / "analyzeHeadless.bat"
        headless.parent.mkdir(parents=True)
        headless.write_text("@echo off\n", encoding="utf-8")
        exe = legacy / "GOG" / "SkyrimSE.exe"
        exe.parent.mkdir()
        exe.write_bytes(b"fixture GOG executable")
        config = {
            "LEGACY_SKYRIM_REPO": str(legacy),
            "GHIDRA_HEADLESS_EXE": str(headless),
            "GHIDRA_PROJECT_DIR": str(project),
            "GHIDRA_PROJECT_NAME": "skyrim-gog",
            "GHIDRA_PROJECT_PROGRAM": "SkyrimSE.exe",
            "GHIDRA_ANALYSIS_EXE_GOG": str(exe),
            # These are the separate runtime target and must not select Ghidra.
            "GAME_ROOT": r"C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition",
            "SKYRIM_EXE_PATH": r"C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition\SkyrimSE.exe",
        }
        return temporary, root, legacy, project, headless, exe, config

    def test_mounted_windows_path_preserves_spaces(self):
        self.assertEqual(_windows_path(Path("/mnt/c/Program Files/Ghidra")), r"C:\Program Files\Ghidra")

    def test_path_outside_mounted_drive_fails_closed_on_linux(self):
        with self.assertRaisesRegex(GhidraProbeError, "mounted Windows drive"):
            _windows_path(Path("/tmp/not-a-windows-path"))

    def test_normalize_ghidra_import_path(self):
        self.assertEqual(
            _normalize_windows_path("/C:/Program Files/GOG/SkyrimSE.exe"),
            _normalize_windows_path(r"C:\Program Files\GOG\SkyrimSE.exe"),
        )

    def test_existing_gog_binding_is_resolved_without_using_runtime_path(self):
        temporary, root, legacy, project, headless, exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        with patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"):
            binding = resolve_binding(config, root=root)
        self.assertEqual(binding["project_name"], "skyrim-gog")
        self.assertEqual(binding["program_name"], "SkyrimSE.exe")
        self.assertEqual(binding["project_dir"], project)
        self.assertEqual(binding["executable"], exe)
        self.assertNotEqual(binding["executable"], Path(config["SKYRIM_EXE_PATH"]))

    def test_missing_project_config_fails_without_creating_a_project(self):
        temporary, root, _legacy, project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        config["GHIDRA_PROJECT_DIR"] = ""
        with patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"):
            with self.assertRaisesRegex(GhidraProbeError, "GHIDRA_PROJECT_DIR"):
                resolve_binding(config, root=root)
        self.assertTrue(project.is_dir())
        self.assertFalse((root / ".local").exists())

    def test_missing_project_files_fail_without_silent_replacement(self):
        temporary, root, _legacy, project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        (project / "skyrim-gog.gpr").unlink()
        with patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"):
            with self.assertRaisesRegex(GhidraProbeError, "configured GOG .gpr project is missing"):
                resolve_binding(config, root=root)
        self.assertFalse((project / "skyrim-gog.gpr").exists())

    def test_missing_local_config_fails_without_creating_a_project_or_config(self):
        temporary, root, _legacy, project, _headless, _exe, _config = self._fixture()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(GhidraProbeError, "config/local.env is missing"):
            run_query(root=root)
        self.assertTrue(project.is_dir())
        self.assertFalse((root / "config" / "local.env").exists())
        self.assertFalse((root / ".local").exists())

    def test_project_inside_harness_checkout_is_rejected(self):
        temporary, root, _legacy, _project, headless, exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        local_project = root / ".local" / "should-not-be-a-project"
        local_project.mkdir(parents=True)
        (local_project / "skyrim-gog.gpr").touch()
        (local_project / "skyrim-gog.rep").mkdir()
        config["GHIDRA_PROJECT_DIR"] = str(local_project)
        with patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"):
            with self.assertRaisesRegex(GhidraProbeError, "external local installation/project"):
                resolve_binding(config, root=root)
        self.assertTrue(headless.is_file())
        self.assertTrue(exe.is_file())

    def test_readonly_query_selects_gog_even_when_runtime_path_is_steam(self):
        temporary, root, _legacy, project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)

        def windows_path(path: Path) -> str:
            if path.name == "SkyrimSE.exe":
                return r"C:\GOG\SkyrimSE.exe"
            if path.name == "ghidra_project":
                return r"C:\legacy\data\ghidra_project"
            if path.name == "legacy-skyrim":
                return r"C:\legacy"
            if path.name == "support":
                return r"C:\ghidra\support"
            if path.name == "ghidra_scripts":
                return r"C:\toolkit\tools\ghidra_scripts"
            return r"C:\toolkit\.local\ghidra\file"

        stdout = (
            b"PROGRAM_EXECUTABLE_PATH=/C:/GOG/SkyrimSE.exe (GhidraScript)\n"
            b"FUNCTION_COUNT=12\nFUNCTION_LOOKUP=FUN_140001000 @ 140001000\n"
            b"XREF_CALL_EDGE=140001010 -> 140001000 target=FUN_140001000\n"
            b"DISASM=140001000 PUSH RBX\nDISASSEMBLY_INSTRUCTION_COUNT=1\n"
            b"DECOMPILATION_BEGIN=FUN_140001000\nreturn;\nDECOMPILATION_END=FUN_140001000\n"
        )
        with (
            patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"),
            patch("tools.ghidra_probe._windows_path", side_effect=windows_path),
            patch("tools.ghidra_probe._cmd_executable", return_value="cmd.exe"),
            patch("tools.ghidra_probe.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")) as run,
        ):
            result = run_query(root=root, config=config, timeout=30)

        self.assertTrue(result["ok"])
        self.assertEqual(result["analysis_distribution"], "GOG")
        self.assertTrue(result["program_executable_path_matches_gog_binary"])
        self.assertTrue(result["auto_analysis_disabled"])
        self.assertTrue(result["read_only"])
        self.assertFalse(result["import_attempted"])
        self.assertEqual(result["checks"]["function_lookup"], True)
        self.assertEqual(result["checks"]["xref_call_edge"], True)
        self.assertEqual(result["checks"]["disassembly"], True)
        self.assertEqual(result["checks"]["decompilation"], True)
        command = next((root / ".local" / "ghidra").glob("*.cmd")).read_text(encoding="utf-8")
        self.assertIn('"skyrim-gog"', command)
        self.assertIn('-process "SkyrimSE.exe" -noanalysis -readOnly', command)
        self.assertEqual(result["analysis_binary_sha256"], hashlib.sha256(_exe.read_bytes()).hexdigest())
        self.assertNotIn("Steam", command)
        self.assertNotIn("-import", command)
        self.assertNotIn("-overwrite", command)
        self.assertNotIn("-deleteProject", command)
        self.assertTrue(project.is_dir())

    def test_build_attested_rva_is_passed_to_existing_project_and_verified(self):
        temporary, root, _legacy, project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        stdout = (
            b"PROGRAM_EXECUTABLE_PATH=/C:/GOG/SkyrimSE.exe (GhidraScript)\n"
            b"TARGET_RVA=0x14C020\nTARGET_ADDRESS=14014C020\n"
            b"FUNCTION_LOOKUP=FUN_14014C000 @ 14014C000\n"
            b"XREF_CALL_EDGE=14014C010 -> 14014C000 target=FUN_14014C000\n"
            b"DISASM=14014C000 PUSH RBX\nDISASSEMBLY_INSTRUCTION_COUNT=1\n"
            b"DECOMPILATION_BEGIN=FUN_14014C000\nreturn;\nDECOMPILATION_END=FUN_14014C000\n"
        )

        def windows_path(path: Path) -> str:
            if path.name == "SkyrimSE.exe":
                return r"C:\\GOG\\SkyrimSE.exe"
            return r"C:\\local\\path"

        with (
            patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"),
            patch("tools.ghidra_probe._windows_path", side_effect=windows_path),
            patch("tools.ghidra_probe._cmd_executable", return_value="cmd.exe"),
            patch("tools.ghidra_probe.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")) as run,
        ):
            result = run_query(root=root, config=config, timeout=30, rva=0x14C020)

        self.assertTrue(result["ok"])
        self.assertEqual(result["requested_rva"], "0x14C020")
        self.assertTrue(result["checks"]["requested_rva_lookup"])
        command = next((root / ".local" / "ghidra").glob("*.cmd")).read_text(encoding="utf-8")
        self.assertIn('-process "SkyrimSE.exe" -noanalysis -readOnly', command)
        self.assertIn(' -postScript "ReadOnlyTargetedQuery.java" 0x14C020', command)
        self.assertNotIn("-import", command)
        self.assertNotIn("-overwrite", command)
        run.assert_called_once()
        self.assertTrue(project.is_dir())

    def test_negative_or_unreasonably_large_rva_fails_before_local_access(self):
        with self.assertRaisesRegex(GhidraProbeError, "non-negative 63-bit"):
            run_query(root=Path("/missing"), config={}, rva=-1)
        with self.assertRaisesRegex(GhidraProbeError, "non-negative 63-bit"):
            run_query(root=Path("/missing"), config={}, rva=2**63)

    def test_wrong_project_program_path_fails_the_query(self):
        temporary, root, _legacy, _project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        stdout = (
            b"PROGRAM_EXECUTABLE_PATH=/C:/Steam/SkyrimSE.exe\n"
            b"FUNCTION_LOOKUP=FUN_140001000\nXREF_CALL_EDGE=A -> B\n"
            b"DISASM=A MOV\nDISASSEMBLY_INSTRUCTION_COUNT=1\n"
            b"DECOMPILATION_BEGIN=FUN\nDECOMPILATION_END=FUN\n"
        )

        def windows_path(path: Path) -> str:
            return r"C:\GOG\SkyrimSE.exe" if path.name == "SkyrimSE.exe" else r"C:\local\path"

        with (
            patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"),
            patch("tools.ghidra_probe._windows_path", side_effect=windows_path),
            patch("tools.ghidra_probe._cmd_executable", return_value="cmd.exe"),
            patch("tools.ghidra_probe.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")),
        ):
            result = run_query(root=root, config=config)
        self.assertFalse(result["ok"])
        self.assertFalse(result["checks"]["program_identity_matches_gog_binary"])

    def test_ghidra_script_error_marker_fails_closed(self):
        temporary, root, _legacy, _project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        stdout = (
            b"ERROR REPORT SCRIPT ERROR\nPROGRAM_EXECUTABLE_PATH=/C:/GOG/SkyrimSE.exe\n"
            b"FUNCTION_LOOKUP=FUN_140001000\nXREF_CALL_EDGE=A -> B\n"
            b"DISASM=A MOV\nDISASSEMBLY_INSTRUCTION_COUNT=1\n"
            b"DECOMPILATION_BEGIN=FUN\nDECOMPILATION_END=FUN\n"
        )
        def windows_path(path: Path) -> str:
            return r"C:\GOG\SkyrimSE.exe" if path.name == "SkyrimSE.exe" else r"C:\local\path"
        with (
            patch("tools.ghidra_probe.read_executable_version", return_value="1.6.1179.0"),
            patch("tools.ghidra_probe._windows_path", side_effect=windows_path),
            patch("tools.ghidra_probe._cmd_executable", return_value="cmd.exe"),
            patch("tools.ghidra_probe.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")),
        ):
            result = run_query(root=root, config=config)
        self.assertFalse(result["ok"])
        self.assertFalse(result["checks"]["script_no_error"])

    def test_unsupported_analysis_binary_version_fails(self):
        temporary, root, _legacy, _project, _headless, _exe, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        with patch("tools.ghidra_probe.read_executable_version", return_value="1.5.97.0"):
            with self.assertRaisesRegex(GhidraProbeError, "not a supported AE"):
                resolve_binding(config, root=root)


if __name__ == "__main__":
    unittest.main()
