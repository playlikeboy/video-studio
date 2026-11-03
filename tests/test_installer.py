import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.install import ALL_TOOLS, ask_yes_no, copy_skill, parse_tools, skill_destination


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
