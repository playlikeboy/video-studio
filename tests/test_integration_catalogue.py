import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.install import TOOLS


class IntegrationCatalogueTests(unittest.TestCase):
    def test_weftcut_is_documented_as_a_manual_external_application(self):
        paths = [
            ROOT / "README.md",
            ROOT / "docs" / "tooling.md",
            ROOT / "docs" / "licensing.md",
            ROOT / "docs" / "weftcut.md",
            ROOT / "docs" / "index.html",
        ]
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIn("WeftCut", path.read_text(encoding="utf-8"))
        self.assertNotIn("weftcut", {name.lower() for name in TOOLS})
        self.assertIn("not part of Video Studio's installer", (ROOT / "docs" / "weftcut.md").read_text(encoding="utf-8"))

    def test_weftcut_release_and_ffmpeg_license_boundary_are_visible(self):
        tooling = (ROOT / "docs" / "tooling.md").read_text(encoding="utf-8")
        licensing = (ROOT / "docs" / "licensing.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "weftcut.md").read_text(encoding="utf-8")
        site = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertIn("v0.5.4", tooling)
        self.assertIn("LGPL-2.1", licensing)
        self.assertIn("GPL-3.0", licensing)
        self.assertIn("Settings → Agent", guide)
        self.assertIn("v0.5.4", site)
        self.assertIn("weftcut", package["keywords"])


if __name__ == "__main__":
    unittest.main()
