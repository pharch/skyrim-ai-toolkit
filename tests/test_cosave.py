"""Co-save parser exit contract: 0 parsed / 1 degraded / 2 not-a-cosave.

Every parser path is exercised by stdlib unittest so the same checks run in
the repository's CI job without depending on pytest discovery.
"""
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COSAVE = ROOT / "tools" / "cosave-info.py"


def run(*args):
    return subprocess.run([sys.executable, str(COSAVE), *args],
                          capture_output=True, text=True)


def _valid_cosave() -> bytes:
    """A structural fixture with a 32-byte header and one well-formed chunk."""
    header = b"SKSE" + struct.pack("<IIIIIII", 1, 0x02000600, 0x01040F00, 0, 0, 0, 0)
    payload = bytes(200)
    return header + b"ATAD" + struct.pack("<II", 1, len(payload)) + payload


class CosaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_a_structurally_valid_fixture(self):
        path = self.root / "ok.skse"
        path.write_bytes(_valid_cosave())
        result = run(str(path))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('"chunkCount": 1', result.stdout)
        self.assertIn('"coveragePct": 100.0', result.stdout)

    def test_degrades_on_a_stub_that_parses_no_chunks(self):
        path = self.root / "stub.skse"
        path.write_bytes(b"SKSE" + bytes(64))
        result = run(str(path))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('"chunkCount": 0', result.stdout)

    def test_refuses_a_file_that_is_not_a_cosave(self):
        path = self.root / "notacosave.txt"
        path.write_text("this is plainly not an SKSE co-save", encoding="utf-8")
        result = run(str(path))
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('"ok": false', result.stdout.lower())

    def test_refuses_a_file_too_short_to_unpack(self):
        path = self.root / "tiny.skse"
        path.write_bytes(b"SKSE")
        result = run(str(path))
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_refuses_a_missing_file(self):
        result = run(str(self.root / "missing.skse"))
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_refuses_with_no_arguments(self):
        result = run()
        self.assertEqual(result.returncode, 2, result.stdout)


if __name__ == "__main__":
    unittest.main()
