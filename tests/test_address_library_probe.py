from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.address_library_probe import AddressLibraryProbeError, commonlib_ae_id, probe


class AddressLibraryProbeTests(unittest.TestCase):
    def _fixture(self, *, decoder_version: str = "1.6.1179.0"):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "toolkit"
        root.mkdir()
        legacy = Path(temporary.name) / "legacy"
        (legacy / "scripts").mkdir(parents=True)
        (legacy / "scripts" / "address_library_lookup.py").write_text(
            "def decode(path):\n"
            f"    return tuple(map(int, {decoder_version!r}.split('.'))), {{11321: 0x14C020}}\n",
            encoding="utf-8",
        )
        (legacy / "out" / "ghidra").mkdir(parents=True)
        (legacy / "out" / "ghidra" / "symbols_ae_relevant.json").write_text(
            '{"target":"ae","symbols":[{"n":"MagicItem::CalculateCost","id":11321,"rva":1360368}]}',
            encoding="utf-8",
        )
        commonlib = Path(temporary.name) / "CommonLibSSE-NG"
        (commonlib / "include" / "RE").mkdir(parents=True)
        (commonlib / "include" / "RE" / "Offsets.h").write_text(
            "namespace MagicItem {\n"
            "    constexpr auto CalculateCost = RELOCATION_ID(11213, 11321);\n"
            "}\n",
            encoding="utf-8",
        )
        exe = Path(temporary.name) / "GOG" / "SkyrimSE.exe"
        exe.parent.mkdir()
        exe.write_bytes(b"fixture executable")
        library = exe.parent / "Data" / "SKSE" / "Plugins" / "versionlib-1-6-1179-0.bin"
        library.parent.mkdir(parents=True)
        library.write_bytes(b"fixture address library")
        config = {
            "LEGACY_SKYRIM_REPO": str(legacy),
            "COMMONLIBSSE_ROOT": str(commonlib),
            "GHIDRA_ANALYSIS_EXE_GOG": str(exe),
        }
        return temporary, root, config

    def test_named_commonlib_ae_relocation_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            header = Path(tmp) / "Offsets.h"
            header.write_text(
                "namespace MagicItem {\nconstexpr auto CalculateCost = RELOCATION_ID(11213, 11321);\n}\n",
                encoding="utf-8",
            )
            self.assertEqual(commonlib_ae_id(header, "MagicItem::CalculateCost"), 11321)
            with self.assertRaises(AddressLibraryProbeError):
                commonlib_ae_id(header, "MagicItem::Missing")

    def test_probe_uses_build_matched_library_and_rejects_unproven_legacy_map(self):
        temporary, root, config = self._fixture()
        self.addCleanup(temporary.cleanup)
        with patch("tools.address_library_probe.read_executable_version", return_value="1.6.1179.0"):
            result = probe(root=root, config=config, symbol="MagicItem::CalculateCost")
        self.assertTrue(result["ok"])
        self.assertEqual(result["commonlib_ae_id"], 11321)
        self.assertEqual(result["address_library_rva"], "0x14C020")
        self.assertEqual(result["analysis_distribution"], "GOG")
        self.assertFalse(result["legacy_map"]["runtime_provenance_present"])
        self.assertFalse(result["legacy_map"]["accepted_as_current_build_evidence"])

    def test_library_version_must_match_verified_executable(self):
        temporary, root, config = self._fixture(decoder_version="1.6.1170.0")
        self.addCleanup(temporary.cleanup)
        with patch("tools.address_library_probe.read_executable_version", return_value="1.6.1179.0"):
            with self.assertRaisesRegex(AddressLibraryProbeError, "internal version does not match"):
                probe(root=root, config=config, symbol="MagicItem::CalculateCost")

    def test_missing_gog_binding_fails_closed(self):
        with self.assertRaisesRegex(AddressLibraryProbeError, "missing local bindings"):
            probe(root=Path("/tmp"), config={}, symbol="MagicItem::CalculateCost")


if __name__ == "__main__":
    unittest.main()
