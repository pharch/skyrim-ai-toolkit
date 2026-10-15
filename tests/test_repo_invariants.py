"""Cross-file invariants for the Codex-first Skyrim AE research checkout."""

from __future__ import annotations

import re
import unittest

from conftest import REPO
from scripts.validate_overlay import _validate_markdown_links, _validate_python_tool_surface


class RepositoryInvariantTests(unittest.TestCase):
    def test_ci_uses_python_test_runner_and_declares_pytest_in_dev_requirements(self):
        workflow = (REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        requirements = (REPO / "requirements-dev.txt").read_text(encoding="utf-8")
        self.assertIn("python -m pytest -q", workflow)
        self.assertRegex(requirements, r"(?im)^pytest==[0-9][^\s]*$")
        self.assertIn("-r requirements.txt", requirements)
        self.assertNotRegex(workflow, r"(?i)setup-node|npm test|node --test")

    def test_python_tool_surface_has_only_the_native_ghidra_payload_exception(self):
        self.assertEqual(_validate_python_tool_surface(REPO), [])

    def test_no_legacy_claude_or_game_installer_is_active(self):
        for relative in (".claude", "CLAUDE.md", "SETUP_PROMPT.txt", "setup.sh", ".devcontainer"):
            self.assertFalse((REPO / relative).exists(), f"obsolete active surface remains: {relative}")

    def test_codex_skill_discovery_files_match_names_and_have_no_claude_paths(self):
        skills = sorted((REPO / ".agents/skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 10)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                text = skill.read_text(encoding="utf-8")
                match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(match, skill)
                assert match is not None
                name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", match.group(1), re.M)
                description = re.search(r"^description:\s*(.{40,})$", match.group(1), re.M)
                self.assertIsNotNone(name, skill)
                self.assertEqual(name.group(1) if name else None, skill.parent.name)
                self.assertIsNotNone(description, skill)
                self.assertIsNone(re.search(r"^paths:", match.group(1), re.M), skill)
                self.assertGreaterEqual(len(re.findall(r"\b[\w'-]+\b", text[match.end():])), 120, skill)

    def test_active_codex_config_has_no_live_mcp_or_provider_hook(self):
        text = (REPO / ".codex/config.toml").read_text(encoding="utf-8")
        self.assertIn('approval_policy = "on-request"', text)
        self.assertIn('sandbox_mode = "workspace-write"', text)
        self.assertNotIn("mcp_servers", text)
        self.assertNotIn("[features]", text)

    def test_active_docs_have_no_broken_relative_links(self):
        self.assertEqual(_validate_markdown_links(REPO), [])
