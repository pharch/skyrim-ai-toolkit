from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import research_safety as safety


@pytest.mark.parametrize("path", [
    r"C:\Games\Skyrim VR\Data\MyMod.esp",
    "/tmp/fixture.esm",
    "test.ess",
    "test.skse",
])
def test_check_write_rejects_binary_and_save_targets(path):
    assert safety.check_write(path, []) is not None


def test_check_write_rejects_configured_game_roots_case_insensitively():
    target = r"c:\games\skyrim vr\Data\Scripts\probe.pex"
    assert safety.check_write(target, [r"C:\Games\Skyrim VR"]) is not None


def test_check_write_rejects_game_shaped_paths_without_local_config():
    assert safety.check_write("Data/Scripts/Probe.psc", []) is not None
    assert safety.check_write("Documents/My Games/Skyrim VR/SkyrimVR.ini", []) is not None


def test_check_write_allows_research_workspace_text_files():
    assert safety.check_write("research/CLAIMS.md", []) is None


def test_snapshot_copies_exact_files_and_records_hashes(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    source = root / "research" / "notes.md"
    source.parent.mkdir(parents=True)
    source.write_text("raw evidence\n", encoding="utf-8")
    backup_root = root / ".research-backups"
    monkeypatch.setattr(safety, "ROOT", root)
    monkeypatch.setattr(safety, "BACKUP_ROOT", backup_root)

    assert safety.snapshot(["research/notes.md"]) == 0
    snapshots = list(backup_root.iterdir())
    assert len(snapshots) == 1
    manifest = json.loads((snapshots[0] / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["files"][0]["path"] == "research/notes.md"
    assert (snapshots[0] / "research/notes.md").read_text(encoding="utf-8") == "raw evidence\n"


def test_snapshot_rejects_path_escape_and_save_files(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.setattr(safety, "ROOT", root)
    monkeypatch.setattr(safety, "BACKUP_ROOT", root / ".research-backups")
    outside = tmp_path / "outside.md"
    outside.write_text("private\n", encoding="utf-8")
    with pytest.raises(ValueError):
        safety._safe_snapshot_source("../outside.md")
    (root / "save.ess").write_bytes(b"protected")
    with pytest.raises(ValueError):
        safety._safe_snapshot_source("save.ess")
