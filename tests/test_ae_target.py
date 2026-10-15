import base64
import os
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.ae_target import (
    REQUIRED_AE_MASTERS,
    TargetError,
    _read_pe_product_version,
    assert_ae_target,
    parse_active_plugins,
    parse_version,
    preflight,
    read_executable_version,
    resolve_plugins_txt,
    resolve_test_plugins_txt,
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

    def test_pe_product_version_reader_extracts_named_version_string(self):
        def align4(data: bytearray) -> None:
            while len(data) % 4:
                data.append(0)

        def block(key: str, value: bytes, value_length: int, value_type: int, children=()) -> bytes:
            output = bytearray(6)
            output.extend(key.encode("utf-16le") + b"\0\0")
            align4(output)
            output.extend(value)
            align4(output)
            for child in children:
                output.extend(child)
                align4(output)
            struct.pack_into("<HHH", output, 0, len(output), value_length, value_type)
            return bytes(output)

        fixed_info = struct.pack(
            "<13I", 0xFEEF04BD, 0x10000, 0x00010006, 0x049B0000,
            0x00010006, 0x049B0000, 0, 0, 0x3F, 0, 0, 0, 0,
        )
        product = block("ProductVersion", "1.6.1179.0\0".encode("utf-16le"), 11, 1)
        table = block("040904B0", b"", 0, 1, (product,))
        strings = block("StringFileInfo", b"", 0, 1, (table,))
        version_resource = block("VS_VERSION_INFO", fixed_info, len(fixed_info), 0, (strings,))

        image = bytearray(0x600)
        image[:2] = b"MZ"
        struct.pack_into("<I", image, 0x3C, 0x80)
        image[0x80:0x84] = b"PE\0\0"
        coff = 0x84
        struct.pack_into("<HHIIIHH", image, coff, 0x8664, 1, 0, 0, 0, 240, 0x22)
        optional = coff + 20
        struct.pack_into("<H", image, optional, 0x20B)
        resource_dir = optional + 112 + 2 * 8
        struct.pack_into("<II", image, resource_dir, 0x1000, 0x200)
        section = optional + 240
        image[section:section + 8] = b".rsrc\0\0\0"
        struct.pack_into("<IIII", image, section + 8, 0x400, 0x1000, 0x400, 0x200)

        resource = 0x200
        struct.pack_into("<IIHHHH", image, resource, 0, 0, 0, 0, 0, 1)
        struct.pack_into("<II", image, resource + 16, 16, 0x80000018)
        struct.pack_into("<IIHHHH", image, resource + 24, 0, 0, 0, 0, 0, 1)
        struct.pack_into("<II", image, resource + 40, 1, 0x80000030)
        struct.pack_into("<IIHHHH", image, resource + 48, 0, 0, 0, 0, 0, 1)
        struct.pack_into("<II", image, resource + 64, 1033, 72)
        struct.pack_into("<IIII", image, resource + 72, 0x1100, len(version_resource), 0, 0)
        image[resource + 0x100:resource + 0x100 + len(version_resource)] = version_resource

        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "SkyrimSE.exe"
            executable.write_bytes(image)
            self.assertEqual(_read_pe_product_version(executable), "1.6.1179.0")

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
        profile = self.root / "profile"
        profile.mkdir()
        plugins = profile / "plugins.txt"
        plugins.write_text("*Skyrim.esm\n", encoding="utf-8")
        with self.assertRaisesRegex(TargetError, "MO2_PROFILE_DIR"):
            resolve_plugins_txt({"PLUGINS_TXT": str(plugins)}, root=self.root)
        self.assertEqual(resolve_plugins_txt({"PLUGINS_TXT": str(plugins), "MO2_PROFILE_DIR": str(profile)}, root=self.root), plugins)

    def test_process_environment_and_global_loadorder_fallbacks_are_not_used(self):
        with patch.dict(os.environ, {
            "PLUGINS_TXT": str(self.root / "global-plugins.txt"),
            "SKYRIM_LOADORDER_DIR": str(self.root),
            "LOCALAPPDATA": str(self.root),
        }):
            with self.assertRaisesRegex(TargetError, "set PLUGINS_TXT"):
                resolve_plugins_txt(root=self.root)

    def test_mo2_plugins_file_must_belong_to_selected_profile(self):
        selected = self.root / "profile"
        other = self.root / "other"
        selected.mkdir(); other.mkdir()
        wrong = other / "plugins.txt"
        wrong.write_text("*Skyrim.esm\n", encoding="utf-8")
        with self.assertRaisesRegex(TargetError, "MO2_PROFILE_DIR"):
            resolve_plugins_txt({"PLUGINS_TXT": str(wrong), "MO2_PROFILE_DIR": str(selected)}, root=self.root)

    def test_test_plugins_file_requires_designated_disposable_profile(self):
        profile = self.root / "test-profile"
        profile.mkdir()
        plugins = profile / "plugins.txt"
        plugins.write_text("*Skyrim.esm\n", encoding="utf-8")
        with self.assertRaisesRegex(TargetError, "SKYRIM_TEST_PROFILE_DIR"):
            resolve_test_plugins_txt({"SKYRIM_TEST_PLUGINS_TXT": str(plugins)}, root=self.root)
        self.assertEqual(resolve_test_plugins_txt({
            "SKYRIM_TEST_PROFILE_DIR": str(profile), "SKYRIM_TEST_PLUGINS_TXT": str(plugins),
        }, root=self.root), plugins)

    def test_test_profile_preflight_is_separate_from_selected_order(self):
        profile = self.root / "test-profile"
        profile.mkdir()
        plugins = profile / "plugins.txt"
        plugins.write_text("".join(f"*{name}\n" for name in REQUIRED_AE_MASTERS), encoding="utf-8")
        result = preflight(
            {
                "SKYRIM_EDITION": "AE", "GAME_ROOT": str(self.game),
                "SKYRIM_TEST_PROFILE_DIR": str(profile), "SKYRIM_TEST_PLUGINS_TXT": str(plugins),
            },
            root=self.root,
            version_reader=lambda _: "1.6.1170.0",
            test_profile=True,
        )
        self.assertEqual(result["scope"], "designated-disposable-profile")
        self.assertTrue(result["disposable_test_profile_verified"])
        self.assertFalse(result["selected_profile_verified"])
        self.assertTrue(result["full_order_verified"])

    def test_scoped_five_master_preflight_is_distinct_from_selected_order(self):
        plugins = self.root / "out" / "session" / "plugins.txt"
        plugins.parent.mkdir(parents=True)
        plugins.write_text("".join(f"*{name}\n" for name in REQUIRED_AE_MASTERS), encoding="utf-8")
        result = preflight(
            {"SKYRIM_EDITION": "AE", "GAME_ROOT": str(self.game)},
            root=self.root,
            version_reader=lambda _: "1.6.1170.0",
            scoped_five_master=plugins,
        )
        self.assertEqual(result["scope"], "scoped-five-master")
        self.assertEqual(result["active_plugins"], 5)
        self.assertFalse(result["full_order_verified"])
        self.assertFalse(result["selected_profile_verified"])

    def test_scoped_five_master_rejects_mods_and_noncanonical_order(self):
        plugins = self.root / "out" / "session" / "plugins.txt"
        plugins.parent.mkdir(parents=True)
        plugins.write_text("".join(f"*{name}\n" for name in REQUIRED_AE_MASTERS) + "*Example.esl\n", encoding="utf-8")
        with self.assertRaisesRegex(TargetError, "exactly the five official AE masters"):
            preflight(
                {"SKYRIM_EDITION": "AE", "GAME_ROOT": str(self.game)},
                root=self.root,
                version_reader=lambda _: "1.6.1170.0",
                scoped_five_master=plugins,
            )

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
