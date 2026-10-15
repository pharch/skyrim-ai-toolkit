from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import bootstrap_python
from scripts.python_env import REQUIRED_DISTRIBUTIONS


class PythonBootstrapTests(unittest.TestCase):
    def _existing_environment(self, root: Path) -> tuple[Path, Path]:
        env_dir = root / ".local" / "test-bootstrap" / "wsl"
        python = env_dir / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.write_text("preserve-this-test-interpreter", encoding="utf-8")
        return env_dir, python

    def _report(self, env_dir: Path, *, failures: list[str] | None = None) -> dict[str, object]:
        return {
            "python": [3, 12, 3],
            "prefix": str(env_dir.resolve()),
            "pip": True,
            "versions": dict(REQUIRED_DISTRIBUTIONS),
            "imports": {name: True for name in bootstrap_python.REQUIRED_MODULES},
            "failures": failures or [],
        }

    def test_healthy_environment_is_reused_without_recreation_or_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_dir, python = self._existing_environment(root)
            original = python.read_bytes()
            with (
                patch.object(bootstrap_python, "execution_host", return_value="wsl"),
                patch.object(bootstrap_python, "find_interpreter", return_value=("/usr/bin/python3.12", (3, 12, 3), [])),
                patch.object(bootstrap_python, "_repair_venv_prerequisite"),
                patch.object(bootstrap_python, "_probe_env", return_value=self._report(env_dir)),
                patch.object(bootstrap_python, "_run") as run,
            ):
                result = bootstrap_python.bootstrap(root=root, requested_env_dir=env_dir)
            self.assertEqual(result["action"], "reused")
            self.assertEqual(python.read_bytes(), original)
            run.assert_not_called()

    def test_missing_package_is_repaired_in_place_without_venv_recreation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_dir, python = self._existing_environment(root)
            before = self._report(env_dir, failures=["pytest==8.0.0 required; found missing"])
            after = self._report(env_dir)
            completed = subprocess.CompletedProcess([], 0, "ok\n", "")
            with (
                patch.object(bootstrap_python, "execution_host", return_value="wsl"),
                patch.object(bootstrap_python, "find_interpreter", return_value=("/usr/bin/python3.12", (3, 12, 3), [])),
                patch.object(bootstrap_python, "_repair_venv_prerequisite"),
                patch.object(bootstrap_python, "_probe_env", side_effect=[before, before, after]),
                patch.object(bootstrap_python, "_module_check", return_value=True),
                patch.object(bootstrap_python, "_run", return_value=completed) as run,
            ):
                result = bootstrap_python.bootstrap(root=root, requested_env_dir=env_dir)
            self.assertEqual(result["action"], "repaired")
            self.assertTrue((env_dir / ".harness-bootstrap.json").is_file())
            self.assertTrue(python.is_file())
            commands = [tuple(call.args[0]) for call in run.call_args_list]
            self.assertTrue(any(command[1:3] == ("-m", "pip") and "install" in command for command in commands))
            self.assertFalse(any(command[1:3] == ("-m", "venv") for command in commands))


if __name__ == "__main__":
    unittest.main()
