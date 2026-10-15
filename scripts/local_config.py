"""Read and validate the single ignored machine-local configuration file."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
_KEY = re.compile(r"[A-Z][A-Z0-9_]*\Z")


class LocalConfigError(ValueError):
    """The local.env file is not a valid simple key/value registry."""


def parse_local_config(text: str) -> dict[str, str]:
    """Parse KEY=VALUE lines; reject malformed keys, values and duplicates."""
    values: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise LocalConfigError(f"line {number}: expected KEY=VALUE")
        key, raw_value = line.split("=", 1)
        key = key.strip()
        value = raw_value.strip()
        if not _KEY.fullmatch(key):
            raise LocalConfigError(f"line {number}: invalid configuration key")
        if key in values:
            raise LocalConfigError(f"line {number}: duplicate key {key}")
        if value[:1] in {"'", '"'}:
            quote = value[0]
            if len(value) < 2 or value[-1] != quote:
                raise LocalConfigError(f"line {number}: unmatched quote")
            value = value[1:-1]
        elif value.endswith(("'", '"')):
            raise LocalConfigError(f"line {number}: unmatched quote")
        values[key] = value
    return values


def read_local_config(root: Path = ROOT) -> dict[str, str]:
    """Read config/local.env; absent files remain empty for non-strict callers."""
    path = root / "config" / "local.env"
    if not path.is_file():
        return {}
    return parse_local_config(path.read_text(encoding="utf-8-sig"))
