from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import subprocess

from tools.xedit_bridge import (
    BridgeError,
    OFFICIAL_PLUGINS,
    QUERY_TEMPLATE,
    SOURCE_FILES,
    ensure_official_data_overlay,
    _parse_ui_status,
    helper_config,
    invoke_helper,
    materialize,
    render_native_query_script,
    validate_native_receipt,
    validate_official_plugin_list,
)


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

    def test_global_xedit_scripts_directory_is_optional(self):
        values = helper_config({
            "SSEEDIT_EXE": "C:/tools/SSEEdit.exe",
            "SKYRIM_DATA": "C:/Games/Skyrim/Data",
            "SKYRIM_EXE_PATH": "C:/Games/Skyrim/SkyrimSE.exe",
        })
        self.assertEqual(values["XEDIT_SCRIPTS"], "")

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

    def test_native_query_template_reuses_read_only_walker_and_renders_target(self):
        template = (Path(__file__).resolve().parents[1] / QUERY_TEMPLATE).read_text(encoding="utf-8")
        script = render_native_query_script(
            template,
            output_path=r"C:\research\native-records.tsv",
            loaded_files_path=r"C:\research\native-loaded-files.txt",
            status_path=r"C:\research\native-query-status.txt",
            plugin="Skyrim.esm",
            signature="QUST",
            editor_id="DA14",
        )
        self.assertIn("Hotkey: Ctrl+Alt+F9", script)
        self.assertIn("GetEditValue(e)", script)
        self.assertIn("WinningOverride(r)", script)
        self.assertIn("'C:\\research\\native-records.tsv'", script)
        self.assertIn("'C:\\research\\native-loaded-files.txt'", script)
        self.assertIn("'C:\\research\\native-query-status.txt'", script)
        self.assertIn("'Skyrim.esm'", script)
        self.assertIn("'QUST'", script)
        self.assertIn("'DA14'", script)
        self.assertNotRegex(script, r"__[A-Z_]+__")
        self.assertNotIn("function Process", script)
        self.assertIn("rows.SaveToFile('C:\\research\\native-records.tsv')", script)
        self.assertNotIn("function Finalize", script)

    def test_native_query_rejects_partial_or_reordered_official_lists(self):
        content = "".join("*" + item + "\n" for item in OFFICIAL_PLUGINS)
        self.assertEqual(validate_official_plugin_list(content), OFFICIAL_PLUGINS)
        with self.assertRaisesRegex(BridgeError, "exactly the five official masters"):
            validate_official_plugin_list("*Skyrim.esm\n*Update.esm\n")
        with self.assertRaisesRegex(BridgeError, "exactly the five official masters"):
            validate_official_plugin_list("".join("*" + item + "\n" for item in reversed(OFFICIAL_PLUGINS)))

    def test_official_data_overlay_copies_only_vanilla_masters_and_matching_strings(self):
        import stat
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "toolkit"
            source_data = Path(tmp) / "game" / "Data"
            root.mkdir(); source_data.mkdir(parents=True)
            for plugin in OFFICIAL_PLUGINS:
                (source_data / plugin).write_bytes(plugin.encode("ascii"))
            (source_data / "ccBGSSSE001-Fish.esm").write_bytes(b"cc")
            (source_data / "Skyrim.ccc").write_text("ccBGSSSE001-Fish.esm\n", encoding="ascii")
            strings = source_data / "Strings"
            strings.mkdir()
            (strings / "Skyrim_English.STRINGS").write_bytes(b"vanilla strings")
            (strings / "ccBGSSSE001-Fish_English.STRINGS").write_bytes(b"cc strings")

            overlay, manifest = ensure_official_data_overlay(root, source_data)
            self.assertTrue(all((overlay / plugin).read_bytes() == (source_data / plugin).read_bytes() for plugin in OFFICIAL_PLUGINS))
            self.assertTrue((overlay / "Strings/Skyrim_English.STRINGS").read_bytes() == (strings / "Skyrim_English.STRINGS").read_bytes())
            self.assertFalse((overlay / "Skyrim.esm").samefile(source_data / "Skyrim.esm"))
            self.assertFalse((overlay / "Skyrim.esm").stat().st_mode & stat.S_IWUSR)
            self.assertFalse((overlay / "ccBGSSSE001-Fish.esm").exists())
            self.assertFalse((overlay / "Skyrim.ccc").exists())
            self.assertEqual(len(manifest["source_files"]), len(OFFICIAL_PLUGINS) + 1)
            ensure_official_data_overlay(root, source_data)

    def test_native_xedit_smoke_fixture_preserves_loaded_scope_and_stage_fields(self):
        import json

        fixture_path = Path(__file__).resolve().parent / "fixtures/xedit/native_quest_smoke.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        loaded_plugins = tuple(
            item for item in fixture["loaded_files"] if item.casefold() != "skyrimse.exe"
        )
        self.assertEqual(loaded_plugins, OFFICIAL_PLUGINS)
        self.assertEqual(fixture["record"]["signature"], "QUST")
        self.assertEqual(fixture["record"]["form_id"], "000427A0")
        fields = {item["field_path"]: item["value"] for item in fixture["representative_stage_fields"]}
        self.assertEqual(
            fields[r"QUST\6:Stages\2:Stage\0:INDX - Stage Index\0:Stage Index"],
            "20",
        )
        self.assertEqual(
            fields[r"QUST\6:Stages\4:Stage\0:INDX - Stage Index\1:Flags\0:Shut Down Stage"],
            "1",
        )

    def test_native_status_parser_treats_blank_startup_output_as_not_ready(self):
        status, names = _parse_ui_status(b"")
        self.assertEqual(status, {"windows": []})
        self.assertEqual(names, [])
        status, names = _parse_ui_status(
            b'{"ProcessId": 12, "Window": "SSEView 4.1.5f", "Controls": [{"Name": "Background Loader: finished"}]}'
        )
        self.assertEqual(names, ["SSEView 4.1.5f", "Background Loader: finished"])

    def test_native_status_parser_reads_concatenated_window_json(self):
        raw = (
            b'{"ProcessId": 12, "Window": "", "Controls": []}\r\n'
            b'{"ProcessId": 12, "Window": "SSEView 4.1.5f", "Controls": '
            b'[{"Name": "Background Loader: finished"}]}\r\n'
        )
        status, names = _parse_ui_status(raw)
        self.assertEqual(len(status["windows"]), 2)
        self.assertEqual(names, ["SSEView 4.1.5f", "Background Loader: finished"])

    def test_native_status_parser_sanitizes_raw_control_chars_in_ui_names(self):
        raw = b'{"ProcessId": 12, "Window": "SSEView", "Controls": [{"Name": "bad\x07name"}]}'
        _, names = _parse_ui_status(raw)
        self.assertEqual(names, ["SSEView", "bad name"])

    def test_native_receipt_requires_matching_structured_and_tsv_hashes(self):
        import hashlib
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tsv = root / ".local/xedit-native/result.tsv"
            result = root / ".local/xedit-native/result.json"
            receipt_path = root / ".local/xedit-native/latest.json"
            tsv.parent.mkdir(parents=True)
            tsv.write_text("native record", encoding="utf-8")
            result.write_text("{}", encoding="utf-8")
            receipt_path.write_text(json.dumps({
                "status": "PASS",
                "record": {"editor_id": "DA14"},
                "plugins": list(OFFICIAL_PLUGINS),
                "loaded_files": ["Skyrim.esm", "SkyrimSE.exe", *OFFICIAL_PLUGINS[1:]],
                "tsv": ".local/xedit-native/result.tsv",
                "tsv_sha256": hashlib.sha256(tsv.read_bytes()).hexdigest(),
                "result_json": ".local/xedit-native/result.json",
                "result_json_sha256": hashlib.sha256(result.read_bytes()).hexdigest(),
                "completed_utc": "2026-10-15T00:00:00Z",
            }), encoding="utf-8")
            self.assertEqual(validate_native_receipt(root)["status"], "PASS")
            tsv.write_text("changed", encoding="utf-8")
            self.assertEqual(validate_native_receipt(root)["status"], "STALE_OR_INVALID")


if __name__ == "__main__":
    unittest.main()
