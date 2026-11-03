import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.install import ALL_TOOLS, ask_yes_no, copy_skill, install_hyperframes, install_selected_tools, parse_tools, skill_destination


class InstallerTests(unittest.TestCase):
    def test_copy_preserves_unrelated_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            (source / "references").mkdir(parents=True)
            (source / "SKILL.md").write_text("original", encoding="utf-8")
            (source / "references" / "guide.md").write_text("guide", encoding="utf-8")
            target = root / "target"
            target.mkdir()
            (target / "notes.md").write_text("keep", encoding="utf-8")
            self.assertTrue(copy_skill(source, target, update=True))
            self.assertEqual((target / "SKILL.md").read_text(), "original")
            self.assertEqual((target / "references" / "guide.md").read_text(), "guide")
            self.assertEqual((target / "notes.md").read_text(), "keep")

    def test_existing_skill_is_untouched_without_update_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = root / "source", root / "target"
            source.mkdir(); target.mkdir()
            (source / "SKILL.md").write_text("new", encoding="utf-8")
            (target / "SKILL.md").write_text("existing", encoding="utf-8")
            self.assertFalse(copy_skill(source, target))
            self.assertEqual((target / "SKILL.md").read_text(), "existing")

    def test_refuses_symlink_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, real, link = root / "source", root / "real", root / "link"
            source.mkdir(); real.mkdir()
            (source / "SKILL.md").write_text("x", encoding="utf-8")
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                copy_skill(source, link)

    def test_refuses_symlinked_parent_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, trusted, outside = root / "source", root / "trusted", root / "outside"
            source.mkdir(); trusted.mkdir(); outside.mkdir()
            (source / "SKILL.md").write_text("x", encoding="utf-8")
            (trusted / ".claude").symlink_to(outside, target_is_directory=True)
            target = trusted / ".claude" / "skills" / "video-studio"
            with self.assertRaisesRegex(ValueError, "symlink"):
                copy_skill(source, target, trusted_root=trusted)

    def test_refuses_symlink_inside_existing_skill_on_update(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = root / "source", root / "target"
            source.mkdir(); target.mkdir()
            (source / "SKILL.md").write_text("new", encoding="utf-8")
            outside = root / "outside.txt"
            outside.write_text("do not touch", encoding="utf-8")
            (target / "linked.md").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "symlink"):
                copy_skill(source, target, update=True, trusted_root=root)
            self.assertEqual(outside.read_text(encoding="utf-8"), "do not touch")

    def test_refuses_destination_outside_trusted_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, trusted, outside = root / "source", root / "trusted", root / "outside"
            source.mkdir(); trusted.mkdir(); outside.mkdir()
            (source / "SKILL.md").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside"):
                copy_skill(source, outside / "video-studio", trusted_root=trusted)

    def test_optional_tool_failure_is_reported(self):
        def fake_installer(name, scope, home, dry_run):
            return name == "fablecut"
        failures = install_selected_tools(
            {"hyperframes", "fablecut"},
            "user",
            Path("/tmp/home"),
            installer=fake_installer,
        )
        self.assertEqual(failures, ["hyperframes"])

    def test_hyperframes_reuses_marketplace_at_selected_scope(self):
        calls = []
        existing = '[{"repo":"heygen-com/hyperframes","scope":"user"}]'
        with patch("scripts.install.shutil.which", return_value="/usr/bin/claude"), \
             patch("scripts.install.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=existing, stderr="")), \
             patch("scripts.install.run_command", side_effect=lambda command, dry_run=False: calls.append(command) or True):
            self.assertTrue(install_hyperframes("user"))
        self.assertEqual(calls, [
            ["claude", "plugin", "install", "hyperframes@hyperframes", "--scope", "user"],
        ])

    def test_project_optional_tools_run_from_selected_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            original = Path.cwd()
            def fake_installer(name, scope, home, dry_run):
                self.assertEqual(Path.cwd(), project)
                return True
            failures = install_selected_tools(
                {"fablecut"}, "project", Path("/tmp/home"),
                installer=fake_installer, project_dir=project,
            )
            self.assertEqual(failures, [])
            self.assertEqual(Path.cwd(), original)

    def test_hyperframes_uses_official_claude_plugin_commands(self):
        calls = []
        with patch("scripts.install.shutil.which", return_value="/usr/bin/claude"), \
             patch("scripts.install.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="[]", stderr="")), \
             patch("scripts.install.run_command", side_effect=lambda command, dry_run=False: calls.append(command) or True):
            self.assertTrue(install_hyperframes("project"))
        self.assertEqual(calls, [
            ["claude", "plugin", "marketplace", "add", "heygen-com/hyperframes", "--scope", "project"],
            ["claude", "plugin", "install", "hyperframes@hyperframes", "--scope", "project"],
        ])

    def test_optional_tool_selection(self):
        self.assertEqual(parse_tools("hyperframes,ffmpeg-skill"), {"hyperframes", "ffmpeg-skill"})
        self.assertEqual(parse_tools("all"), set(ALL_TOOLS))
        self.assertEqual(parse_tools(None), set())
        with self.assertRaisesRegex(ValueError, "Unknown"):
            parse_tools("made-up-editor")

    def test_prompts_default_to_no(self):
        self.assertFalse(ask_yes_no("Install?", input_fn=lambda _: ""))
        self.assertFalse(ask_yes_no("Install?", input_fn=lambda _: "n"))
        self.assertTrue(ask_yes_no("Install?", input_fn=lambda _: "yes"))

    def test_personal_and_project_locations(self):
        home, project = Path("/tmp/home"), Path("/tmp/project")
        self.assertEqual(skill_destination("user", home, project), home / ".claude/skills/video-studio")
        self.assertEqual(skill_destination("project", home, project), project / ".claude/skills/video-studio")


if __name__ == "__main__":
    unittest.main()
