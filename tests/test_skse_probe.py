from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.skse_probe import inspect_install


class SkseProbeTests(unittest.TestCase):
    def test_matching_runtime_files_are_hashed_and_versioned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            data = root / "data"
            plugins = data / "SKSE" / "Plugins"
            game.mkdir(); plugins.mkdir(parents=True)
            (game / "skse64_loader.exe").write_bytes(b"loader")
            (game / "skse64_1_6_1170.dll").write_bytes(b"runtime")
            (plugins / "versionlib-1-6-1170-0.bin").write_bytes(b"address")
            result = inspect_install(
                game, data, "1.6.1170", version_reader=lambda _: "0.2.2.6"
            )
        self.assertEqual(result["status"], "matching_runtime_files_present")
        self.assertTrue(result["runtime_filename_match"])
        self.assertEqual(result["runtime_dll"]["product_version"], "0.2.2.6")
        self.assertTrue(result["metadata_only"])
        self.assertFalse(result["live_handshake_attempted"])

    def test_missing_address_library_is_not_reported_as_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"; data = root / "data"
            game.mkdir(); data.mkdir()
            (game / "skse64_loader.exe").write_bytes(b"loader")
            (game / "skse64_1_6_1170.dll").write_bytes(b"runtime")
            result = inspect_install(
                game, data, "1.6.1170", version_reader=lambda _: "0.2.2.6"
            )
        self.assertEqual(result["status"], "incomplete_or_unreadable")
        self.assertFalse(result["runtime_filename_match"])


if __name__ == "__main__":
    unittest.main()
