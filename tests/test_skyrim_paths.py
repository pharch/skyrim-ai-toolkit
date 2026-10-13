from __future__ import annotations

import sys
from pathlib import Path

from conftest import REPO

sys.path.insert(0, str(REPO / "tools"))
import skyrim_paths  # noqa: E402


def test_discovery_targets_only_the_ae_profile_path(tmp_path):
    root = tmp_path / "My Games"
    (root / "Skyrim VR" / "SKSE").mkdir(parents=True)
    (root / "Skyrim" / "SKSE").mkdir(parents=True)
    ae = root / "Skyrim Special Edition" / "SKSE"
    ae.mkdir(parents=True)

    chosen, others = skyrim_paths.find_game_dir("SKSE", base=root)

    assert chosen == ae
    assert others == []


def test_missing_ae_profile_does_not_fall_back_to_another_edition(tmp_path):
    root = tmp_path / "My Games"
    (root / "Skyrim VR" / "SKSE").mkdir(parents=True)

    chosen, others = skyrim_paths.find_game_dir("SKSE", base=root)

    assert chosen == root / "Skyrim Special Edition" / "SKSE"
    assert not chosen.exists()
    assert others == []


def test_explicit_tool_path_override_is_preserved(tmp_path, monkeypatch):
    override = tmp_path / "explicit" / "Papyrus"
    monkeypatch.setenv("PAPYRUS_LOG_DIR", str(override))

    chosen, others = skyrim_paths.resolve_dir("PAPYRUS_LOG_DIR", "Logs/Script")

    assert chosen == override
    assert others == []


def test_ambiguous_game_folders_never_change_the_ae_target(tmp_path):
    root = tmp_path / "My Games"
    for edition in ("Skyrim", "Skyrim VR", "Skyrim Special Edition"):
        (root / edition / "Logs" / "Script").mkdir(parents=True)

    chosen, others = skyrim_paths.find_game_dir("Logs/Script", base=root)

    assert chosen == root / "Skyrim Special Edition" / "Logs" / "Script"
    assert others == []
