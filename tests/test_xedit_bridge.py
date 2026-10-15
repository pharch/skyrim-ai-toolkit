from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import subprocess

from tools.xedit_bridge import BridgeError, SOURCE_FILES, helper_config, invoke_helper, materialize


class XEditBridgeTests(unittest.TestCase):
    def test_root_config_is_mapped_to_legacy_helper_schema(self):
        values = helper_config({
            "SSEEDIT_EXE": "C:/tools/SSEEdit.exe",
            "SKYRIM_DATA": "C:/Games/Skyrim/Data",
            "XEDIT_SCRIPTS": "C:/tools/SSEEdit/Edit Scripts",
            "SKYRIM_EXE_PATH": "C:/Games/Skyrim/SkyrimSE.exe",
            "INCLUDE_CREATION_CLUB": "0",
        })
        self.assertEqual(values["SKYRIM_EXE"], "C:/Games/Skyrim/SkyrimSE.exe")
        self.assertEqual(values["INCLUDE_CREATION_CLUB"], "0")

    def test_conflicting_legacy_and_canonical_executable_bindings_fail(self):
        with self.assertRaisesRegex(BridgeError, "conflicts"):
            helper_config({
                "SSEEDIT_EXE": "xedit",
                "SKYRIM_DATA": "data",
                "XEDIT_SCRIPTS": "scripts",
                "SKYRIM_EXE_PATH": "C:/Skyrim/SkyrimSE.exe",
                "SKYRIM_EXE": "D:/Other/SkyrimSE.exe",
            })

    def test_materialize_copies_only_helper_files_and_derives_private_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "toolkit"
            source = Path(tmp) / "legacy"
            root.mkdir(); source.mkdir()
            for relative in SOURCE_FILES:
                file = source / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("fixture:" + relative, encoding="utf-8")
            private = source / "config" / "local.env"
            private.parent.mkdir()
            private.write_text("ORIGINAL_PRIVATE=keep\n", encoding="utf-8")
            config = {
                "LEGACY_SKYRIM_REPO": str(source),
                "SSEEDIT_EXE": "C:/tools/SSEEdit.exe",
                "SKYRIM_DATA": "C:/Games/Skyrim/Data",
                "XEDIT_SCRIPTS": "C:/tools/SSEEdit/Edit Scripts",
                "SKYRIM_EXE_PATH": "C:/Games/Skyrim/SkyrimSE.exe",
                "INCLUDE_CREATION_CLUB": "0",
            }
            bridge, hashes = materialize(root, config)
            self.assertEqual(len(hashes), len(SOURCE_FILES))
            self.assertTrue((bridge / "scripts/skyrim_tool.py").is_file())
            derived = (bridge / "config/local.env").read_text(encoding="utf-8")
            self.assertIn('SKYRIM_EXE="C:/Games/Skyrim/SkyrimSE.exe"', derived)
            self.assertNotIn("ORIGINAL_PRIVATE", derived)
            self.assertEqual(private.read_text(encoding="utf-8"), "ORIGINAL_PRIVATE=keep\n")

    def test_helper_timeout_is_reported_and_partial_output_is_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bridge = root / "bridge"
            with patch("tools.xedit_bridge.subprocess.run", side_effect=subprocess.TimeoutExpired(
                cmd=["python", "helper"], timeout=1, output=b"partial", stderr=b"timed out",
            )):
                with self.assertRaisesRegex(BridgeError, "timed out after 1 seconds"):
                    invoke_helper(bridge, ["doctor"], root=root, timeout=1)
            capture_dirs = list((root / ".local/alignment/xedit-bridge").iterdir())
            self.assertEqual(len(capture_dirs), 1)
            self.assertEqual((capture_dirs[0] / "stdout.raw").read_text(encoding="utf-8"), "partial")
            self.assertEqual((capture_dirs[0] / "stderr.raw").read_text(encoding="utf-8"), "timed out")


if __name__ == "__main__":
    unittest.main()
