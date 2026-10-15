"""Resolve optional Skyrim AE log folders from config/local.env only."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config  # noqa: E402
from tools.ae_target import _native_path  # noqa: E402

GAME_FOLDERS = ("Skyrim Special Edition",)


def my_games(config: dict[str, str] | None = None) -> Path:
    """Return the configured Skyrim AE settings root; never guess a profile."""
    values = read_local_config(ROOT) if config is None else config
    configured = values.get("SKYRIM_CONFIG_DIR", "").strip()
    if not configured:
        raise ValueError("set SKYRIM_CONFIG_DIR in config/local.env for default log discovery")
    profile = _native_path(configured).expanduser()
    if profile.name.casefold() != "skyrim special edition":
        raise ValueError("SKYRIM_CONFIG_DIR must point to the Skyrim Special Edition (AE) settings folder")
    return profile.parent


def find_game_dir(subpath: str, base: Path | None = None, *, config: dict[str, str] | None = None):
    """Return only the configured AE folder and no cross-edition candidates."""
    root = Path(base) if base is not None else my_games(config)
    return root / "Skyrim Special Edition" / subpath, []


def resolve_dir(
    env_var: str,
    subpath: str,
    base: Path | None = None,
    *,
    config: dict[str, str] | None = None,
):
    """Use an explicit config key or the single configured AE user-data folder."""
    values = read_local_config(ROOT) if config is None else config
    override = values.get(env_var, "").strip()
    if override:
        path = _native_path(override).expanduser()
        if not path.is_absolute():
            path = ROOT / path
        return path, []
    return find_game_dir(subpath, base=base, config=values)
