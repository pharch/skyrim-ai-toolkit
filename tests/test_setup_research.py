from __future__ import annotations

from pathlib import Path

import pytest

from scripts import setup_research


def test_initialize_copies_private_config_once(tmp_path: Path):
    config = tmp_path / "config"
    config.mkdir()
    example = config / "local.env.example"
    example.write_text("SKYRIM_EDITION=AE\n", encoding="utf-8")

    assert setup_research.initialize(tmp_path) is True
    local = config / "local.env"
    assert local.read_text(encoding="utf-8") == "SKYRIM_EDITION=AE\n"
    assert setup_research.initialize(tmp_path) is False


def test_initialize_never_overwrites_existing_configuration(tmp_path: Path):
    config = tmp_path / "config"
    config.mkdir()
    (config / "local.env.example").write_text("template\n", encoding="utf-8")
    local = config / "local.env"
    local.write_text("private user settings\n", encoding="utf-8")

    assert setup_research.initialize(tmp_path) is False
    assert local.read_text(encoding="utf-8") == "private user settings\n"


def test_initialize_requires_template_and_does_not_create_fallback(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        setup_research.initialize(tmp_path)
    assert not (tmp_path / "config" / "local.env").exists()
