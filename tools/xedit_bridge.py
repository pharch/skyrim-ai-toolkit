#!/usr/bin/env python3
"""Route the installed read-only SSEEdit helper from canonical local bindings.

`file-records` is a plugin-file parser; `prepare` creates a view-only SSEView
session without launching it. `native-query` reproduces the original xEdit
launch, UIA hotkey dispatch, and read-only native field export.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BRIDGE_COPY = Path(".local/xedit-authoritative-copy")
QUERY_TEMPLATE = Path("tools/xedit_scripts/native_record_query.pas.tpl")
SOURCE_FILES = (
    "scripts/skyrim_tool.py",
    "scripts/run-xedit.ps1",
    "scripts/xedit-status.ps1",
    "scripts/xedit-export-hotkey.ps1",
    "scripts/xedit/README.md",
    "scripts/xedit/export-records.pas",
    "scripts/xedit/investigation-export.pas",
    "scripts/xedit/investigation-references.pas",
)
OFFICIAL_PLUGINS = (
    "Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm",
)


class BridgeError(ValueError):
    """The configured authoritative bridge cannot be safely staged."""


def _same_path(left: str, right: str) -> bool:
    return left.replace("/", "\\").rstrip("\\").casefold() == right.replace("/", "\\").rstrip("\\").casefold()


def helper_config(config: dict[str, str]) -> dict[str, str]:
    """Map the toolkit's canonical names to the legacy helper's local schema."""
    canonical_exe = config.get("SKYRIM_EXE_PATH", "").strip()
    legacy_exe = config.get("SKYRIM_EXE", "").strip()
    if canonical_exe and legacy_exe and not _same_path(canonical_exe, legacy_exe):
        raise BridgeError("SKYRIM_EXE conflicts with canonical SKYRIM_EXE_PATH")
    values = {
        "SSEEDIT_EXE": config.get("SSEEDIT_EXE", "").strip(),
        "SKYRIM_DATA": config.get("SKYRIM_DATA", "").strip(),
        "XEDIT_SCRIPTS": config.get("XEDIT_SCRIPTS", "").strip(),
        "SKYRIM_EXE": canonical_exe or legacy_exe,
        "INCLUDE_CREATION_CLUB": config.get("INCLUDE_CREATION_CLUB", "0").strip() or "0",
    }
    missing = [key for key in ("SSEEDIT_EXE", "SKYRIM_DATA", "SKYRIM_EXE") if not values[key]]
    if missing:
        raise BridgeError("missing xEdit bindings in config/local.env: " + ", ".join(missing))
    if values["INCLUDE_CREATION_CLUB"] not in {"0", "1"}:
        raise BridgeError("INCLUDE_CREATION_CLUB must be 0 or 1")
    if any('"' in value or "\n" in value or "\r" in value for value in values.values()):
        raise BridgeError("xEdit bindings contain a quote or newline unsupported by the bridge config")
    return values


def render_helper_config(values: dict[str, str]) -> str:
    lines = [
        "# Generated from the toolkit's ignored config/local.env by tools/xedit_bridge.py.",
        "# Do not edit this derived file; change the toolkit's canonical local.env.",
    ]
    lines.extend(f'{key}="{value}"' for key, value in values.items())
    return "\n".join(lines) + "\n"


def materialize(root: Path = ROOT, config: dict[str, str] | None = None) -> tuple[Path, dict[str, str]]:
    """Stage verified helper files under ignored .local without touching source."""
    from scripts.local_config import read_local_config
    from tools.ae_target import _native_path

    values = read_local_config(root) if config is None else config
    source_value = values.get("LEGACY_SKYRIM_REPO", "").strip()
    if not source_value:
        raise BridgeError("set LEGACY_SKYRIM_REPO to the read-only authoritative helper checkout")
    source = _native_path(source_value).resolve()
    if not source.is_dir():
        raise BridgeError("configured LEGACY_SKYRIM_REPO is not accessible")
    translated = helper_config(values)
    destination = root / BRIDGE_COPY
    destination.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for relative in SOURCE_FILES:
        source_file = source / relative
        if not source_file.is_file():
            raise BridgeError(f"authoritative bridge file is missing: {relative}")
        content = source_file.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            target.write_bytes(content)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise BridgeError(f"staged bridge file hash mismatch: {relative}")
        hashes[relative] = digest
    private_config = destination / "config" / "local.env"
    private_config.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_helper_config(translated)
    private_config.write_text(rendered, encoding="utf-8")
    return destination, hashes


def _capture_dir(root: Path, category: str = "xedit-bridge") -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    path = root / ".local" / "alignment" / category / stamp
    path.mkdir(parents=True, exist_ok=False)
    return path


def _captured_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def invoke_helper(
    bridge: Path,
    command: list[str],
    *,
    root: Path = ROOT,
    timeout: int = 120,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    capture = _capture_dir(root)
    try:
        result = subprocess.run(
            [sys.executable, str(bridge / "scripts" / "skyrim_tool.py"), *command],
            cwd=bridge, text=True, capture_output=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        (capture / "stdout.raw").write_text(_captured_text(exc.stdout), encoding="utf-8", errors="replace")
        (capture / "stderr.raw").write_text(_captured_text(exc.stderr), encoding="utf-8", errors="replace")
        raise BridgeError(f"helper timed out after {timeout} seconds; raw output is retained under {capture.relative_to(root)}") from exc
    (capture / "stdout.raw").write_text(result.stdout, encoding="utf-8")
    (capture / "stderr.raw").write_text(result.stderr, encoding="utf-8")
    return result, capture


def _safe_result(
    command: str,
    result: subprocess.CompletedProcess[str],
    capture: Path,
    hashes: dict[str, str],
    *,
    root: Path = ROOT,
) -> dict[str, object]:
    summary: dict[str, object] = {
        "command": command,
        "exit_code": result.returncode,
        "source_files_sha256": hashes,
        "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest(),
        "raw_output": str(capture.relative_to(root)),
    }
    return summary


def _doctor(root: Path, bridge: Path, hashes: dict[str, str]) -> dict[str, object]:
    result, capture = invoke_helper(bridge, ["doctor"], root=root)
    summary = _safe_result("doctor", result, capture, hashes, root=root)
    try:
        raw = json.loads(result.stdout)
        from scripts.local_config import read_local_config
        from tools.ae_target import _native_path

        config = read_local_config(root)
        script_dir = _native_path(config["XEDIT_SCRIPTS"]) if config.get("XEDIT_SCRIPTS", "").strip() else None
        summary["configured_inputs_exist"] = all(item.get("exists", False) for item in raw.values())
        summary["input_count"] = len(raw)
        summary["file_record_query_is_native_xedit"] = False
        summary["xedit_scripts_path_exists"] = script_dir.is_dir() if script_dir is not None else None
        summary["custom_script_installation"] = "per-session -S directory; no global script install required"
        summary["native_query_template_exists"] = (root / QUERY_TEMPLATE).is_file()
        summary["mo2_required_for_official_masters"] = False
        summary["native_export_interface"] = (
            "SSEView -view against the official-master .local Data view; isolated -S script directory; "
            "Ctrl+Alt+F9 dispatches the read-only Apply Script exporter"
        )
        summary["native_query_command"] = (
            "tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm "
            "--editor-id dunDA14MorvunskarQST"
        )
        receipt = validate_native_receipt(root)
        summary["latest_native_query"] = receipt
        if not summary["native_query_template_exists"]:
            summary["configured_inputs_exist"] = False
    except (json.JSONDecodeError, AttributeError):
        summary["configured_inputs_exist"] = False
        summary["output_parse"] = "invalid helper doctor JSON"
    return summary


def _prepare(
    root: Path,
    bridge: Path,
    hashes: dict[str, str],
    *,
    data_overlay: Path | None = None,
) -> dict[str, object]:
    result, capture = invoke_helper(bridge, ["prepare-xedit"], root=root)
    summary = _safe_result("prepare", result, capture, hashes, root=root)
    if result.returncode != 0:
        summary["prepared"] = False
        return summary
    session = Path(result.stdout.strip().splitlines()[-1]).resolve()
    allowed = (bridge / "out" / "xedit").resolve()
    if allowed not in session.parents:
        raise BridgeError("helper returned a session outside its isolated xEdit output directory")
    manifest = json.loads((session / "manifest.json").read_text(encoding="utf-8"))
    if data_overlay is not None:
        manifest["native_data_overlay"] = str(data_overlay.relative_to(root))
        manifest["native_data_scope"] = "five official masters; Creation Club and user plugins omitted"
        manifest["effective_loaded_files_verified"] = False
        (session / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    summary.update({
        "prepared": True,
        "session": str(session.relative_to(root)),
        "manifest_sha256": hashlib.sha256((session / "manifest.json").read_bytes()).hexdigest(),
        "export_script_sha256": hashlib.sha256((session / "export-records.pas").read_bytes()).hexdigest(),
        "plugins": manifest.get("plugins", []),
        "mode": manifest.get("mode"),
        "native_launch_requested": False,
        "record_query_completed": False,
        "native_data_overlay": str(data_overlay.relative_to(root)) if data_overlay is not None else None,
        "effective_loaded_files_verified": False,
    })
    return summary


def _pascal_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def render_native_query_script(
    template: str,
    *,
    output_path: str,
    loaded_files_path: str,
    status_path: str,
    plugin: str,
    signature: str,
    editor_id: str,
) -> str:
    """Render the original field walker as an xEdit Apply Script hotkey query."""
    if plugin not in OFFICIAL_PLUGINS:
        raise BridgeError("native official-master query requires an official plugin name")
    if not re.fullmatch(r"[A-Z0-9]{4}", signature):
        raise BridgeError("signature must be exactly four uppercase letters or digits")
    if not editor_id or any(ord(ch) < 32 for ch in editor_id):
        raise BridgeError("EditorID must be nonempty and contain no control characters")
    replacements = {
        "__OUTPUT__": _pascal_string(output_path),
        "__LOADED__": _pascal_string(loaded_files_path),
        "__STATUS__": _pascal_string(status_path),
        "__PLUGIN__": _pascal_string(plugin),
        "__SIGNATURE__": _pascal_string(signature),
        "__EDITOR_ID__": _pascal_string(editor_id),
    }
    script = template
    for token, value in replacements.items():
        script = script.replace(token, value)
    unresolved = re.findall(r"__[A-Z_]+__", script)
    if unresolved:
        raise BridgeError("native query template contains unresolved placeholders: " + ", ".join(sorted(set(unresolved))))
    return script


def validate_official_plugin_list(plugins_text: str) -> tuple[str, ...]:
    """Require the exact ordered vanilla master selection emitted by the source helper."""
    plugins = tuple(line.strip().removeprefix("*") for line in plugins_text.splitlines() if line.strip())
    if plugins != OFFICIAL_PLUGINS:
        raise BridgeError("isolated xEdit list must contain exactly the five official masters in canonical order")
    return plugins


def validate_native_receipt(root: Path = ROOT) -> dict[str, object]:
    """Verify a locally recorded native query without launching an application."""
    receipt_path = root / ".local" / "xedit-native" / "latest.json"
    if not receipt_path.is_file():
        return {"status": "NOT_RUN", "reason": "native query has not produced a local receipt"}
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        tsv = root / str(receipt["tsv"])
        result = root / str(receipt["result_json"])
        valid = (
            receipt.get("status") == "PASS"
            and tsv.is_file()
            and result.is_file()
            and hashlib.sha256(tsv.read_bytes()).hexdigest() == receipt.get("tsv_sha256")
            and hashlib.sha256(result.read_bytes()).hexdigest() == receipt.get("result_json_sha256")
            and tuple(receipt.get("plugins", [])) == OFFICIAL_PLUGINS
            and tuple(
                name for name in receipt.get("loaded_files", [])
                if str(name).casefold() != "skyrimse.exe"
            ) == OFFICIAL_PLUGINS
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return {"status": "STALE_OR_INVALID", "reason": "native query receipt or output failed integrity checks"}
    if not valid:
        return {"status": "STALE_OR_INVALID", "reason": "native query receipt or output failed integrity checks"}
    return {
        "status": "PASS",
        "record": receipt.get("record"),
        "plugins": receipt.get("plugins"),
        "loaded_files": receipt.get("loaded_files"),
        "completed_utc": receipt.get("completed_utc"),
        "tsv_sha256": receipt.get("tsv_sha256"),
        "result_json_sha256": receipt.get("result_json_sha256"),
    }


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _powershell_binary() -> str:
    executable = shutil.which("powershell.exe") or shutil.which("powershell")
    if not executable:
        raise BridgeError("native xEdit requires Windows PowerShell; use native Windows or WSL2 with Windows interop")
    return executable


def _windows_path(path: Path) -> str:
    if os.name == "nt":
        return str(path.resolve())
    try:
        return subprocess.check_output(["wslpath", "-w", str(path.resolve())], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BridgeError("could not translate the isolated session path for Windows PowerShell") from exc


def _run_powershell(binary: str, args: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [binary, "-NoProfile", "-ExecutionPolicy", "Bypass", *args],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise BridgeError(f"Windows PowerShell timed out after {timeout} seconds") from exc


def _decode_windows(value: bytes) -> str:
    # Windows PowerShell 5.1 writes using the active Windows code page; the
    # WSL research host currently uses a western Windows code page.
    return value.decode("cp1252", errors="replace")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_official_data_overlay(root: Path, source_data: Path) -> tuple[Path, dict[str, object]]:
    """Build a read-only, official-master-only copy under ignored .local."""
    overlay = root / ".local" / "xedit-data" / "official-ae-v1"
    overlay.mkdir(parents=True, exist_ok=True)
    expected: dict[str, Path] = {}
    for name in OFFICIAL_PLUGINS:
        source = source_data / name
        if not source.is_file():
            raise BridgeError(f"configured game Data is missing official master {name}")
        expected[name] = source

    # Keep localized vanilla string tables available when installed. Their
    # names correspond to the five masters; no Creation Club strings are staged.
    strings = source_data / "Strings"
    if strings.is_dir():
        stems = {Path(name).stem.casefold() + "_" for name in OFFICIAL_PLUGINS}
        extensions = {".strings", ".dlstrings", ".ilstrings"}
        for source in strings.iterdir():
            if source.is_file() and source.suffix.casefold() in extensions and any(
                source.name.casefold().startswith(stem) for stem in stems
            ):
                expected[(Path("Strings") / source.name).as_posix()] = source

    def make_readonly_copy(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source_hash = _sha256_file(source)
        if destination.exists() or destination.is_symlink():
            if destination.is_symlink():
                destination.unlink()
            elif not destination.is_file():
                raise BridgeError(f"managed xEdit data path is not a file: {destination.relative_to(root)}")
            elif not os.path.samefile(source, destination):
                if _sha256_file(destination) == source_hash:
                    destination.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
                    return
                destination.chmod(stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            if destination.exists():
                destination.unlink()
        temporary = destination.with_name(destination.name + ".partial")
        if temporary.exists():
            temporary.chmod(stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            temporary.unlink()
        try:
            shutil.copyfile(source, temporary)
        except OSError as exc:
            raise BridgeError(f"could not copy official xEdit input {source.name} into ignored .local: {exc}") from exc
        if _sha256_file(temporary) != source_hash:
            temporary.unlink()
            raise BridgeError(f"xEdit Data copy hash mismatch for {source.name}")
        os.replace(temporary, destination)
        destination.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        if _sha256_file(destination) != source_hash or os.path.samefile(source, destination):
            raise BridgeError(f"xEdit Data copy validation failed for {source.name}")

    for relative_name, source in expected.items():
        make_readonly_copy(source, overlay / relative_name)

    official_names = {Path(name).name.casefold() for name in OFFICIAL_PLUGINS}
    unexpected = [
        path.relative_to(overlay).as_posix()
        for path in overlay.rglob("*")
        if path.is_file() and path.suffix.casefold() in {".esm", ".esp", ".esl"}
        and path.name.casefold() not in official_names
    ]
    ccc_files = [path.name for path in overlay.iterdir() if path.is_file() and path.name.casefold() == "skyrim.ccc"]
    if unexpected or ccc_files:
        details = unexpected + ccc_files
        raise BridgeError("managed official xEdit data overlay contains unexpected plugin inputs: " + ", ".join(details))

    file_manifest = [
        {"name": Path(name).as_posix(), "sha256": _sha256_file(source)}
        for name, source in sorted(expected.items())
    ]
    manifest = {
        "scope": "five official masters and their matching localized string tables only",
        "creation_club_list_present": False,
        "storage": "private copies under ignored .local; each destination is hash-verified and read-only",
        "source_files": file_manifest,
    }
    (overlay / "overlay-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return overlay, manifest


def configure_official_helper_data(
    root: Path, bridge: Path,
) -> tuple[Path, dict[str, object]]:
    """Bind the staged original helper to a vanilla-only view of configured Data."""
    from scripts.local_config import read_local_config
    from tools.ae_target import _native_path

    config = read_local_config(root)
    if (config.get("INCLUDE_CREATION_CLUB", "0").strip() or "0") != "0":
        raise BridgeError("official-master xEdit sessions require INCLUDE_CREATION_CLUB=0")
    source_data = _native_path(config["SKYRIM_DATA"])
    overlay, manifest = ensure_official_data_overlay(root, source_data)
    derived_values = helper_config(config)
    derived_values["SKYRIM_DATA"] = _windows_path(overlay)
    (bridge / "config" / "local.env").write_text(render_helper_config(derived_values), encoding="utf-8")
    return overlay, manifest


def _sanitize_json_controls(text: str) -> str:
    """Replace raw control characters in legacy UIA names before JSON parsing."""
    output: list[str] = []
    in_string = False
    escaped = False
    for char in text:
        code = ord(char)
        if in_string:
            if escaped:
                escaped = False
                output.append(char)
            elif char == "\\":
                escaped = True
                output.append(char)
            elif char == '"':
                in_string = False
                output.append(char)
            elif code < 0x20:
                output.append(" ")
            else:
                output.append(char)
        else:
            if char == '"':
                in_string = True
                output.append(char)
            elif code < 0x20 and char not in "\t\r\n":
                output.append(" ")
            else:
                output.append(char)
    return "".join(output)


def _parse_ui_status(raw: bytes) -> tuple[dict[str, object], list[str]]:
    if not raw.strip():
        return {"windows": []}, []
    text = _sanitize_json_controls(_decode_windows(raw))
    decoder = json.JSONDecoder()
    values: list[object] = []
    offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset >= len(text):
            break
        try:
            value, offset = decoder.raw_decode(text, offset)
        except json.JSONDecodeError as exc:
            raise BridgeError(f"xEdit UI status helper returned malformed JSON near byte {exc.pos}") from exc
        values.append(value)
    windows: list[dict[str, object]] = []
    for value in values:
        if isinstance(value, list):
            windows.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            windows.append(value)
        else:
            raise BridgeError("xEdit UI status helper returned a non-object JSON value")
    names: list[str] = []
    for window in windows:
        title = str(window.get("Window", ""))
        if title:
            names.append(title)
        for control in window.get("Controls", []):
            name = str(control.get("Name", ""))
            if name:
                names.append(name)
    return {"windows": windows}, names


def _native_session_script(
    root: Path,
    bridge: Path,
    hashes: dict[str, str],
    data_overlay: Path,
    plugin: str,
    signature: str,
    editor_id: str,
) -> tuple[Path, Path, dict[str, object]]:
    prepared = _prepare(root, bridge, hashes, data_overlay=data_overlay)
    if prepared.get("exit_code") != 0 or not prepared.get("prepared"):
        raise BridgeError("original SSEView session preparation failed; see " + str(prepared.get("raw_output")))
    session = (root / str(prepared["session"])).resolve()
    if not (bridge.resolve() / "out" / "xedit").resolve() in session.parents:
        raise BridgeError("prepared SSEView session escaped the isolated authoritative-helper output directory")
    plugins = validate_official_plugin_list((session / "plugins.txt").read_text(encoding="utf-8"))
    load_order = tuple(line.strip() for line in (session / "loadorder.txt").read_text(encoding="utf-8").splitlines() if line.strip())
    if load_order != OFFICIAL_PLUGINS:
        raise BridgeError("original helper generated an unexpected official-master load order")

    output = session / "native-records.tsv"
    loaded_files = session / "native-loaded-files.txt"
    script_status = session / "native-query-status.txt"
    template_path = root / QUERY_TEMPLATE
    template = template_path.read_text(encoding="utf-8")
    script = render_native_query_script(
        template,
        output_path=_windows_path(output),
        loaded_files_path=_windows_path(loaded_files),
        status_path=_windows_path(script_status),
        plugin=plugin,
        signature=signature,
        editor_id=editor_id,
    )
    script_path = session / "native-query.pas"
    script_path.write_text(script, encoding="utf-8")
    manifest_path = session / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({
        "native_query": {"plugin": plugin, "signature": signature, "editor_id": editor_id},
        "native_script": str(script_path),
        "native_script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        "native_output": str(output),
        "native_output_sha256": None,
        "native_loaded_files": str(loaded_files),
        "native_status": str(script_status),
        "native_invocation": "SSEView -view with -S pointing to this session; Ctrl+Alt+F9 invokes the script through Apply Script",
        "mo2_required": False,
        "load_order_scope": "five official AE masters only; no profile or mod override claim",
        "native_data_overlay": str(data_overlay.relative_to(root)),
        "native_data_scope": "read-only copies of the five official masters; Creation Club and user plugins omitted",
    })
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return session, output, {"prepared": prepared, "plugins": plugins, "manifest": manifest}


def _powershell_script(binary: str, script: str, capture: Path, label: str, *, timeout: int = 60) -> bytes:
    result = _run_powershell(binary, ["-Command", script], timeout=timeout)
    (capture / f"{label}.stdout.raw").write_bytes(result.stdout)
    (capture / f"{label}.stderr.raw").write_bytes(result.stderr)
    if result.returncode != 0:
        detail = _decode_windows(result.stderr).strip()[:500]
        raise BridgeError(f"PowerShell step {label} exited {result.returncode}: {detail or 'see private capture'}")
    return result.stdout


def _powershell_file(binary: str, script_path: Path, args: list[str], capture: Path, label: str) -> bytes:
    result = _run_powershell(binary, ["-File", _windows_path(script_path), *args], timeout=90)
    (capture / f"{label}.stdout.raw").write_bytes(result.stdout)
    (capture / f"{label}.stderr.raw").write_bytes(result.stderr)
    if result.returncode != 0:
        detail = _decode_windows(result.stderr).strip()[:500]
        raise BridgeError(f"original xEdit helper {label} exited {result.returncode}: {detail or 'see private capture'}")
    return result.stdout


def _xedit_processes(binary: str, capture: Path, label: str) -> list[dict[str, object]]:
    script = (
        "$items = @(Get-Process SSEEdit -ErrorAction SilentlyContinue | ForEach-Object { "
        "[pscustomobject]@{ Id=$_.Id; Title=$_.MainWindowTitle; Responding=$_.Responding } }); "
        "ConvertTo-Json -InputObject $items -Compress"
    )
    raw = _powershell_script(binary, script, capture, label)
    try:
        result = json.loads(_decode_windows(raw).strip() or "[]")
    except json.JSONDecodeError as exc:
        raise BridgeError("Windows process probe did not return valid JSON") from exc
    if isinstance(result, dict):
        return [result]
    return result


def _native_query(
    root: Path,
    bridge: Path,
    hashes: dict[str, str],
    *,
    plugin: str,
    signature: str,
    editor_id: str,
    timeout: int = 900,
    keep_open: bool = False,
) -> dict[str, object]:
    from scripts.local_config import read_local_config
    from tools.ae_target import _native_path

    config = read_local_config(root)
    source_data = _native_path(config["SKYRIM_DATA"])
    data_overlay, overlay_manifest = configure_official_helper_data(root, bridge)

    session, output, setup = _native_session_script(
        root, bridge, hashes, data_overlay, plugin, signature, editor_id
    )
    loaded_files = session / "native-loaded-files.txt"
    script_status = session / "native-query-status.txt"
    capture = _capture_dir(root, "xedit-native")
    (capture / "session.json").write_text(json.dumps({
        "session": str(session.relative_to(root)),
        "query": {"plugin": plugin, "signature": signature, "editor_id": editor_id},
        "source_files_sha256": hashes,
        "official_plugins": list(setup["plugins"]),
        "native_script_sha256": setup["manifest"]["native_script_sha256"],
        "native_data_overlay": str(data_overlay.relative_to(root)),
        "native_data_files": overlay_manifest["source_files"],
    }, indent=2), encoding="utf-8")

    # The scoped preflight verifies the executable's ProductVersion and this
    # exact official list; it intentionally does not require an MO2 profile.
    preflight = subprocess.run(
        [sys.executable, str(root / "tools" / "ae_preflight.py"), "--scoped-five-master", str(session / "plugins.txt")],
        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=False,
    )
    (capture / "scoped-preflight.stdout.raw").write_bytes(preflight.stdout)
    (capture / "scoped-preflight.stderr.raw").write_bytes(preflight.stderr)
    if preflight.returncode != 0:
        detail = _decode_windows(preflight.stdout + preflight.stderr).strip()[-1200:]
        raise BridgeError("scoped official-master AE preflight failed: " + (detail or str(capture.relative_to(root))))

    data = _native_path(config["SKYRIM_DATA"])
    missing_plugins = [name for name in OFFICIAL_PLUGINS if not (data / name).is_file()]
    if missing_plugins:
        raise BridgeError("official master files are unavailable: " + ", ".join(missing_plugins))
    for path in (session / "plugins.txt", session / "loadorder.txt", session / "native-query.pas"):
        if not path.is_file():
            raise BridgeError("native session input disappeared: " + str(path.relative_to(root)))

    binary = _powershell_binary()
    before = {int(item["Id"]) for item in _xedit_processes(binary, capture, "processes-before")}
    launch = _windows_path(session / "launch.ps1")
    launch_script = (
        "$p = Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile',"
        "'-ExecutionPolicy','Bypass','-File'," + _ps_quote(launch) + ") -PassThru; $p.Id"
    )
    launch_raw = _powershell_script(binary, launch_script, capture, "launch")
    try:
        launcher_pid = int(_decode_windows(launch_raw).strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise BridgeError("could not identify the original launcher process; see private capture") from exc
    (capture / "launcher-pid.txt").write_text(str(launcher_pid) + "\n", encoding="ascii")

    process_id: int | None = None
    deadline = time.monotonic() + min(timeout, 90)
    process_poll = 0
    while time.monotonic() < deadline:
        processes = _xedit_processes(binary, capture, f"processes-startup-{process_poll:02d}")
        new = [item for item in processes if int(item["Id"]) not in before]
        if new:
            process_id = int(new[-1]["Id"])
            break
        process_poll += 1
        time.sleep(2)
    if process_id is None:
        raise BridgeError("the original launcher started but no new SSEEdit process appeared within 90 seconds")
    (capture / "xedit-pid.txt").write_text(str(process_id) + "\n", encoding="ascii")

    status_script = bridge / "scripts" / "xedit-status.ps1"
    export_hotkey = bridge / "scripts" / "xedit-export-hotkey.ps1"

    def read_status(label: str) -> tuple[dict[str, object], list[str]]:
        raw = _powershell_file(binary, status_script, ["-ProcessId", str(process_id)], capture, label)
        (capture / f"{label}.json.utf8").write_text(_decode_windows(raw), encoding="utf-8")
        return _parse_ui_status(raw)

    # Dismiss only the three explicitly named first-run/module dialogs handled
    # by the recovered source controller. Never click an unknown dialog.
    deadline = time.monotonic() + min(timeout, 300)
    n = 0
    while time.monotonic() < deadline:
        status, names = read_status(f"status-{n:02d}")
        joined = "\n".join(names).casefold()
        action: str | None = None
        if "what's new?" in joined:
            action = "-DismissWhatsNew"
        elif "a message from the developer" in joined:
            action = "-DismissDeveloperMessage"
        elif "module selection" in joined:
            # Verify the session list immediately before confirming it.
            validate_official_plugin_list((session / "plugins.txt").read_text(encoding="utf-8"))
            action = "-ConfirmModuleSelection"
        if action:
            _powershell_file(binary, status_script, ["-ProcessId", str(process_id), action], capture, f"dialog{n:02d}")
            time.sleep(2)
            n += 1
            continue
        if "background loader: finished" in joined:
            load_status = "Background Loader: finished"
            break
        n += 1
        time.sleep(5)
    else:
        raise BridgeError("SSEView did not finish loading the isolated official masters before the configured timeout")
    (capture / "load-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")

    _powershell_file(binary, export_hotkey, ["-ProcessId", str(process_id)], capture, "native-export-hotkey")
    deadline = time.monotonic() + timeout
    stable_size: int | None = None
    stable_checks = 0
    while time.monotonic() < deadline:
        if script_status.is_file():
            status_values = {}
            for line in script_status.read_text(encoding="cp1252", errors="replace").splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    status_values[key.strip()] = value.strip()
            if status_values.get("status") != "PASS":
                detail = ", ".join(f"{key}={value}" for key, value in sorted(status_values.items()))
                raise BridgeError(
                    f"native Apply Script reported {detail or 'an empty status'}; "
                    f"loaded-file inventory is {loaded_files.relative_to(root)}"
                )
        if output.is_file():
            size = output.stat().st_size
            if size > 0 and size == stable_size:
                stable_checks += 1
                if stable_checks >= 2:
                    break
            else:
                stable_size, stable_checks = size, 0
        time.sleep(2)
    if not output.is_file() or output.stat().st_size == 0:
        try:
            _, names = read_status("status-after-export")
            (capture / "export-status.txt").write_text("\n".join(names), encoding="utf-8")
        except BridgeError:
            pass
        raise BridgeError("xEdit did not produce the native record export; inspect the private status capture")

    raw_tsv = output.read_bytes()
    (capture / "native-records.tsv").write_bytes(raw_tsv)
    text = raw_tsv.decode("cp1252", errors="replace")
    parsed = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    required_columns = {"source_plugin", "form_id", "editor_id", "signature", "winning_plugin", "field_path", "value", "links_to"}
    if not parsed or not required_columns.issubset(parsed[0]):
        raise BridgeError("native xEdit TSV has no data rows or the expected original field schema")
    identities = {
        (row["source_plugin"], row["form_id"], row["editor_id"], row["signature"], row["winning_plugin"])
        for row in parsed
    }
    if len(identities) != 1:
        raise BridgeError("native xEdit export contains multiple or inconsistent record identities")
    source_plugin, form_id, actual_editor_id, actual_signature, winning_plugin = next(iter(identities))
    if source_plugin.casefold() != plugin.casefold() or actual_editor_id.casefold() != editor_id.casefold() or actual_signature != signature:
        raise BridgeError("native xEdit export identity does not match the requested record")
    loaded_files_names = tuple(
        line.strip() for line in loaded_files.read_text(encoding="cp1252", errors="replace").splitlines() if line.strip()
    )
    loaded_plugins = tuple(name for name in loaded_files_names if name.casefold() != "skyrimse.exe")
    if loaded_plugins != OFFICIAL_PLUGINS:
        raise BridgeError(
            "native xEdit loaded-file inventory does not match the five configured official masters: "
            + ", ".join(loaded_plugins)
        )
    for source_file in overlay_manifest["source_files"]:
        source_path = source_data / str(source_file["name"])
        if _sha256_file(source_path) != source_file["sha256"]:
            raise BridgeError(f"configured game data changed during native xEdit query: {source_file['name']}")
    record = {
        "source_plugin": source_plugin,
        "form_id": form_id,
        "editor_id": actual_editor_id,
        "signature": actual_signature,
        "winning_plugin_within_official_five_master_scope": winning_plugin,
    }
    structured = {
        "route": "native SSEView -view + original hotkey Apply Script field walker",
        "query": {"plugin": plugin, "signature": signature, "editor_id": editor_id},
        "plugins": list(setup["plugins"]),
        "loaded_files": list(loaded_files_names),
        "loader_status": load_status,
        "native_data_overlay": str(data_overlay.relative_to(root)),
        "native_data_files": overlay_manifest["source_files"],
        "record": record,
        "field_count": len(parsed),
        "fields": parsed,
        "tsv_sha256": hashlib.sha256(raw_tsv).hexdigest(),
        "source_files_sha256": hashes,
        "native_script_sha256": setup["manifest"]["native_script_sha256"],
        "raw_tsv": str(output.relative_to(root)),
        "capture": str(capture.relative_to(root)),
        "mo2_required": False,
        "effective_profile_override_resolution": "not established; only five official masters loaded",
    }
    structured_path = session / "native-result.json"
    structured_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    (capture / "native-result.json").write_text(structured_path.read_text(encoding="utf-8"), encoding="utf-8")

    # Record a small local receipt for the non-launching consolidated doctor.
    receipt = {
        "status": "PASS",
        "record": record,
        "plugins": list(setup["plugins"]),
        "loaded_files": list(loaded_files_names),
        "loader_status": load_status,
        "native_data_overlay": str(data_overlay.relative_to(root)),
        "native_data_files": overlay_manifest["source_files"],
        "tsv": str(output.relative_to(root)),
        "tsv_sha256": structured["tsv_sha256"],
        "result_json": str(structured_path.relative_to(root)),
        "result_json_sha256": hashlib.sha256(structured_path.read_bytes()).hexdigest(),
        "source_files_sha256": hashes,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    }
    receipt_dir = root / ".local" / "xedit-native"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / "latest.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    if not keep_open:
        close_script = (
            "$p=Get-Process -Id " + str(process_id) + " -ErrorAction Stop; "
            "if ($p.ProcessName -ne 'SSEEdit' -or $p.MainWindowTitle -notlike 'SSEView *') { throw 'Unexpected xEdit process' }; "
            "$null=$p.CloseMainWindow(); Start-Sleep -Seconds 2; "
            "if (Get-Process -Id " + str(process_id) + " -ErrorAction SilentlyContinue) { 'still-open' } else { 'closed' }"
        )
        close_result = _powershell_script(binary, close_script, capture, "close-after-export")
        receipt["process_after_export"] = _decode_windows(close_result).strip()
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    samples = []
    for row in parsed:
        path = row["field_path"]
        if any(token in path.casefold() for token in ("stages", "ctda", "conditions")):
            samples.append({"field_path": path, "value": row["value"], "links_to": row["links_to"]})
        if len(samples) >= 16:
            break
    return {
        "ok": True,
        "command": "native-query",
        "route": structured["route"],
        "session": str(session.relative_to(root)),
        "process_id": process_id,
        "loader_status": load_status,
        "plugins": list(setup["plugins"]),
        "loaded_files": list(loaded_files_names),
        "record": record,
        "field_count": len(parsed),
        "field_samples": samples,
        "native_tsv": str(output.relative_to(root)),
        "native_tsv_sha256": structured["tsv_sha256"],
        "structured_result": str(structured_path.relative_to(root)),
        "receipt": str(receipt_path.relative_to(root)),
        "capture": str(capture.relative_to(root)),
        "mo2_required": False,
        "effective_profile_override_resolution": "not established; only official masters loaded",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor", help="sync the configured helper into ignored .local and check bindings")
    subs.add_parser("prepare", help="prepare a scoped five-master SSEView -view session; does not launch it")
    records = subs.add_parser("file-records", help="read records directly from plugin bytes; this does not invoke xEdit")
    records.add_argument("--signature", required=True)
    records.add_argument("--editor-id", help="case-insensitive substring")
    records.add_argument("--form-id", help="plugin-local 6-digit object ID")
    records.add_argument("--plugin", action="append", choices=OFFICIAL_PLUGINS)
    native = subs.add_parser(
        "native-query",
        help="launch isolated five-master SSEView and export one named record through the original Apply Script workflow",
    )
    native.add_argument("--signature", required=True)
    native.add_argument("--plugin", required=True, choices=OFFICIAL_PLUGINS)
    native.add_argument("--editor-id", required=True)
    native.add_argument("--timeout", type=int, default=900, help="maximum loader/export wait in seconds")
    native.add_argument("--keep-open", action="store_true", help="leave the completed SSEView window open")
    args = parser.parse_args(argv)
    try:
        bridge, hashes = materialize()
        if args.command == "doctor":
            summary = _doctor(ROOT, bridge, hashes)
        elif args.command == "prepare":
            overlay, overlay_manifest = configure_official_helper_data(ROOT, bridge)
            summary = _prepare(ROOT, bridge, hashes, data_overlay=overlay)
            summary["native_data_files"] = overlay_manifest["source_files"]
        elif args.command == "native-query":
            if args.timeout < 30:
                raise BridgeError("--timeout must be at least 30 seconds")
            summary = _native_query(
                ROOT, bridge, hashes,
                plugin=args.plugin,
                signature=args.signature.upper(),
                editor_id=args.editor_id,
                timeout=args.timeout,
                keep_open=args.keep_open,
            )
        else:
            command = ["records", "--signature", args.signature]
            if args.editor_id:
                command.extend(("--editor-id", args.editor_id))
            if args.form_id:
                command.extend(("--form-id", args.form_id))
            for plugin in args.plugin or []:
                command.extend(("--plugin", plugin))
            result, capture = invoke_helper(bridge, command)
            summary = _safe_result("file-records", result, capture, hashes)
            summary["query_route"] = "direct read-only TES4 file parser; not xEdit"
            if result.stdout:
                summary["record_count"] = sum(1 for line in result.stdout.splitlines() if line.strip())
                summary["records_jsonl"] = result.stdout
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        if args.command == "native-query":
            return 0 if summary.get("ok") else 1
        return 0 if summary.get("exit_code") == 0 and summary.get("configured_inputs_exist", True) else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
