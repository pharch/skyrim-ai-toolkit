"""Resolve Skyrim AE user-data paths without searching other editions."""

from __future__ import annotations

import os
from pathlib import Path

GAME_FOLDERS = ("Skyrim Special Edition",)


def my_games() -> Path:
    """Return the per-user Bethesda settings root."""
    configured = os.environ.get("SKYRIM_CONFIG_DIR")
    if configured:
        profile = Path(configured).expanduser()
        if profile.name.casefold() != "skyrim special edition":
            raise ValueError("SKYRIM_CONFIG_DIR must point to the Skyrim Special Edition (AE) settings folder")
        return profile.parent
    profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return Path(profile) / "Documents" / "My Games"


def find_game_dir(subpath: str, base: Path | None = None):
    """Return the sole AE candidate and an empty rival list."""
    root = Path(base) if base is not None else my_games()
    return root / "Skyrim Special Edition" / subpath, []


def resolve_dir(env_var: str, subpath: str, base: Path | None = None):
    """Use an explicit tool-specific override or the single AE user-data path."""
    override = os.environ.get(env_var)
    if override:
        return Path(override), []
    return find_game_dir(subpath, base=base)
