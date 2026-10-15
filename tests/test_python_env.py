from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import python_env


class PythonEnvironmentTests(unittest.TestCase):
    def test_venv_path_is_platform_specific(self):
        root = Path("/checkout")
        self.assertEqual(python_env.venv_python(root, windows=False), root / ".venv/bin/python")
        self.assertEqual(python_env.venv_python(root, windows=True), root / ".venv/Scripts/python.exe")

    def test_wrong_interpreter_fails_probe(self):
        report = {
            "inside_repo_venv": False,
            "python_major_minor": [3, 12],
            "distribution_versions": {"lz4": "4.3.3", "PyYAML": "6.0.1"},
            "module_imports": {"lz4": True, "PyYAML": True},
            "config_present": True,
            "config_valid": True,
        }
        self.assertIn("wrong_interpreter", python_env.probe_failures(report))

    def test_missing_lz4_is_a_required_dependency_failure(self):
        failures = python_env.dependency_failures({"PyYAML": "6.0.1"})
        self.assertEqual(failures, ["lz4==4.3.3 (found missing)"])

    def test_wrong_required_package_version_fails(self):
        failures = python_env.dependency_failures({"lz4": "4.3.3", "PyYAML": "6.0.2"})
        self.assertEqual(failures, ["PyYAML==6.0.1 (found 6.0.2)"])

    def test_selected_and_disposable_profile_bindings_are_separate(self):
        result = python_env.external_binding_status({
            "MO2_PROFILE_DIR": "selected-profile",
            "PLUGINS_TXT": "selected-profile/plugins.txt",
            "SKYRIM_OBSERVER_STAGED_DLL": ".local/staged.dll",
        })
        self.assertTrue(result["selected_profile_configured"])
        self.assertFalse(result["disposable_test_profile_configured"])
        self.assertTrue(result["observer_staged_dll_configured"])
        self.assertFalse(result["observer_deployed_dll_configured"])
        self.assertFalse(result["live_bindings_configured"])

    def test_incomplete_environment_cannot_dispatch(self):
        with self.assertRaisesRegex(RuntimeError, "repository .venv is incomplete"):
            python_env.command_for(["-c", "pass"], interpreter="/system/python", ready=False)

    def test_successful_configured_launch_uses_repo_venv_and_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status = {"ready": True}
            with patch.object(python_env.subprocess, "run", return_value=type("Result", (), {"returncode": 0})()) as run:
                result = python_env.dispatch(["-c", "print('ok')"], root=root, status=status)
            self.assertEqual(result, 0)
            args, kwargs = run.call_args
            self.assertEqual(args[0][0], str(python_env.venv_python(root)))
            self.assertEqual(args[0][1:], ["-c", "print('ok')"])
            self.assertEqual(kwargs["cwd"], root)

    def test_missing_venv_is_reported_without_system_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            (root / "config/local.env").write_text("SKYRIM_EDITION=AE\n", encoding="utf-8")
            status = python_env.environment_status(root)
        self.assertFalse(status["ready"])
        self.assertEqual(status["python_status"], "FAIL_VENV_MISSING")
        self.assertTrue(status["config_present"])
        self.assertTrue(status["config_valid"])
        self.assertNotIn("system_python_supported", status)

    def test_fresh_process_uses_local_config_through_dispatcher(self):
        status = python_env.environment_status()
        if not status["ready"]:
            self.skipTest("repository .venv and local config are not ready")
        code = (
            "import json; from scripts.local_config import read_local_config; "
            "print(json.dumps({'config_loaded': bool(read_local_config())}))"
        )
        result = subprocess.run(
            [sys.executable, "scripts/python_env.py", "run", "-c", code],
            cwd=python_env.ROOT, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout.strip())["config_loaded"])


if __name__ == "__main__":
    unittest.main()
