import hashlib
from contextlib import redirect_stderr
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.ae_target import TargetError
from tools.ghidra_probe import _attested_existing_project_target, _windows_path, main


class GhidraProbeTests(unittest.TestCase):
    def _attested_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        local = root / ".local" / "readiness"
        local.mkdir(parents=True)
        game_root = root / "game"
        game_root.mkdir()
        executable = game_root / "SkyrimSE.exe"
        executable.write_bytes(b"verified AE executable fixture")
        image_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
        version_capture = local / "version.stdout.raw"
        version_capture.write_text("ProductVersion=1.6.1170.0\n", encoding="utf-8")
        project_dir = local / "ghidra" / "project_AE_SkyrimSE_1_6_1170_attempt2"
        project_dir.mkdir(parents=True)
        metadata_path = local / "ghidra" / "analysis-attempt2.meta.json"
        metadata = {"project_name": "AE_SkyrimSE_1_6_1170_attempt2", "input_sha256": image_hash}
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        long_project_dir = local / "ghidra" / "project_AE_SkyrimSE_1_6_1170_longanalysis"
        long_project_dir.mkdir()
        long_metadata_path = local / "ghidra" / "AE_SkyrimSE_1_6_1170_longanalysis.meta.json"
        long_metadata_path.write_text(json.dumps({
            "project_name": "AE_SkyrimSE_1_6_1170_longanalysis",
            "input_sha256": image_hash,
        }), encoding="utf-8")
        long_stdout_path = local / "ghidra" / "AE_SkyrimSE_1_6_1170_longanalysis.stdout.raw"
        long_stdout_path.write_bytes(b"analysis saved after timeout\n")
        evidence = {
            "schema_version": 1,
            "items": [
                {
                    "id": "EV-0109", "edition": "AE", "runtime": "1.6.1170",
                    "source": f"ProductVersion probe; input SHA256 {image_hash}",
                    "artifact": "private-local:.local/readiness/version.stdout.raw",
                    "sha256": hashlib.sha256(version_capture.read_bytes()).hexdigest(),
                },
                {
                    "id": "EV-0113", "edition": "AE", "runtime": "1.6.1170",
                    "source": f"Ghidra import; input SHA256 {image_hash}",
                    "artifact": "private-local:.local/readiness/ghidra/analysis-attempt2.meta.json",
                    "sha256": hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
                },
                {
                    "id": "EV-0139", "edition": "AE", "runtime": "1.6.1170",
                    "source": f"Ghidra analysis session; input SHA256 {image_hash}",
                    "artifact": "private-local:.local/readiness/ghidra/AE_SkyrimSE_1_6_1170_longanalysis.stdout.raw",
                    "sha256": hashlib.sha256(long_stdout_path.read_bytes()).hexdigest(),
                    "metadata_artifact": "private-local:.local/readiness/ghidra/AE_SkyrimSE_1_6_1170_longanalysis.meta.json",
                    "metadata_sha256": hashlib.sha256(long_metadata_path.read_bytes()).hexdigest(),
                },
            ],
        }
        (root / "research").mkdir()
        (root / "research" / "EVIDENCE.json").write_text(json.dumps(evidence), encoding="utf-8")
        return temporary, root, game_root, executable, project_dir, long_project_dir

    def test_mounted_windows_path_is_quoted_by_caller_and_mapped_without_loss(self):
        self.assertEqual(_windows_path(Path("/mnt/c/Program Files/Ghidra")), r"C:\Program Files\Ghidra")

    def test_non_windows_host_paths_outside_a_mounted_drive_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "mounted Windows drive"):
            _windows_path(Path("/tmp/not-a-windows-path"))

    def test_result_distinguishes_missing_xref_from_function_and_disassembly_outputs(self):
        script = Path(__file__).parents[1] / "tools" / "ghidra_scripts" / "ReadOnlyTargetedQuery.java"
        source = script.read_text(encoding="utf-8")
        self.assertIn("FUNCTION_LOOKUP=", source)
        self.assertIn("DISASM=", source)
        self.assertIn("XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT", source)
        self.assertNotIn('throw new IllegalStateException("No direct call reference between analyzed functions was found")', source)

    def test_attested_existing_project_query_requires_same_verified_image_hash(self):
        temporary, root, game_root, _executable, project_dir, _long_project_dir = self._attested_fixture()
        self.addCleanup(temporary.cleanup)
        target = _attested_existing_project_target(
            root=root,
            config={"GAME_ROOT": str(game_root)},
            project_dir=project_dir,
            project_name="AE_SkyrimSE_1_6_1170_attempt2",
        )
        self.assertEqual(target["version"], "1.6.1170")
        self.assertEqual(target["edition"], "AE")

    def test_attested_existing_project_query_rejects_changed_executable(self):
        temporary, root, game_root, executable, project_dir, _long_project_dir = self._attested_fixture()
        self.addCleanup(temporary.cleanup)
        executable.write_bytes(b"different executable")
        with self.assertRaisesRegex(RuntimeError, "current executable bytes"):
            _attested_existing_project_target(
                root=root,
                config={"GAME_ROOT": str(game_root)},
                project_dir=project_dir,
                project_name="AE_SkyrimSE_1_6_1170_attempt2",
            )

    def test_attested_existing_project_query_accepts_ev0139_longanalysis(self):
        temporary, root, game_root, _executable, _project_dir, long_project_dir = self._attested_fixture()
        self.addCleanup(temporary.cleanup)
        target = _attested_existing_project_target(
            root=root,
            config={"GAME_ROOT": str(game_root)},
            project_dir=long_project_dir,
            project_name="AE_SkyrimSE_1_6_1170_longanalysis",
        )
        self.assertEqual(target["version"], "1.6.1170")

    def test_attested_existing_project_query_rejects_unregistered_name(self):
        temporary, root, game_root, _executable, project_dir, _long_project_dir = self._attested_fixture()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(RuntimeError, "not in the hash-attested query allowlist"):
            _attested_existing_project_target(
                root=root,
                config={"GAME_ROOT": str(game_root)},
                project_dir=project_dir,
                project_name="unregistered-project",
            )

    def test_attested_longanalysis_rejects_changed_metadata(self):
        temporary, root, game_root, _executable, _project_dir, long_project_dir = self._attested_fixture()
        self.addCleanup(temporary.cleanup)
        metadata_path = root / ".local" / "readiness" / "ghidra" / "AE_SkyrimSE_1_6_1170_longanalysis.meta.json"
        metadata_path.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "saved project metadata artifact is missing or has changed"):
            _attested_existing_project_target(
                root=root,
                config={"GAME_ROOT": str(game_root)},
                project_dir=long_project_dir,
                project_name="AE_SkyrimSE_1_6_1170_longanalysis",
            )

    def test_target_errors_are_reported_as_json_not_tracebacks(self):
        error = StringIO()
        with patch("tools.ghidra_probe.run_query", side_effect=TargetError("unsupported Skyrim runtime")):
            with redirect_stderr(error):
                exit_code = main(["--timeout", "10"])
        self.assertEqual(exit_code, 2)
        self.assertIn('"error": "unsupported Skyrim runtime"', error.getvalue())


if __name__ == "__main__":
    unittest.main()
