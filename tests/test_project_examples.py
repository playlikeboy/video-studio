import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_assets import validate_preset, validate_project, validate_skill  # noqa: E402


class ProjectExamplesTests(unittest.TestCase):
    def test_all_presets_match_their_file_names_and_schema(self):
        files = sorted((ROOT / "presets").glob("*.json"))
        self.assertGreaterEqual(len(files), 1)
        for path in files:
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                validate_preset(path, data)

    def test_project_example_matches_manifest_contract(self):
        data = json.loads((ROOT / "examples/project.json").read_text(encoding="utf-8"))
        validate_project(data)

    def test_project_rejects_path_traversal(self):
        data = json.loads((ROOT / "examples/project.json").read_text(encoding="utf-8"))
        data["sources"][0]["path"] = "../../outside.mp4"
        with self.assertRaisesRegex(ValueError, "safe relative path"):
            validate_project(data)

    def test_project_rejects_unknown_source_reference(self):
        data = json.loads((ROOT / "examples/project.json").read_text(encoding="utf-8"))
        data["tracks"][0]["clips"][0]["sourceId"] = "missing-source"
        with self.assertRaisesRegex(ValueError, "unknown source"):
            validate_project(data)

    def test_project_rejects_non_positive_speed(self):
        data = json.loads((ROOT / "examples/project.json").read_text(encoding="utf-8"))
        data["tracks"][0]["clips"][0]["speed"] = 0
        with self.assertRaisesRegex(ValueError, "speed must be positive"):
            validate_project(data)

    def test_skill_has_valid_frontmatter_and_body(self):
        validate_skill(ROOT / "skills/video-studio" / "SKILL.md")

    def test_skill_reference_guides_exist(self):
        content = (ROOT / "skills/video-studio" / "SKILL.md").read_text(encoding="utf-8")
        references = set(re.findall(r"(references/[A-Za-z0-9_-]+\.md)", content))
        self.assertTrue(references)
        for reference in references:
            with self.subTest(reference=reference):
                self.assertTrue((ROOT / "skills/video-studio" / reference).is_file())


if __name__ == "__main__":
    unittest.main()
