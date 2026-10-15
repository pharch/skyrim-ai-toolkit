from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import lz4.block
except ImportError:
    lz4 = None

from scripts import python_env


def synthetic_save_bytes() -> bytes:
    """Build a parser fixture, not a game save or behavioral evidence."""
    decompressed = bytearray(b"\x00" * 5)
    plugin = b"Skyrim.esm"
    decompressed.append(1)
    decompressed.extend(struct.pack("<H", len(plugin)))
    decompressed.extend(plugin)
    decompressed.extend(struct.pack("<H", 0))
    decompressed.extend(b"\x00" * (1_000_100 - len(decompressed)))
    compressed = lz4.block.compress(bytes(decompressed), store_size=False)
    header = (
        b"TESV_SAVEGAM\x00"
        + struct.pack("<IIIH", 0, 0, 1, 0)
    )
    return header + struct.pack("<II", len(decompressed), len(compressed)) + compressed


class SaveReaderTests(unittest.TestCase):
    @unittest.skipIf(lz4 is None, "requires pinned lz4 runtime dependency")
    def test_help_starts_with_required_lz4_dependency(self):
        result = subprocess.run(
            [sys.executable, "scripts/python_env.py", "run", "scripts/read-save.py", "--help"],
            cwd=python_env.ROOT, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skyrim Save File Reader", result.stdout)

    @unittest.skipIf(lz4 is None, "requires pinned lz4 runtime dependency")
    def test_synthetic_fixture_info_path_decompresses_and_reads_plugin_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "synthetic-fixture.ess"
            fixture.write_bytes(synthetic_save_bytes())
            result = subprocess.run(
                [sys.executable, "scripts/python_env.py", "run", "scripts/read-save.py", "info", str(fixture)],
                cwd=python_env.ROOT, capture_output=True, text=True, timeout=60,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual(info["format"], "SSE/VR")
        self.assertEqual(info["decompressedSize"], 1_000_100)
        self.assertEqual(info["regularPlugins"], 1)
        self.assertEqual(info["totalPlugins"], 1)


if __name__ == "__main__":
    unittest.main()
