import unittest

from scripts.python_env import ENV_NAME, active_environment, command_for, parse_run_args


class PythonEnvironmentTests(unittest.TestCase):
    def test_active_environment_runs_its_python_directly(self):
        command = command_for(["-m", "pytest"], env={"CONDA_DEFAULT_ENV": ENV_NAME},
                              prefix="/envs/" + ENV_NAME, python_executable="/envs/tool/bin/python")
        self.assertEqual(command, ["/envs/tool/bin/python", "-m", "pytest"])

    def test_inactive_environment_dispatches_via_conda_run(self):
        command = command_for(["tools/ae_preflight.py"], env={}, prefix="/usr", conda_executable="/bin/conda")
        self.assertEqual(command, ["/bin/conda", "run", "--no-capture-output", "--name", ENV_NAME,
                                   "python", "tools/ae_preflight.py"])

    def test_missing_conda_uses_python_fallback_unless_forbidden(self):
        self.assertEqual(command_for(["-m", "pytest"], env={}, prefix="/usr", python_executable="/usr/bin/python"),
                         ["/usr/bin/python", "-m", "pytest"])
        with self.assertRaisesRegex(FileNotFoundError, "environment.yml"):
            command_for(["-m", "pytest"], env={}, prefix="/usr", conda_executable=None, require_conda=True)

    def test_environment_detection_requires_the_named_environment(self):
        self.assertTrue(active_environment({"CONDA_DEFAULT_ENV": ENV_NAME}, "/tmp/conda"))
        self.assertFalse(active_environment({"CONDA_DEFAULT_ENV": "base"}, "/tmp/base"))

    def test_module_flags_are_passed_to_python_without_argparse_interference(self):
        self.assertEqual(parse_run_args(["-m", "tools.uesp", "doctor"]),
                         (False, ["-m", "tools.uesp", "doctor"]))
        self.assertEqual(parse_run_args(["--require-conda", "--", "-m", "pytest", "-q"]),
                         (True, ["-m", "pytest", "-q"]))


if __name__ == "__main__":
    unittest.main()
