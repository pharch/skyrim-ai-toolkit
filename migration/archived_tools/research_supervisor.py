#!/usr/bin/env python3
"""Opt-in bounded Codex cycles with explicit durable checkpoints and recovery."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "research" / "RECOVERY.json"
DURABLE_PATHS = (
    "STATE.md",
    "research/FRONTIER.json",
    "research/EVIDENCE.json",
    "research/CLAIMS.md",
    "research/CONTRADICTIONS.md",
    "research/SESSION_LOG.md",
)
CORE_DURABLE_PATHS = DURABLE_PATHS[:-1]
PROMPT = """Continue the Skyrim AE glitch-research program documented in AGENTS.md.
Read the required state documents. Select a tractable open frontier item with
the highest information gain; prioritize OBJ-1 or OBJ-2. Do not repeat the last
work without a new discriminant. Verify source assumptions, preserve raw output
and provenance, and update relevant evidence/claims/contradictions/frontier,
STATE.md, and research/SESSION_LOG.md with an exact next action.

This cycle is offline-first. Never access a live game, DevBench, external save,
or mutation endpoint. Do not write game/plugin/archive/save files. Treat
diagnostic interventions as non-vanilla evidence. Do not invent results or
upgrade a hypothesis without evidence. Continue on another offline item when
a user test or Windows runtime is unavailable.
"""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def durable_hashes(root: Path = ROOT) -> dict[str, str | None]:
    return {name: digest(root / name) for name in DURABLE_PATHS}


def append_session_log(root: Path, message: str) -> None:
    log = root / "research" / "SESSION_LOG.md"
    with log.open("a", encoding="utf-8") as stream:
        stream.write(f"\n- {utc_now()} — {message}\n")


def frontier_ids(root: Path) -> list[str]:
    data = json.loads((root / "research" / "FRONTIER.json").read_text(encoding="utf-8"))
    return [
        item["id"] for item in data["items"]
        if item.get("status") not in {"resolved"}
    ]


def recover_previous(root: Path = ROOT) -> dict[str, Any] | None:
    recovery_path = root / "research" / "RECOVERY.json"
    if not recovery_path.exists():
        return None
    previous = json.loads(recovery_path.read_text(encoding="utf-8"))
    if previous.get("status") == "running":
        previous["status"] = "interrupted"
        previous["interrupted_detected_at"] = utc_now()
        previous["resume_action"] = (
            "Inspect this run's metadata/stdout/stderr and the durable file diffs; "
            "then use STATE.md and the frontier to continue."
        )
        atomic_json(recovery_path, previous)
        append_session_log(
            root,
            f"Recovered interrupted supervisor cycle {previous.get('cycle')} "
            f"({previous.get('run_artifacts', 'artifacts unknown')}); inspect before resuming.",
        )
    return previous


def build_command() -> list[str]:
    return [
        "codex", "exec", "--sandbox", "workspace-write",
        "--ask-for-approval", "never", "--json", "-",
    ]


def stop_process(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":
        process.kill()
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except ProcessLookupError:
        return
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def run_codex_cycle(
    command: list[str],
    root: Path,
    prompt: str,
    timeout: int,
    stdout: Any,
    stderr: Any,
    *,
    popen=subprocess.Popen,
    stopper=stop_process,
) -> int:
    process = popen(
        command,
        cwd=root,
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=stderr,
        text=True,
        start_new_session=os.name != "nt",
    )
    try:
        process.communicate(input=prompt, timeout=timeout)
        return int(process.returncode)
    except subprocess.TimeoutExpired:
        stopper(process)
        process.communicate()
        return 124
    except KeyboardInterrupt:
        stopper(process)
        process.communicate()
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=float, default=168)
    parser.add_argument("--round-minutes", type=int, default=45)
    parser.add_argument("--max-failures", type=int, default=3)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if args.hours <= 0 or args.round_minutes < 5 or args.max_failures < 1:
        parser.error("hours must be > 0, round-minutes >= 5, and max-failures >= 1")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    command = build_command()
    if not args.execute:
        print("DRY RUN ONLY. Would run:", " ".join(command))
        print("CWD:", ROOT)
        print("The Codex command is bounded and writes only to this checkout sandbox.")
        print("Review docs/WEEK_LONG_OPERATION.md and pass --execute explicitly to run.")
        return 0
    if not shutil.which("codex"):
        raise SystemExit("Codex executable is not on PATH")
    if not (ROOT / "AGENTS.md").is_file():
        raise SystemExit(f"wrong repository root: {ROOT}")

    sys.path.insert(0, str(ROOT / "scripts"))
    from validate_overlay import validate

    failures = validate(ROOT)
    if failures:
        raise SystemExit("Preflight failed; refusing unattended run:\n - " + "\n - ".join(failures))

    lock = ROOT / ".research-supervisor.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SystemExit(f"Lock exists ({lock}); inspect the prior process/recovery state manually") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(f"pid={os.getpid()}\nstarted={utc_now()}\n")

    recovered = recover_previous(ROOT)
    session_id = str(uuid.uuid4())
    logdir = ROOT / "research" / "supervisor-logs"
    logdir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + args.hours * 3600
    failures_in_a_row = 0
    cycle = 0
    status = "completed"
    try:
        while time.monotonic() < deadline and not (ROOT / ".stop-research").exists():
            cycle += 1
            timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            base = logdir / f"{timestamp}-run{cycle:04d}"
            meta_path = Path(f"{base}.meta.json")
            out_path = Path(f"{base}.out.jsonl")
            err_path = Path(f"{base}.err.log")
            before = durable_hashes(ROOT)
            meta: dict[str, Any] = {
                "session_id": session_id,
                "cycle": cycle,
                "started_at": utc_now(),
                "command": command,
                "timeout_minutes": args.round_minutes,
                "frontier_ids_before": frontier_ids(ROOT),
                "input_hashes": before,
                "recovered_previous_session": recovered.get("session_id") if recovered else None,
                "run_artifacts": str(base.relative_to(ROOT)),
            }
            atomic_json(meta_path, meta)
            atomic_json(RECOVERY, {
                "schema_version": 1,
                "status": "running",
                "session_id": session_id,
                "cycle": cycle,
                "started_at": meta["started_at"],
                "frontier_ids": meta["frontier_ids_before"],
                "run_artifacts": str(base.relative_to(ROOT)),
                "next_action": "Inspect this run's results, update the durable research state, then continue from STATE.md.",
            })
            print(f"[{meta['started_at']}] Starting cycle {cycle}", flush=True)
            timeout = min(args.round_minutes * 60, max(1, int(deadline - time.monotonic())))
            try:
                with out_path.open("w", encoding="utf-8") as stdout, err_path.open("w", encoding="utf-8") as stderr:
                    exit_code = run_codex_cycle(command, ROOT, PROMPT, timeout, stdout, stderr)
            except KeyboardInterrupt:
                status = "interrupted"
                atomic_json(RECOVERY, {
                    **json.loads(RECOVERY.read_text(encoding="utf-8")),
                    "status": status,
                    "interrupted_at": utc_now(),
                    "resume_action": "Inspect this cycle's output and durable file diffs before continuing.",
                })
                raise

            after = durable_hashes(ROOT)
            changed = [name for name in DURABLE_PATHS if before.get(name) != after.get(name)]
            core_changed = [name for name in CORE_DURABLE_PATHS if before.get(name) != after.get(name)]
            durable_update = bool(core_changed)
            meta.update({
                "ended_at": utc_now(),
                "exit_code": exit_code,
                "changed_durable_files": changed,
                "changed_core_files": core_changed,
                "durable_update": durable_update,
            })
            from validate_overlay import validate
            validation_errors = validate(ROOT)
            meta["validation_errors"] = validation_errors
            valid_state = not validation_errors
            atomic_json(meta_path, meta)
            success = exit_code == 0 and durable_update and valid_state
            cycle_status = "completed" if success else ("timeout" if exit_code == 124 else "failed")
            atomic_json(RECOVERY, {
                "schema_version": 1,
                "status": cycle_status,
                "session_id": session_id,
                "cycle": cycle,
                "started_at": meta["started_at"],
                "ended_at": meta["ended_at"],
                "exit_code": exit_code,
                "changed_durable_files": changed,
                "frontier_ids": frontier_ids(ROOT),
                "run_artifacts": str(base.relative_to(ROOT)),
                "next_action": "Review run metadata and STATE.md before starting another cycle.",
            })
            append_session_log(
                ROOT,
                f"Supervisor cycle {cycle_status}; exit={exit_code}; "
                f"durable updates={','.join(changed) if changed else 'none'}; "
                f"artifacts={base.relative_to(ROOT)}.",
            )
            if success:
                failures_in_a_row = 0
            else:
                failures_in_a_row += 1
                print(
                    f"Cycle {cycle} {cycle_status}; consecutive failures: {failures_in_a_row}",
                    flush=True,
                )
                if failures_in_a_row >= args.max_failures:
                    status = "failure_limit"
                    break
                time.sleep(10)
    finally:
        lock.unlink(missing_ok=True)

    if status == "completed" and (ROOT / ".stop-research").exists():
        status = "stopped"
    print(f"Supervisor ended; cycles={cycle}, status={status}. Review RECOVERY.json and run logs.")
    return 0 if status in {"completed", "stopped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
