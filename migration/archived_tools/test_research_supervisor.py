from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts import research_supervisor as supervisor


def test_research_supervisor_defaults_to_dry_run(capsys):
    assert supervisor.main([]) == 0
    output = capsys.readouterr().out
    assert "DRY RUN ONLY" in output
    assert "--sandbox workspace-write" in output


def test_bad_codex_command_is_reported_without_fallback(monkeypatch):
    monkeypatch.setattr(supervisor.shutil, "which", lambda _: None)

    try:
        supervisor.main(["--execute"])
    except SystemExit as exc:
        assert "Codex executable is not on PATH" in str(exc)
    else:
        raise AssertionError("missing Codex executable should stop execution")


def test_forced_timeout_terminates_process_and_returns_timeout_code(tmp_path):
    class FakeProcess:
        pid = 12
        returncode = None

        def __init__(self):
            self.calls = 0

        def communicate(self, input=None, timeout=None):
            self.calls += 1
            if timeout is not None:
                raise subprocess.TimeoutExpired("codex", timeout)

    process = FakeProcess()
    stopped = []
    code = supervisor.run_codex_cycle(
        ["codex"], tmp_path, "prompt", 1, None, None,
        popen=lambda *args, **kwargs: process,
        stopper=lambda current: stopped.append(current),
    )

    assert code == 124
    assert stopped == [process]
    assert process.calls == 2


def test_interrupted_cycle_is_recovered_with_explicit_next_action(tmp_path):
    research = tmp_path / "research"
    research.mkdir()
    recovery_path = research / "RECOVERY.json"
    recovery_path.write_text(json.dumps({
        "schema_version": 1,
        "status": "running",
        "session_id": "prior-session",
        "cycle": 3,
        "run_artifacts": "research/supervisor-logs/run3",
    }), encoding="utf-8")
    (research / "SESSION_LOG.md").write_text("# Session Log\n", encoding="utf-8")

    recovered = supervisor.recover_previous(tmp_path)
    saved = json.loads(recovery_path.read_text(encoding="utf-8"))

    assert recovered is not None
    assert saved["status"] == "interrupted"
    assert "Inspect" in saved["resume_action"]
    assert "Recovered interrupted supervisor cycle 3" in (
        research / "SESSION_LOG.md"
    ).read_text(encoding="utf-8")


def test_frontier_snapshot_contains_only_unresolved_questions(tmp_path):
    research = tmp_path / "research"
    research.mkdir()
    (research / "FRONTIER.json").write_text(json.dumps({
        "items": [
            {"id": "Q-0001", "status": "open"},
            {"id": "Q-0002", "status": "resolved"},
            {"id": "Q-0003", "status": "awaiting-user-data"},
        ],
    }), encoding="utf-8")

    assert supervisor.frontier_ids(tmp_path) == ["Q-0001", "Q-0003"]
