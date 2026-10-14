import struct
import tempfile
import unittest
from pathlib import Path

from tools.ae_target import REQUIRED_AE_MASTERS
from tools.plugin_reader import PluginFormatError, read_plugin, resolve_record_winner


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

    def test_raw_subrecord_mode_preserves_conditions_aliases_and_script_bytes(self):
        payload = (
            subrecord(b"EDID", b"QuestFixture\0")
            + subrecord(b"CTDA", bytes(range(32)))
            + subrecord(b"ALST", b"\x01\x02\x03\x04")
            + subrecord(b"ALID", b"AliasName\0")
            + subrecord(b"VMAD", b"ScriptFixture\0\x00\x00")
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "QuestFixture.esp"
            path.write_bytes(record(b"QUST", 0x00001234, payload))
            row = next(read_plugin(path, "QUST", include_subrecords=True))
        fields = row["subrecords"]
        by_signature = {field["signature"]: field for field in fields}
        self.assertEqual(by_signature["CTDA"]["length"], 32)
        self.assertEqual(by_signature["CTDA"]["value_hex"], bytes(range(32)).hex())
        self.assertEqual(by_signature["ALST"]["value_hex"], "01020304")
        self.assertEqual(by_signature["ALID"]["text_cp1252"], "AliasName")
        self.assertTrue(by_signature["VMAD"]["value_hex"].startswith(b"ScriptFixture".hex()))

    def test_two_record_override_fixture_selects_last_active_plugin(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "Skyrim.esm"
            update = Path(directory) / "Update.esm"
            base_header = subrecord(b"HEDR", bytes(12))
            update_header = subrecord(b"HEDR", bytes(12)) + subrecord(b"MAST", b"Skyrim.esm\0") + subrecord(b"DATA", bytes(8))
            base_record = subrecord(b"EDID", b"FixtureBase\0") + subrecord(b"FULL", b"Base\0")
            override_record = subrecord(b"EDID", b"FixtureOverride\0") + subrecord(b"FULL", b"Override\0")
            base.write_bytes(record(b"TES4", 0, base_header) + record(b"WEAP", 0x00001234, base_record))
            update.write_bytes(record(b"TES4", 0, update_header) + record(b"WEAP", 0x00001234, override_record))
            candidates = [*read_plugin(base, "WEAP"), *read_plugin(update, "WEAP")]
            winner = resolve_record_winner(candidates, list(REQUIRED_AE_MASTERS))
        self.assertEqual(winner["plugin"], "Update.esm")
        self.assertEqual(winner["editor_id"], "FixtureOverride")
        self.assertEqual(winner["origin_plugin"], "Skyrim.esm")

    def test_winner_fixture_rejects_incomplete_order(self):
        candidate = {
            "signature": "QUST", "plugin": "Skyrim.esm", "origin_plugin": "Skyrim.esm",
            "local_form_id": "000001",
        }
        with self.assertRaisesRegex(PluginFormatError, "complete AE plugin list"):
            resolve_record_winner([candidate], ["Skyrim.esm", "Update.esm"])


if __name__ == "__main__":
    unittest.main()
