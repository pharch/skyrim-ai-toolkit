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
import struct
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

    values = read_local_config(root)
    if env is not None:
        values.update(dict(env))
    return values


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
    """Read ProductVersion from SkyrimSE.exe's PE version resource."""
    if os.name != "nt":
        # Read the file's version resource directly first. This keeps target
        # attestation usable in WSL even when Windows process interop is off.
        try:
            return _read_pe_product_version(Path(executable))
        except TargetError:
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


def _read_pe_product_version(executable: Path) -> str:
    """Read the named ProductVersion string from a PE resource tree (stdlib only)."""
    try:
        data = executable.read_bytes()
    except OSError as exc:
        raise TargetError(f"cannot read executable PE data: {executable}") from exc

    def require(offset: int, size: int, label: str) -> None:
        if offset < 0 or size < 0 or offset + size > len(data):
            raise TargetError(f"truncated PE {label}")

    def u16(offset: int) -> int:
        require(offset, 2, "header")
        return struct.unpack_from("<H", data, offset)[0]

    def u32(offset: int) -> int:
        require(offset, 4, "header")
        return struct.unpack_from("<I", data, offset)[0]

    if len(data) < 0x40 or data[:2] != b"MZ":
        raise TargetError("executable is not a valid PE image")
    pe = u32(0x3C)
    require(pe, 24, "COFF header")
    if data[pe:pe + 4] != b"PE\0\0":
        raise TargetError("executable has no PE signature")
    section_count = u16(pe + 6)
    optional_size = u16(pe + 20)
    optional = pe + 24
    require(optional, optional_size, "optional header")
    magic = u16(optional)
    if magic == 0x10B:  # PE32
        directory_base = optional + 96
    elif magic == 0x20B:  # PE32+
        directory_base = optional + 112
    else:
        raise TargetError("unsupported PE optional-header format")
    if optional_size < directory_base - optional + (3 * 8):
        raise TargetError("PE optional header has no resource directory entry")
    resource_rva, resource_size = struct.unpack_from("<II", data, directory_base + 2 * 8)
    if not resource_rva or not resource_size:
        raise TargetError("executable has no PE version resource directory")

    sections: list[tuple[int, int, int, int]] = []
    section_table = optional + optional_size
    require(section_table, section_count * 40, "section table")
    for index in range(section_count):
        entry = section_table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", data, entry + 8)
        sections.append((virtual_address, max(virtual_size, raw_size), raw_size, raw_pointer))

    def rva_offset(rva: int, size: int = 1) -> int:
        for virtual_address, span, raw_size, raw_pointer in sections:
            delta = rva - virtual_address
            if 0 <= delta < span and delta + size <= raw_size:
                require(raw_pointer + delta, size, "resource data")
                return raw_pointer + delta
        raise TargetError(f"PE resource RVA 0x{rva:X} is not backed by section data")

    resource_file_offset = rva_offset(resource_rva, min(resource_size, 16))
    require(resource_file_offset, 16, "resource directory")
    root = resource_file_offset

    def directory_entries(relative: int) -> list[tuple[int, int]]:
        directory = root + relative
        require(directory, 16, "resource directory entry")
        named, ids = struct.unpack_from("<HH", data, directory + 12)
        count = named + ids
        require(directory + 16, count * 8, "resource directory entries")
        return [struct.unpack_from("<II", data, directory + 16 + i * 8) for i in range(count)]

    version_directory: int | None = None
    for name, target in directory_entries(0):
        if not name & 0x80000000 and (name & 0xFFFF) == 16:
            if target & 0x80000000:
                version_directory = target & 0x7FFFFFFF
            break
    if version_directory is None:
        raise TargetError("executable has no RT_VERSION resource")

    resource_values: list[tuple[int, int]] = []

    def collect_data(relative: int, depth: int = 0) -> None:
        if depth > 4:
            raise TargetError("PE version resource tree is unexpectedly deep")
        for _name, target in directory_entries(relative):
            child = target & 0x7FFFFFFF
            if target & 0x80000000:
                collect_data(child, depth + 1)
            else:
                entry = root + child
                require(entry, 16, "resource data entry")
                rva, size = struct.unpack_from("<II", data, entry)
                if size:
                    resource_values.append((rva, size))

    collect_data(version_directory)

    def parse_block(blob: bytes, start: int, limit: int, depth: int = 0) -> tuple[str, bytes, list[tuple[str, bytes, list]]]:
        if depth > 16 or start + 6 > limit:
            raise TargetError("malformed PE version string block")
        length, value_length, value_type = struct.unpack_from("<HHH", blob, start)
        block_end = start + length
        if length < 6 or block_end > limit:
            raise TargetError("malformed PE version string block length")
        cursor = start + 6
        key_end = cursor
        while key_end + 2 <= block_end and blob[key_end:key_end + 2] != b"\0\0":
            key_end += 2
        if key_end + 2 > block_end:
            raise TargetError("unterminated PE version string block key")
        try:
            key = blob[cursor:key_end].decode("utf-16le")
        except UnicodeDecodeError as exc:
            raise TargetError("invalid UTF-16 key in PE version resource") from exc
        cursor = (key_end + 2 + 3) & ~3
        value_size = value_length * (2 if value_type == 1 else 1)
        if cursor + value_size > block_end:
            raise TargetError("PE version block value exceeds its declared length")
        value = blob[cursor:cursor + value_size]
        cursor = (cursor + value_size + 3) & ~3
        children = []
        while cursor + 6 <= block_end:
            child_length = struct.unpack_from("<H", blob, cursor)[0]
            if child_length == 0:
                break
            child = parse_block(blob, cursor, block_end, depth + 1)
            children.append(child)
            cursor = (cursor + child_length + 3) & ~3
        return key, value, children

    for version_rva, version_size in resource_values:
        try:
            offset = rva_offset(version_rva, version_size)
            blob = data[offset:offset + version_size]
            key, fixed, children = parse_block(blob, 0, len(blob))
            if key != "VS_VERSION_INFO" or len(fixed) < 52 or struct.unpack_from("<I", fixed)[0] != 0xFEEF04BD:
                continue

            def find_product_version(node: tuple[str, bytes, list]) -> str | None:
                node_key, value, descendants = node
                if node_key == "ProductVersion" and value:
                    try:
                        text = value.decode("utf-16le").rstrip("\0").strip()
                    except UnicodeDecodeError:
                        return None
                    if text:
                        return text
                for descendant in descendants:
                    found = find_product_version(descendant)
                    if found:
                        return found
                return None

            for child in children:
                found = find_product_version(child)
                if found:
                    return found
        except TargetError:
            continue
    raise TargetError("ProductVersion string is absent from the PE version resource")


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


def _resolve_explicit_profile_plugins(
    config: Mapping[str, str],
    *,
    list_key: str,
    profile_key: str,
    game_root: str | Path | None,
    require_profile: bool = False,
) -> Path:
    candidate = config.get(list_key, "").strip()
    if not candidate:
        raise TargetError(f"set {list_key} to the explicit plugins.txt for {profile_key}")
    windows_path = PureWindowsPath(candidate)
    path = _native_path(candidate)
    if not path.is_absolute() and not windows_path.is_absolute():
        raise TargetError(f"{list_key} must be an absolute path")
    path = path.resolve()
    if path.name.casefold() != "plugins.txt":
        raise TargetError(f"{list_key} must name plugins.txt, not loadorder.txt")
    if not path.is_file():
        raise TargetError(f"the configured {list_key} is missing or inaccessible")
    if game_root is not None and Path(game_root).resolve() in path.parents:
        raise TargetError(f"{list_key} must be a profile list outside GAME_ROOT")
    profile = config.get(profile_key, "").strip()
    if require_profile and not profile:
        raise TargetError(f"set {profile_key} to the explicitly selected MO2 profile")
    if profile:
        profile_path = _native_path(profile).resolve()
        if not profile_path.is_dir():
            raise TargetError(f"configured {profile_key} is not an accessible directory")
        if path.parent.resolve() != profile_path:
            raise TargetError(f"{list_key} must belong to the explicitly selected {profile_key}")
    return path


def resolve_plugins_txt(env: Mapping[str, str] | None = None, *, game_root: str | Path | None = None, root: Path = ROOT) -> Path:
    config = settings(env, root)
    return _resolve_explicit_profile_plugins(
        config, list_key="PLUGINS_TXT", profile_key="MO2_PROFILE_DIR", game_root=game_root,
        require_profile=True,
    )


def resolve_test_plugins_txt(env: Mapping[str, str] | None = None, *, game_root: str | Path | None = None, root: Path = ROOT) -> Path:
    config = settings(env, root)
    return _resolve_explicit_profile_plugins(
        config, list_key="SKYRIM_TEST_PLUGINS_TXT", profile_key="SKYRIM_TEST_PROFILE_DIR", game_root=game_root,
        require_profile=True,
    )


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


def preflight(
    env: Mapping[str, str] | None = None,
    *,
    root: Path = ROOT,
    version_reader=read_executable_version,
    scoped_five_master: str | Path | None = None,
    test_profile: bool = False,
) -> dict[str, object]:
    if scoped_five_master is not None and test_profile:
        raise TargetError("choose either a scoped five-master list or the designated test profile")
    target = assert_ae_target(env, root=root, version_reader=version_reader)
    if test_profile:
        load_order = resolve_test_plugins_txt(env, game_root=target["game_root"], root=root)
        scope = "designated-disposable-profile"
        full_order_verified = True
    elif scoped_five_master is None:
        load_order = resolve_plugins_txt(env, game_root=target["game_root"], root=root)
        scope = "explicit-active-order"
        full_order_verified = True
    else:
        windows_path = PureWindowsPath(str(scoped_five_master))
        load_order = _native_path(scoped_five_master)
        if not load_order.is_absolute() and not windows_path.is_absolute():
            raise TargetError("scoped five-master list must be an explicit absolute path")
        load_order = load_order.resolve()
        if load_order.name.casefold() != "plugins.txt":
            raise TargetError("scoped five-master input must be the generated plugins.txt")
        if not load_order.is_file():
            raise TargetError("scoped five-master plugins.txt is missing or inaccessible")
        if Path(target["game_root"]).resolve() in load_order.parents:
            raise TargetError("scoped plugin list must remain in the isolated research session")
        scope = "scoped-five-master"
        full_order_verified = False
    load_bytes = load_order.read_bytes()
    plugins = parse_active_plugins(load_bytes.decode("utf-8-sig"))
    if scoped_five_master is not None and [x.casefold() for x in plugins] != [x.casefold() for x in REQUIRED_AE_MASTERS]:
        raise TargetError("scoped list must contain exactly the five official AE masters in canonical order")
    exe_bytes = Path(target["executable"]).read_bytes()
    config = settings(env, root)
    selected_profile = bool(config.get("MO2_PROFILE_DIR", "").strip()) and scoped_five_master is None and not test_profile
    disposable_profile = bool(config.get("SKYRIM_TEST_PROFILE_DIR", "").strip()) and test_profile
    return {
        "edition": target["edition"],
        "runtime": target["version"],
        "executable_sha256": hashlib.sha256(exe_bytes).hexdigest(),
        "active_plugins": len(plugins),
        "base_plugin": plugins[0],
        "load_order": str(load_order),
        "load_order_sha256": hashlib.sha256(load_bytes).hexdigest(),
        "scope": scope,
        "full_order_verified": full_order_verified,
        "selected_profile_verified": selected_profile,
        "disposable_test_profile_verified": disposable_profile,
        "live_runtime_tested": False,
    }
