import base64
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.ae_target import (
    REQUIRED_AE_MASTERS,
    TargetError,
    assert_ae_target,
    parse_active_plugins,
    parse_version,
    read_executable_version,
    resolve_plugins_txt,
)


class AETargetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.game = self.root / "game"
        self.game.mkdir()
        self.exe = self.game / "SkyrimSE.exe"
        self.exe.write_bytes(b"test executable")

    def tearDown(self):
        self.temp.cleanup()

    def test_version_parser_reads_three_component_runtime(self):
        self.assertEqual(parse_version("1.6.1170.0"), (1, 6, 1170))
        with self.assertRaisesRegex(TargetError, "cannot parse"):
            parse_version("Anniversary Edition")

    def test_ae_target_uses_injected_product_version_reader(self):
        target = assert_ae_target(
            {"SKYRIM_EDITION": "AE", "GAME_ROOT": str(self.game)},
            root=self.root,
            version_reader=lambda path: "1.6.1170.0",
        )
        self.assertEqual(target["version"], "1.6.1170")
        self.assertEqual(Path(target["executable"]), self.exe)

    def test_target_rejects_missing_scope_wrong_executable_and_old_runtime(self):
        with self.assertRaisesRegex(TargetError, "SKYRIM_EDITION"):
            assert_ae_target({"GAME_ROOT": str(self.game)}, root=self.root, version_reader=lambda _: "1.6.1170.0")
        with self.assertRaisesRegex(TargetError, "SkyrimSE.exe"):
            assert_ae_target(
                {"SKYRIM_EDITION": "AE", "GAME_ROOT": str(self.game), "SKYRIM_EXE_PATH": str(self.game / "SkyrimVR.exe")},
                root=self.root,
                version_reader=lambda _: "1.6.1170.0",
            )
        with self.assertRaisesRegex(TargetError, "1.6.318"):
            assert_ae_target({"SKYRIM_EDITION": "AE", "GAME_ROOT": str(self.game)}, root=self.root, version_reader=lambda _: "1.5.97.0")

    def test_active_order_requires_the_complete_ae_master_set(self):
        text = "\n".join("*" + name for name in REQUIRED_AE_MASTERS)
        self.assertEqual(parse_active_plugins(text), list(REQUIRED_AE_MASTERS))
        with self.assertRaisesRegex(TargetError, "missing required AE masters"):
            parse_active_plugins("*Skyrim.esm\n*Update.esm")

    def test_active_order_rejects_duplicate_and_wrong_base(self):
        with self.assertRaisesRegex(TargetError, "duplicate"):
            parse_active_plugins("*Skyrim.esm\n*" + "\n*".join(REQUIRED_AE_MASTERS))
        with self.assertRaisesRegex(TargetError, "begin with Skyrim.esm"):
            parse_active_plugins("*Update.esm\n*" + "\n*".join(REQUIRED_AE_MASTERS))

    def test_plugins_path_must_be_explicit_absolute_active_list(self):
        with self.assertRaisesRegex(TargetError, "set PLUGINS_TXT"):
            resolve_plugins_txt({}, root=self.root)
        plugins = self.root / "plugins.txt"
        plugins.write_text("*Skyrim.esm\n", encoding="utf-8")
        self.assertEqual(resolve_plugins_txt({"PLUGINS_TXT": str(plugins)}, root=self.root), plugins)

    @unittest.skipIf(os.name == "nt", "exercises the WSL PowerShell bridge")
    def test_wsl_version_reader_uses_ascii_transport_for_non_ascii_output(self):
        payload = base64.b64encode("1.6.1170.0®".encode("utf-8"))
        completed = SimpleNamespace(returncode=0, stdout=payload, stderr=b"diagnostic \xae")
        with patch("tools.ae_target.shutil.which", return_value="powershell.exe"), patch(
            "tools.ae_target.subprocess.run", return_value=completed
        ) as run:
            value = read_executable_version(Path("/mnt/c/game/SkyrimSE.exe"))
        self.assertEqual(value, "1.6.1170.0®")
        self.assertFalse(run.call_args.kwargs["text"])
        argv = run.call_args.args[0]
        self.assertEqual(argv[-2], "-EncodedCommand")
        script = base64.b64decode(argv[-1]).decode("utf-16le")
        self.assertIn(base64.b64encode(b"C:\\game\\SkyrimSE.exe").decode("ascii"), script)
        self.assertIn("ToBase64String", script)

    @unittest.skipIf(os.name == "nt", "exercises the WSL PowerShell bridge")
    def test_wsl_version_reader_finds_inbox_powershell_without_windows_path(self):
        payload = base64.b64encode(b"1.6.1170.0")
        completed = SimpleNamespace(returncode=0, stdout=payload, stderr=b"")
        with patch("tools.ae_target.shutil.which", return_value=None), patch(
            "tools.ae_target.Path.is_file", return_value=True
        ), patch("tools.ae_target.subprocess.run", return_value=completed) as run:
            value = read_executable_version(Path("/mnt/c/game/SkyrimSE.exe"))
        self.assertEqual(value, "1.6.1170.0")
        self.assertIn("WindowsPowerShell/v1.0/powershell.exe", run.call_args.args[0][0])


if __name__ == "__main__":
    unittest.main()
