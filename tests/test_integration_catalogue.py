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
        self.assertIn("v0.5.6", tooling)
        self.assertIn("LGPL-2.1", licensing)
        self.assertIn("GPL-3.0", licensing)
        self.assertIn("Settings → Agent", guide)
        self.assertIn("2026-10-31", guide)
        self.assertIn("preview-scale reader", guide)
        self.assertIn("LGPL-only", guide)
        self.assertIn("process for encoding/transcoding", guide)
        self.assertIn("v0.5.6", site)
        self.assertIn("blob/main/docs/weftcut.md", site)
        self.assertIn("weftcut", package["keywords"])


    def test_current_upstream_release_snapshot_is_consistent(self):
        tooling = (ROOT / "docs" / "tooling.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("v3.1.1", tooling)
        self.assertIn("v0.9.8", tooling)
        self.assertIn("v1.18.0", tooling)
        self.assertIn("WeftCut v0.5.6", tooling)
        self.assertIn("WeftCut v0.5.6", readme)
        self.assertIn("WeftCut v0.5.6", changelog)
        self.assertIn("HyperFrames v0.9.8", readme)
        self.assertIn("HyperFrames v0.9.8", changelog)
        self.assertNotIn("HyperFrames v0.9.7", changelog)

    def test_openchatcut_is_documented_as_a_manual_external_application(self):
        paths = [
            ROOT / "README.md",
            ROOT / "docs" / "tooling.md",
            ROOT / "docs" / "licensing.md",
            ROOT / "docs" / "openchatcut.md",
            ROOT / "docs" / "index.html",
        ]
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIn("OpenChatCut", path.read_text(encoding="utf-8"))
        self.assertNotIn("openchatcut", {name.lower() for name in TOOLS})
        guide = (ROOT / "docs" / "openchatcut.md").read_text(encoding="utf-8")
        self.assertIn("not a Video Studio adapter", guide)
        self.assertIn("AGPL-3.0-or-later", guide)

    def test_openchatcut_manual_approval_and_license_boundaries_are_visible(self):
        guide = (ROOT / "docs" / "openchatcut.md").read_text(encoding="utf-8")
        licensing = (ROOT / "docs" / "licensing.md").read_text(encoding="utf-8")
        site = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertIn("v0.2.17", guide)
        self.assertIn("begin_edit_session", guide)
        self.assertIn("review_edit_session", guide)
        self.assertIn("AGENT_IMPORT_ROOTS", guide)
        self.assertIn("unrestricted directory access", guide)
        self.assertIn("26 specialized skills", guide)
        self.assertIn("claude mcp add --transport http", guide)
        self.assertIn("[mcp_servers.openchatcut]", guide)
        self.assertIn("localhost:5199", guide)
        self.assertIn("GPL-3.0-only", guide)
        self.assertIn("AGPL-3.0-or-later", licensing)
        self.assertIn("blob/main/docs/openchatcut.md", site)
        self.assertIn("openchatcut", package["keywords"])

    def test_earshot_installs_from_a_pinned_github_commit_not_pypi(self):
        label, kind, spec = TOOLS["earshot"]
        self.assertEqual(kind, "python")
        self.assertRegex(spec, r"^earshot @ git\+https://github\.com/Leonxlnx/earshot@[0-9a-f]{40}$")
        self.assertIn("MIT", label)

    def test_sound_design_credits_its_three_references(self):
        guide = (ROOT / "skills" / "video-studio" / "references" / "sound-design.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills" / "video-studio" / "SKILL.md").read_text(encoding="utf-8")
        licensing = (ROOT / "docs" / "licensing.md").read_text(encoding="utf-8")
        for name, url in (("earshot", "github.com/Leonxlnx/earshot"),
                          ("Clipwing", "github.com/Clipwing/skills"),
                          ("Openverse", "github.com/WordPress/openverse")):
            with self.subTest(name=name):
                self.assertIn(url, guide)
                self.assertIn(url, licensing)
        self.assertIn("references/sound-design.md", skill)
        self.assertIn("scripts/sound_design.py", skill)
        self.assertIn("not from PyPI", skill)
        self.assertTrue((ROOT / "skills" / "video-studio" / "scripts" / "sound_design.py").is_file())


if __name__ == "__main__":
    unittest.main()
