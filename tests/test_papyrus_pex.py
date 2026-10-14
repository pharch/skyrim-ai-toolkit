from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path

from tools.papyrus_pex import (
    MAGIC,
    PexFormatError,
    _safe_local_output,
    extract_pex_from_bsa,
    parse_pex,
    scan_literal_actor_values,
)


def _raw_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack(">H", len(encoded)) + encoded


def _minimal_pex(source: str = "Fixture.psc") -> bytes:
    return b"".join((
        struct.pack(">I", 0xFA57C0DE), bytes((3, 2)), struct.pack(">H", 1),
        struct.pack(">Q", 0), _raw_string(source), _raw_string("private-user"),
        _raw_string("private-machine"), struct.pack(">H", 0), bytes((0,)),
        struct.pack(">H", 0), struct.pack(">H", 0),
    ))


class PapyrusPexTests(unittest.TestCase):
    def test_minimal_pex_parses_and_redacted_metadata_is_not_emitted(self) -> None:
        result = parse_pex(_minimal_pex())
        self.assertEqual(result["source"], "Fixture.psc")
        self.assertEqual((result["major"], result["minor"]), (3, 2))
        self.assertEqual(result["trailing_bytes"], 0)
        self.assertNotIn("private-user", str(result))
        self.assertNotIn("private-machine", str(result))

    def test_truncated_input_fails_closed(self) -> None:
        with self.assertRaises(PexFormatError):
            parse_pex(MAGIC)

    def test_misc_bsa_extracts_only_matching_supported_pex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "Skyrim - Misc.bsa"
            pex = _minimal_pex("Fixture.psc")
            archive.write_bytes(b"BSA\x00fixture" + pex + MAGIC)
            payload, metadata = extract_pex_from_bsa(archive, "Fixture.psc")
        self.assertEqual(payload, pex)
        self.assertEqual(metadata["source"], "Fixture.psc")
        self.assertEqual(metadata["trailing_bytes"], 0)

    def test_archive_extraction_rejects_non_pex_source_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "Skyrim - Misc.bsa"
            archive.write_bytes(b"BSA\x00" + MAGIC + b"bad Source.psc" + MAGIC)
            with self.assertRaises(FileNotFoundError):
                extract_pex_from_bsa(archive, "Source")

    def test_literal_scan_defaults_to_base_archive_and_opt_in_adds_cc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data / "Skyrim - Misc.bsa").write_bytes(b"AlterationPowerModifier")
            (data / "cc-test.bsa").write_bytes(b"MarksmanPowerModifier")
            default = scan_literal_actor_values(data)
            broad = scan_literal_actor_values(data, include_creations=True)
        self.assertEqual(default["archive_count"], 1)
        self.assertEqual(default["hit_count"], 1)
        self.assertEqual(broad["archive_count"], 2)
        self.assertEqual(broad["hit_count"], 2)

    def test_output_must_stay_under_ignored_local_storage(self) -> None:
        with self.assertRaises(ValueError):
            _safe_local_output("/tmp/research-output.pex", "fixture.pex")


if __name__ == "__main__":
    unittest.main()
