"""Fail-closed Skyrim AE executable and active-order validation (stdlib only)."""
from __future__ import annotations

import ctypes
import base64
import binascii
import hashlib
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import subprocess
from typing import Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
MIN_AE_VERSION = (1, 6, 318)
REQUIRED_AE_MASTERS = (
    "Skyrim.esm",
    "Update.esm",
    "Dawnguard.esm",
    "HearthFires.esm",
    "Dragonborn.esm",
)


class TargetError(ValueError):
    """Target or load-order data cannot support a verified AE result."""


def settings(env: Mapping[str, str] | None = None, root: Path = ROOT) -> dict[str, str]:
    from scripts.local_config import read_local_config

    merged = read_local_config(root)
    merged.update(dict(os.environ if env is None else env))
    return merged


def parse_version(value: str) -> tuple[int, int, int]:
    match = re.search(r"(?:^|[^\d])(\d+)\.(\d+)\.(\d+)(?:\.\d+)?(?:$|[^\d])", str(value or ""))
    if not match:
        raise TargetError(f"cannot parse Skyrim executable ProductVersion: {value!r}")
    return tuple(int(part) for part in match.groups())


def compare_version(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    for a, b in zip(left, right):
        if a != b:
            return a - b
    return 0


def _native_path(value: str | Path) -> Path:
    """Map a configured Windows drive path to its WSL mount for path checks."""
    text = str(value)
    windows = PureWindowsPath(text)
    if os.name != "nt" and windows.drive and len(windows.drive) == 2 and windows.drive[1] == ":":
        return Path("/mnt") / windows.drive[0].lower() / Path(*windows.parts[1:])
    return Path(text).expanduser()


def read_executable_version(executable: str | Path) -> str:
    """Read ProductVersion from the PE version resource using Windows' version.dll."""
    if os.name != "nt":
        return _read_version_from_wsl(executable)
    path = str(Path(executable).resolve())
    version_dll = ctypes.WinDLL("version", use_last_error=True)
    get_size = version_dll.GetFileVersionInfoSizeW
    get_size.argtypes = (ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint))
    get_size.restype = ctypes.c_uint
    get_info = version_dll.GetFileVersionInfoW
    get_info.argtypes = (ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p)
    get_info.restype = ctypes.c_int
    query = version_dll.VerQueryValueW
    query.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint))
    query.restype = ctypes.c_int

    ignored = ctypes.c_uint()
    size = get_size(path, ctypes.byref(ignored))
    if not size:
        raise TargetError("Skyrim executable has no readable version resource")
    buffer = ctypes.create_string_buffer(size)
    if not get_info(path, 0, size, buffer):
        raise TargetError("Windows could not read the Skyrim executable version resource")

    def query_string(subblock: str) -> str | None:
        value = ctypes.c_void_p()
        length = ctypes.c_uint()
        if not query(buffer, subblock, ctypes.byref(value), ctypes.byref(length)) or not value.value:
            return None
        text = ctypes.wstring_at(value.value, length.value).rstrip("\0").strip()
        return text or None

    translations: list[tuple[int, int]] = []
    value = ctypes.c_void_p()
    length = ctypes.c_uint()
    if query(buffer, r"\VarFileInfo\Translation", ctypes.byref(value), ctypes.byref(length)) and value.value:
        words = ctypes.cast(value, ctypes.POINTER(ctypes.c_ushort))
        translations = [(words[i], words[i + 1]) for i in range(0, length.value // 2, 2)]
    for language, codepage in translations:
        result = query_string(rf"\StringFileInfo\{language:04x}{codepage:04x}\ProductVersion")
        if result:
            return result
    for table in ("040904B0", "000004B0", "040904E4"):
        result = query_string(rf"\StringFileInfo\{table}\ProductVersion")
        if result:
            return result
    raise TargetError("ProductVersion string is absent from the Skyrim executable version resource")


def _read_version_from_wsl(executable: str | Path) -> str:
    """Use the host Windows version API through its installed PowerShell bridge in WSL."""
    shell = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
    if not shell:
        # WSL interop often exposes cmd.exe without importing the full Windows
        # PATH. Check the inbox PowerShell path directly before failing closed.
        candidate = Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
        if candidate.is_file():
            shell = str(candidate)
    if not shell:
        raise TargetError("Skyrim ProductVersion inspection requires Windows or its PowerShell bridge")
    native = Path(executable).resolve().as_posix()
    match = re.match(r"^/mnt/([a-z])(?:/(.*))?$", native, re.IGNORECASE)
    if not match:
        raise TargetError("WSL ProductVersion inspection requires the executable under a mounted Windows drive")
    windows_path = match.group(1).upper() + ":\\" + (match.group(2) or "").replace("/", "\\")
    path_payload = base64.b64encode(windows_path.encode("utf-8")).decode("ascii")
    # Put the path inside an encoded script rather than an environment value:
    # WSL's Windows process bridge can otherwise transform drive paths.
    command = (
        "$ErrorActionPreference='Stop'; "
        f"$p=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{path_payload}')); "
        "$v=[Diagnostics.FileVersionInfo]::GetVersionInfo($p).ProductVersion; "
        "[Console]::Out.Write([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([string]$v)))"
    )
    encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
    try:
        result = subprocess.run(
            [shell, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_command],
            capture_output=True, text=False, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TargetError("PowerShell could not read the Skyrim executable version resource") from exc
    encoded = result.stdout.strip()
    if result.returncode != 0 or not encoded:
        raise TargetError("PowerShell did not return a Skyrim ProductVersion")
    try:
        return base64.b64decode(encoded, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise TargetError("PowerShell returned an invalid ProductVersion payload") from exc


def assert_ae_target(
    env: Mapping[str, str] | None = None,
    *,
    root: Path = ROOT,
    version_reader: Callable[[str | Path], str] = read_executable_version,
) -> dict[str, str]:
    config = settings(env, root)
    if config.get("SKYRIM_EDITION") != "AE":
        raise TargetError("SKYRIM_EDITION must be explicitly set to AE")
    game_value = config.get("GAME_ROOT", "").strip()
    if not game_value:
        raise TargetError("GAME_ROOT must point to the Skyrim AE installation")
    game_root = _native_path(game_value).resolve()
    executable_value = config.get("SKYRIM_EXE_PATH") or str(game_root / "SkyrimSE.exe")
    executable = _native_path(executable_value).resolve()
    if executable.name.casefold() != "skyrimse.exe":
        raise TargetError("AE target executable must be SkyrimSE.exe")
    if executable == game_root or game_root not in executable.parents:
        raise TargetError("SkyrimSE.exe must be inside GAME_ROOT")
    if not game_root.is_dir():
        raise TargetError("GAME_ROOT is not an accessible directory")
    if not executable.is_file():
        raise TargetError("SkyrimSE.exe is not an accessible file")
    version_text = version_reader(executable)
    version = parse_version(version_text)
    if version[0] != 1 or version[1] != 6 or compare_version(version, MIN_AE_VERSION) < 0:
        raise TargetError(f"unsupported Skyrim runtime {version_text}; AE 1.6.318 or newer is required")
    return {
        "edition": "AE",
        "game_root": str(game_root),
        "executable": str(executable),
        "version": ".".join(map(str, version)),
    }


def resolve_plugins_txt(env: Mapping[str, str] | None = None, *, game_root: str | Path | None = None, root: Path = ROOT) -> Path:
    config = settings(env, root)
    candidate = config.get("PLUGINS_TXT", "").strip()
    if not candidate and config.get("SKYRIM_LOADORDER_DIR", "").strip():
        candidate = str(Path(config["SKYRIM_LOADORDER_DIR"]) / "plugins.txt")
    if not candidate and config.get("LOCALAPPDATA", "").strip():
        candidate = str(Path(config["LOCALAPPDATA"]) / "Skyrim Special Edition" / "plugins.txt")
    if not candidate and config.get("USERPROFILE", "").strip():
        candidate = str(Path(config["USERPROFILE"]) / "AppData" / "Local" / "Skyrim Special Edition" / "plugins.txt")
    if not candidate:
        raise TargetError("set PLUGINS_TXT to the selected AE/MO2 profile's explicit plugins.txt")
    windows_path = PureWindowsPath(candidate)
    path = _native_path(candidate)
    if not path.is_absolute() and not windows_path.is_absolute():
        raise TargetError("PLUGINS_TXT must be an absolute path")
    path = path.resolve()
    if path.name.casefold() != "plugins.txt":
        raise TargetError("PLUGINS_TXT must name the active plugins.txt, not loadorder.txt")
    if not path.is_file():
        raise TargetError("the configured active plugins.txt is missing or inaccessible")
    if game_root is not None and Path(game_root).resolve() in path.parents:
        raise TargetError("PLUGINS_TXT must be the active profile list, not a file inside GAME_ROOT")
    return path


def parse_active_plugins(text: str) -> list[str]:
    active = [line.strip()[1:].strip() for line in text.lstrip("\ufeff").splitlines() if line.strip().startswith("*")]
    if not active:
        raise TargetError("active plugin list contains no active plugins")
    if active[0].casefold() != "skyrim.esm":
        raise TargetError("active plugin list must begin with Skyrim.esm")
    seen: set[str] = set()
    for name in active:
        if not re.fullmatch(r'[^\\/:*?"<>|]+\.(?:esm|esp|esl)', name, re.IGNORECASE):
            raise TargetError(f"invalid active plugin name: {name}")
        folded = name.casefold()
        if folded in seen:
            raise TargetError(f"duplicate active plugin: {name}")
        seen.add(folded)
    missing = [master for master in REQUIRED_AE_MASTERS if master.casefold() not in seen]
    if missing:
        raise TargetError("active plugin list is incomplete; missing required AE masters: " + ", ".join(missing))
    return active


def preflight(env: Mapping[str, str] | None = None, *, root: Path = ROOT, version_reader=read_executable_version) -> dict[str, object]:
    target = assert_ae_target(env, root=root, version_reader=version_reader)
    load_order = resolve_plugins_txt(env, game_root=target["game_root"], root=root)
    load_bytes = load_order.read_bytes()
    plugins = parse_active_plugins(load_bytes.decode("utf-8-sig"))
    exe_bytes = Path(target["executable"]).read_bytes()
    return {
        "edition": target["edition"],
        "runtime": target["version"],
        "executable_sha256": hashlib.sha256(exe_bytes).hexdigest(),
        "active_plugins": len(plugins),
        "base_plugin": plugins[0],
        "load_order": str(load_order),
        "load_order_sha256": hashlib.sha256(load_bytes).hexdigest(),
        "live_runtime_tested": False,
    }
