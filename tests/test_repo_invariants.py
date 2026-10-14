"""Cross-file invariants for the Codex-first Skyrim AE research checkout."""

from __future__ import annotations

import re
import subprocess

from conftest import REPO
from scripts.validate_overlay import _validate_markdown_links


def test_node_test_command_runs_registered_tests():
    result = subprocess.run(
        ["node", "--test", "--test-reporter=tap"],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    match = re.search(r"^#\s*pass\s+(\d+)", result.stdout, re.M)
    assert match and int(match.group(1)) > 0, result.stdout
    assert not re.search(r"^ok\s+\d+\s+-\s+\S+\.test\.js\s*$", result.stdout, re.M)


def test_no_legacy_claude_or_game_installer_is_active():
    for relative in (".claude", "CLAUDE.md", "SETUP_PROMPT.txt", "setup.sh", ".devcontainer"):
        assert not (REPO / relative).exists(), f"obsolete active surface remains: {relative}"


def test_codex_skill_discovery_files_match_names_and_have_no_claude_paths():
    skills = sorted((REPO / ".agents/skills").glob("*/SKILL.md"))
    assert len(skills) >= 10
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        assert match, skill
        name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", match.group(1), re.M)
        description = re.search(r"^description:\s*(.{40,})$", match.group(1), re.M)
        assert name and name.group(1) == skill.parent.name, skill
        assert description, skill
        assert not re.search(r"^paths:", match.group(1), re.M), skill
        assert len(re.findall(r"\b[\w'-]+\b", text[match.end():])) >= 120, skill


def test_active_codex_config_has_no_live_mcp_or_provider_hook():
    text = (REPO / ".codex/config.toml").read_text(encoding="utf-8")
    assert "approval_policy = \"on-request\"" in text
    assert "sandbox_mode = \"workspace-write\"" in text
    assert "mcp_servers" not in text
    assert "[features]" not in text


def test_active_docs_have_no_broken_relative_links():
    assert not _validate_markdown_links(REPO)
