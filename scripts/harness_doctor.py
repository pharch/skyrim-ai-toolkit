#!/usr/bin/env python3
"""Run a non-mutating, privacy-preserving cold-start readiness audit.

The doctor may write raw subprocess captures and one JSON summary below ignored
.local/alignment/harness-doctor/. It never deploys Observer, launches Skyrim or
SSEView, or performs xEdit record selection. Ghidra is queried only through the
read-only adapter after the repository venv and build identity checks pass.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import parse_local_config, read_local_config
from scripts.python_env import environment_status, external_binding_status, venv_python
from tools.ae_target import _native_path


def _safe_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _capture(
    label: str,
    argv: list[str],
    capture_dir: Path,
    *,
    timeout: int = 120,
) -> tuple[dict[str, Any], subprocess.CompletedProcess[str] | None]:
    """Run one known local check, store raw output privately, return safe metadata."""
    try:
        result = subprocess.run(
            argv, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False,
        )
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
        completed: subprocess.CompletedProcess[str] | None = result
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code, completed = _safe_text(exc.stdout), _safe_text(exc.stderr), 124, None
    except OSError as exc:
        stdout, stderr, code, completed = "", f"{type(exc).__name__}: command could not start", 127, None

    stdout_path = capture_dir / f"{label}.stdout.raw"
    stderr_path = capture_dir / f"{label}.stderr.raw"
    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    record: dict[str, Any] = {
        "exit_code": code,
        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
        "raw_stdout": str(stdout_path.relative_to(ROOT)),
        "raw_stderr": str(stderr_path.relative_to(ROOT)),
    }
    return record, completed


def _status_for_failure(stderr: str, stdout: str = "") -> str:
    text = (stderr + "\n" + stdout).casefold()
    if any(token in text for token in (
        "productversion", "powershell", "windows process", "wsl", "not accessible",
        "repository .venv is incomplete", "fail_venv_missing",
    )):
        return "BLOCKED_EXTERNAL"
    return "FAIL"


def _check(label: str, status: str, summary: str, **metadata: Any) -> dict[str, Any]:
    return {"id": label, "status": status, "summary": summary, **metadata}


def _configuration_status(root: Path = ROOT) -> tuple[str, dict[str, Any]]:
    path = root / "config" / "local.env"
    example = root / "config" / "local.env.example"
    if not path.is_file():
        return "FAIL", {"present": False, "valid": False, "schema_matches": False, "git_ignored": False}
    try:
        actual = read_local_config(root)
        expected = parse_local_config(example.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "FAIL", {"present": True, "valid": False, "schema_matches": False, "git_ignored": False}
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "config/local.env"],
        cwd=root, capture_output=True, check=False,
    ).returncode == 0
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    schema_matches = not missing and not extra
    return (
        "PASS" if ignored and schema_matches else "FAIL",
        {
            "present": True,
            "valid": True,
            "schema_matches": schema_matches,
            "git_ignored": ignored,
            "missing_keys": missing,
            "unexpected_keys": extra,
            "external_bindings": external_binding_status(actual),
        },
    )


def _run_local(
    label: str,
    argv: list[str],
    capture_dir: Path,
    checks: list[dict[str, Any]],
    *,
    timeout: int = 120,
) -> tuple[str, str, str, dict[str, Any]]:
    raw, result = _capture(label, argv, capture_dir, timeout=timeout)
    code = int(raw["exit_code"])
    if result is None:
        stdout = (capture_dir / f"{label}.stdout.raw").read_text(encoding="utf-8")
        stderr = (capture_dir / f"{label}.stderr.raw").read_text(encoding="utf-8")
    else:
        stdout, stderr = result.stdout, result.stderr
    status = "PASS" if code == 0 else _status_for_failure(stderr, stdout)
    checks.append(_check(label, status, "exit status recorded; raw output is private under .local",
                         **raw))
    return status, stdout, stderr, raw


def _run_dispatched(
    label: str,
    tool_args: list[str],
    capture_dir: Path,
    checks: list[dict[str, Any]],
    *,
    timeout: int = 650,
) -> tuple[str, str, str, dict[str, Any]]:
    argv = [sys.executable, "scripts/python_env.py", "run", *tool_args]
    return _run_local(label, argv, capture_dir, checks, timeout=timeout)


def _stage_status(config: dict[str, str]) -> dict[str, Any]:
    value = config.get("SKYRIM_OBSERVER_STAGED_DLL", "").strip()
    result: dict[str, Any] = {"configured": bool(value), "exists": False, "size_bytes": None, "sha256": None}
    if not value:
        return result
    try:
        path = _native_path(value)
        if path.is_file():
            data = path.read_bytes()
            result.update({"exists": True, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    except OSError:
        pass
    return result


def _mode_has(mode: str, capability: str) -> bool:
    return mode == "all" or mode == capability


def _overall_exit(checks: list[dict[str, Any]]) -> int:
    statuses = {entry.get("status") for entry in checks}
    if "FAIL" in statuses:
        return 1
    if "BLOCKED_EXTERNAL" in statuses:
        return 2
    return 0


def _base_checks(
    mode: str,
    capture_dir: Path,
    checks: list[dict[str, Any]],
    interpreter: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    python = environment_status(ROOT)
    python_status = "PASS" if python.get("ready") else "BLOCKED_EXTERNAL"
    checks.append(_check(
        "python_environment", python_status,
        str(python.get("python_status")),
        python_status=python.get("python_status"),
        python_required=python.get("python_required"),
        venv_present=python.get("venv_present"),
        dependency_failures=python.get("dependency_failures", []),
        config_present=python.get("config_present"),
        config_valid=python.get("config_valid"),
    ))
    config_status, config_details = _configuration_status(ROOT)
    checks.append(_check("local_config", config_status, "schema, parser, and ignore status checked without values",
                         **config_details))

    # These local validators can still report their results when the strict
    # research venv is absent. Their execution never opens native applications.
    local_interpreter = interpreter
    for label, args in (
        ("research_state_validation", ["scripts/research_state.py", "validate"]),
        ("setup_state_check", ["scripts/setup_research.py", "check"]),
        ("research_validation", ["scripts/validate_research.py"]),
        ("overlay_validation", ["scripts/validate_overlay.py"]),
        ("local_paths_doctor", ["scripts/local_paths.py", "doctor"]),
        ("domain_doctor", ["tools/domain_doctor.py"]),
        ("markdown_policy", ["scripts/markdown_policy_audit.py", "--check"]),
        ("pre_push_audit", ["scripts/pre_push_audit.py"]),
        ("python_compileall", ["-m", "compileall", "-q", "scripts", "tools", "tests"]),
        ("unit_tests", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
    ):
        status, _, _, _ = _run_local(label, [local_interpreter, *args], capture_dir, checks, timeout=300)
    return python, config_details.get("external_bindings", {})


def _static_checks(
    capture_dir: Path,
    checks: list[dict[str, Any]],
    python: dict[str, Any],
) -> None:
    if not python.get("ready"):
        checks.append(_check(
            "gog_read_only_query", "BLOCKED_EXTERNAL",
            "strict repository venv is unavailable; native static query was not dispatched",
        ))
        return
    status, stdout, stderr, raw = _run_dispatched(
        "gog_address_library", ["tools/address_library_probe.py", "--symbol", "MagicItem::CalculateCost"],
        capture_dir, checks,
    )
    if status != "PASS":
        checks[-1]["status"] = _status_for_failure(stderr, stdout)
        checks[-1]["summary"] = "GOG identity/Address Library lookup did not pass"
        checks.append(_check(
            "gog_read_only_query", "BLOCKED_EXTERNAL",
            "Ghidra was not launched because build identity or Address Library verification failed",
        ))
        return
    try:
        mapping = json.loads(stdout)
        rva = str(mapping["address_library_rva"])
    except (json.JSONDecodeError, KeyError, TypeError):
        checks[-1]["status"] = "FAIL"
        checks[-1]["summary"] = "Address Library output did not contain a verified RVA"
        checks.append(_check("gog_read_only_query", "FAIL", "no verified RVA was available"))
        return
    status, stdout, stderr, raw = _run_dispatched(
        "gog_ghidra_read_only",
        ["tools/ghidra_probe.py", "--rva", rva, "--timeout", "600"],
        capture_dir, checks, timeout=650,
    )
    if status != "PASS":
        checks[-1]["status"] = _status_for_failure(stderr, stdout)
        checks[-1]["summary"] = "existing-project query did not complete"
    else:
        checks[-1]["summary"] = "existing GOG project queried with the read-only adapter"
        checks[-1]["rva"] = rva


def _record_checks(
    capture_dir: Path,
    checks: list[dict[str, Any]],
    python: dict[str, Any],
    bindings: dict[str, Any],
) -> None:
    if not python.get("ready"):
        checks.append(_check("xedit_helper", "BLOCKED_EXTERNAL",
                             "strict repository venv is unavailable; helper was not dispatched"))
        checks.append(_check("tes4_file_record_query", "BLOCKED_EXTERNAL",
                             "strict repository venv is unavailable; file parser was not dispatched"))
    else:
        status, stdout, stderr, _ = _run_dispatched(
            "xedit_helper_doctor", ["tools/xedit_bridge.py", "doctor"], capture_dir, checks,
        )
        if status == "PASS":
            try:
                helper = json.loads(stdout)
                if not helper.get("configured_inputs_exist"):
                    checks[-1]["status"] = "FAIL"
                    checks[-1]["summary"] = "one or more helper inputs are unavailable"
                else:
                    checks[-1]["summary"] = "authoritative helper bindings are available; no native launch occurred"
            except json.JSONDecodeError:
                checks[-1]["status"] = "FAIL"
                checks[-1]["summary"] = "helper doctor returned invalid JSON"
        else:
            checks[-1]["summary"] = "helper doctor did not pass"

        if checks[-1].get("status") == "PASS":
            status, stdout, stderr, _ = _run_dispatched(
                "tes4_file_record_query",
                ["tools/xedit_bridge.py", "file-records", "--signature", "QUST",
                 "--plugin", "Skyrim.esm", "--editor-id", "CreatureDialogueWerewolf"],
                capture_dir, checks,
            )
            if status == "PASS":
                try:
                    query = json.loads(stdout)
                    if query.get("query_route") != "direct read-only TES4 file parser; not xEdit" or query.get("record_count") != 1:
                        checks[-1]["status"] = "FAIL"
                    checks[-1]["summary"] = "one QUST record read from plugin bytes; this is not native xEdit"
                    checks[-1]["record_count"] = query.get("record_count")
                    checks[-1]["query_route"] = query.get("query_route")
                except json.JSONDecodeError:
                    checks[-1]["status"] = "FAIL"
                    checks[-1]["summary"] = "file parser returned invalid JSON"
            else:
                checks[-1]["summary"] = "file parser query did not complete"

            # A native export remains a separate manual interface. The safe
            # preparation route is still worth validating independently.

        status, stdout, stderr, _ = _run_dispatched(
            "xedit_view_prepare", ["tools/xedit_bridge.py", "prepare"], capture_dir, checks,
        )
        if status == "PASS":
            try:
                prepared = json.loads(stdout)
                if not prepared.get("prepared") or prepared.get("native_launch_requested") is not False:
                    checks[-1]["status"] = "FAIL"
                    checks[-1]["summary"] = "view preparation did not remain prepare-only"
                else:
                    checks[-1]["summary"] = "scoped five-master view session prepared; no native launch requested"
                    checks[-1]["plugins"] = prepared.get("plugins", [])
            except json.JSONDecodeError:
                checks[-1]["status"] = "FAIL"
                checks[-1]["summary"] = "view preparation returned invalid JSON"

    if not bindings.get("selected_profile_configured"):
        detail = "selected MO2 profile directory and explicit plugins.txt are not both configured"
    else:
        detail = "doctor does not automate safe SSEView record selection or Apply Script export"
    checks.append(_check("native_xedit_record_export", "BLOCKED_EXTERNAL", detail))


def _live_checks(
    capture_dir: Path,
    checks: list[dict[str, Any]],
    python: dict[str, Any],
    bindings: dict[str, Any],
    config: dict[str, str],
) -> None:
    stage = _stage_status(config)
    checks.append(_check(
        "observer_staged_artifact", "PASS" if stage["exists"] else "BLOCKED_EXTERNAL",
        "staged file metadata only; deployment/load/connection are not implied",
        **stage,
    ))
    if python.get("ready"):
        status, stdout, stderr, _ = _run_dispatched(
            "skse_installed_identity", ["tools/skse_probe.py"], capture_dir, checks, timeout=90,
        )
        if status != "PASS":
            checks[-1]["status"] = _status_for_failure(stderr, stdout)
            checks[-1]["summary"] = "installed identity probe did not verify the executable/runtime"
        else:
            checks[-1]["summary"] = "installed file identity verified; no live connection was attempted"
    else:
        checks.append(_check("skse_installed_identity", "BLOCKED_EXTERNAL",
                             "strict repository venv is unavailable; identity probe was not dispatched"))

    if not bindings.get("live_bindings_configured"):
        detail = "deployed DLL, disposable profile/plugins.txt, save, or observer log directory is unbound"
    else:
        detail = "doctor does not launch Skyrim or claim an Observer handshake/snapshot"
    checks.append(_check(
        "skse_live_observation", "BLOCKED_EXTERNAL",
        detail,
        game_process="not_probed",
        observer_loaded="not_probed",
        handshake="not_observed",
        snapshot="not_observed",
        devbench_connection="not_attempted",
    ))


def run_doctor(mode: str = "all", root: Path = ROOT) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    capture_dir = root / ".local" / "alignment" / "harness-doctor" / stamp
    capture_dir.mkdir(parents=True, exist_ok=False)
    python_status = environment_status(root)
    interpreter_path = venv_python(root) if python_status.get("ready") else Path(sys.executable)
    checks: list[dict[str, Any]] = []
    python, bindings = _base_checks(mode, capture_dir, checks, str(interpreter_path))
    try:
        config = read_local_config(root)
    except (OSError, ValueError):
        config = {}

    if _mode_has(mode, "static"):
        _static_checks(capture_dir, checks, python)
    if _mode_has(mode, "records"):
        _record_checks(capture_dir, checks, python, bindings)
    if _mode_has(mode, "live"):
        _live_checks(capture_dir, checks, python, bindings, config)

    code = _overall_exit(checks)
    verdict = "READY" if code == 0 else ("FAIL" if code == 1 else "BLOCKED")
    report = {
        "schema_version": 1,
        "mode": mode,
        "verdict": verdict,
        "ready": code == 0,
        "exit_code": code,
        "runtime_scope": "Skyrim AE only",
        "native_launches_requested": [],
        "mutation_scope": "writes only private diagnostic captures below ignored .local",
        "checks": checks,
        "artifact_directory": str(capture_dir.relative_to(root)),
    }
    (capture_dir / "harness_doctor.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=("all", "static", "records", "live"), default="all")
    args = parser.parse_args(argv)
    report = run_doctor(args.mode)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())

