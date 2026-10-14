import struct
import tempfile
import unittest
from pathlib import Path

from tools.plugin_reader import PluginFormatError, read_plugin


def subrecord(signature: bytes, payload: bytes) -> bytes:
    return signature + struct.pack("<H", len(payload)) + payload


def record(signature: bytes, form_id: int, payload: bytes, flags: int = 0) -> bytes:
    return signature + struct.pack("<II", len(payload), flags) + struct.pack("<I", form_id) + bytes(8) + payload


def plugin_bytes() -> bytes:
    header_payload = subrecord(b"MAST", b"Skyrim.esm\0") + subrecord(b"DATA", bytes(8))
    weapon_payload = subrecord(b"EDID", b"TestWeapon\0") + subrecord(b"FULL", b"Test Weapon\0")
    return record(b"TES4", 0, header_payload) + record(b"WEAP", 0x01001234, weapon_payload)


class PluginReaderTests(unittest.TestCase):
    def test_reads_record_identity_and_subrecord_signatures(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Fixture.esp"
            path.write_bytes(plugin_bytes())
            rows = list(read_plugin(path, "WEAP"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["editor_id"], "TestWeapon")
        self.assertEqual(rows[0]["origin_plugin"], "Fixture.esp")
        self.assertEqual(rows[0]["local_form_id"], "001234")
        self.assertEqual(rows[0]["subrecord_signatures"], ["EDID", "FULL"])

    def test_rejects_truncated_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Bad.esp"
            path.write_bytes(b"WEAP" + struct.pack("<I", 100) + bytes(20))
            with self.assertRaises(PluginFormatError):
                list(read_plugin(path))

    def test_compressed_record_is_read_without_modifying_input(self):
        import zlib
        payload = subrecord(b"EDID", b"Compressed\0")
        compressed = struct.pack("<I", len(payload)) + zlib.compress(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Compressed.esp"
            path.write_bytes(record(b"WEAP", 0x00001234, compressed, flags=0x00040000))
            before = path.read_bytes()
            rows = list(read_plugin(path, "WEAP"))
            self.assertEqual(path.read_bytes(), before)
        self.assertEqual(rows[0]["editor_id"], "Compressed")


if __name__ == "__main__":
    unittest.main()
