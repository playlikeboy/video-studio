import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class ProjectExamplesTests(unittest.TestCase):
    def test_presets_are_valid_objects(self):
        files = list((ROOT / "presets").glob("*.json"))
        self.assertGreaterEqual(len(files), 1)
        for path in files:
            with self.subTest(path=path.name):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_project_example_has_schema_version(self):
        data = json.loads((ROOT / "examples/project.json").read_text(encoding="utf-8"))
        self.assertEqual(data.get("schemaVersion"), "1.0.0")
        self.assertIn("sources", data)
        self.assertIn("tracks", data)

if __name__ == "__main__":
    unittest.main()
