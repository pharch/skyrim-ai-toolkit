"""Behavioral tests for tools/devbench-cli.sh against a mock DevBench server.

The exit codes are the contract -- anything scripting this wrapper branches on
them -- so they are asserted, not just the human-readable text.

Why this suite exists: from v3.3 to v3.5.1 `alive` diffed the frame counter
across two `inspect` calls, but every DevBench tool call runs on the game's main
thread and 504s after 5s when that thread is stuck. On a genuine hang the probe
hung too, and the result was indistinguishable from a closed game. The check
failed in precisely the case it existed for, and nothing caught it for three
releases.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from conftest import BASH, REPO

CLI = REPO / "tools" / "devbench-cli.sh"
MOCK = Path(__file__).resolve().parent / "mock_devbench.py"


# Everything devbench-cli.sh shells out to, minus jq. `bash` is here because
# the test itself execs it.
NEEDED = ["bash", "curl", "sed", "head", "tr", "cat", "sleep", "env"]

_nojq_dir: Path | None = None
_preflight_dir: Path | None = None


def _preflight_node() -> str:
    """Stub only the executable gate; AE target behavior is tested separately."""
    global _preflight_dir
    if _preflight_dir is None:
        _preflight_dir = Path(tempfile.mkdtemp(prefix="toolkit-ae-preflight-stub-"))
        script = _preflight_dir / "node"
        script.write_text(
            "#!/bin/sh\n"
            "if [ \"$2\" = \"--game-root\" ]; then printf '%s\\n' \"$TEST_GAME_ROOT\"; fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        script.chmod(0o755)
    return str(_preflight_dir)


def _path_without_jq() -> str:
    """A PATH with everything the script needs except jq.

    Dropping whole PATH entries that contain jq works on Windows, where jq sits
    in its own WinGet/choco directory. It is wrong on Linux: jq lives in
    /usr/bin alongside bash, curl and coreutils, so dropping that directory
    takes the interpreter with it and the run dies with
    "No such file or directory: 'bash'" having tested nothing.
    """
    if os.name == "nt":
        keep = []
        for entry in os.environ.get("PATH", "").split(os.pathsep):
            if not entry:
                continue
            d = Path(entry)
            if (d / "jq").exists() or (d / "jq.exe").exists():
                continue
            keep.append(entry)
        return os.pathsep.join(keep)

    global _nojq_dir
    if _nojq_dir is None:
        _nojq_dir = Path(tempfile.mkdtemp(prefix="toolkit-nojq-"))
        for name in NEEDED:
            real = shutil.which(name)
            if real:
                (_nojq_dir / name).symlink_to(real)
    return str(_nojq_dir)


def held_dead_port():
    """A port guaranteed to refuse connections, held open for the caller.

    Binding without listening is what makes this reliable: the port cannot be
    grabbed by another process while the test runs, and a connect attempt is
    refused rather than accepted. The old "bind port 0, close it, assume it
    stays free" approach was a race that would surface as a spurious failure.
    """
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    return s, s.getsockname()[1]


def _wait_until_listening(port: int, timeout: float = 10.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as s:
            s.settimeout(0.25)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.05)
    return False


class Server:
    def __init__(self, mode: str):
        # Port 0: the server binds, then tells us which port it got. Choosing a
        # port here and hoping it is still free when the child binds it is a
        # race that shows up as an intermittent "never started listening".
        self.proc = subprocess.Popen(
            [sys.executable, str(MOCK), "0", mode],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        )
        line = self.proc.stdout.readline().strip()
        if not line.startswith("PORT="):
            self.stop()
            raise RuntimeError(f"mock server ({mode}) did not announce a port: {line!r}")
        self.port = int(line.split("=", 1)[1])
        if not _wait_until_listening(self.port):
            self.stop()
            raise RuntimeError(f"mock server ({mode}) never started listening")

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


@pytest.fixture
def server(request):
    s = Server(request.param)
    yield s
    s.stop()


def run_cli(*args, port: int, mask_jq: bool = False):
    env = dict(os.environ)
    env["DEVBENCH_PORT"] = str(port)
    env["TEST_GAME_ROOT"] = str(Path(tempfile.gettempdir()) / "skyrim-ae-fixture")
    base_path = _path_without_jq() if mask_jq else env.get("PATH", "")
    env["PATH"] = _preflight_node() + os.pathsep + base_path
    if mask_jq:
        env["PATH"] = _preflight_node() + os.pathsep + _path_without_jq()
        # Prove the mask worked. If jq were still reachable this test would run
        # the jq path and pass while claiming to cover the fallback -- a test
        # that examines nothing must never report success.
        probe = subprocess.run([BASH, "-c", "command -v jq"], env=env,
                               capture_output=True, text=True)
        assert probe.returncode != 0, (
            f"jq still resolvable after masking: {probe.stdout.strip()!r}")
    return subprocess.run(
        [BASH, str(CLI), *args],
        cwd=str(REPO), env=env, capture_output=True, text=True, timeout=120,
    )


# ----------------------------------------------------------------- liveness

@pytest.mark.parametrize("server", ["running"], indirect=True)
def test_running_game_reports_running(server):
    r = run_cli("alive", port=server.port)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUNNING" in r.stdout


@pytest.mark.parametrize("server", ["paused"], indirect=True)
def test_paused_game_is_not_called_a_hang(server):
    """A frozen frame alone is not evidence of a hang -- menus and loading
    screens freeze it too. The old check cried wolf every time."""
    r = run_cli("alive", port=server.port)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "NOT ADVANCING" in r.stdout
    assert "HUNG" not in r.stdout, "a pause was reported as a hang"


@pytest.mark.parametrize("server", ["hung"], indirect=True)
def test_starved_main_thread_is_reported_as_hung(server):
    """Frame frozen AND pendingTasks piling up while lastTaskFrame stalls."""
    r = run_cli("alive", port=server.port)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "HUNG" in r.stdout or "STARVED" in r.stdout


@pytest.mark.parametrize("server", ["notingame"], indirect=True)
def test_no_save_loaded_is_its_own_state(server):
    """frame < 0 means the server is up but nothing is loaded -- distinct from
    both running and hung, and it gets its own exit code."""
    r = run_cli("alive", port=server.port)
    assert r.returncode == 3, r.stdout + r.stderr
    assert "NOT IN GAME" in r.stdout


@pytest.mark.parametrize("server", ["legacy"], indirect=True)
def test_pre_1_11_devbench_is_rejected_without_identity_fields(server):
    r = run_cli("alive", port=server.port)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "predates identity-bearing /api/health" in r.stderr


def test_dead_port_is_distinguishable_from_a_hang():
    """No server at all: exit 1, with the closed-game message."""
    sock, port = held_dead_port()
    try:
        r = run_cli("alive", port=port)
    finally:
        sock.close()
    assert r.returncode == 1
    assert "no response" in (r.stdout + r.stderr).lower()


# ----------------------------------------------------------- HTTP semantics

@pytest.mark.parametrize("server", ["busy504"], indirect=True)
def test_504_is_reported_as_a_busy_main_thread(server):
    """504 means the server is fine and the game is busy. Before v3.5.1 any
    JSON body counted as success and this printed as though it worked."""
    r = run_cli("state", port=server.port)
    assert r.returncode != 0, "a 504 was treated as success"
    assert "504" in r.stderr


@pytest.mark.parametrize("server", ["badarg400"], indirect=True)
def test_400_is_reported_as_a_bad_argument(server):
    r = run_cli("inspect", "vm", port=server.port)
    assert r.returncode != 0, "a 400 was treated as success"
    assert "400" in r.stderr


# ------------------------------------------------------------------- no jq

@pytest.mark.parametrize("server", ["running", "hung", "notingame"], indirect=True)
def test_liveness_still_works_without_jq(server):
    """jget's no-jq branch is hand-rolled sed and is the least-exercised code in
    the script; every verdict must survive losing jq."""
    r = run_cli("alive", port=server.port, mask_jq=True)
    assert "instance:" in r.stdout, r.stdout + r.stderr
    assert r.returncode in (0, 2, 3), f"unexpected exit {r.returncode}"


@pytest.mark.parametrize("server", ["wrongexe"], indirect=True)
def test_live_reads_reject_a_non_ae_devbench_process(server):
    r = run_cli("inspect", "player", port=server.port)
    assert r.returncode == 4, r.stdout + r.stderr
    assert "not verifiably the expected Skyrim AE process" in r.stderr


def test_mutating_devbench_commands_are_not_exposed():
    r = run_cli("exec", "player.kill", port=8920)
    assert r.returncode == 1
    assert "Unknown command: exec" in r.stderr
