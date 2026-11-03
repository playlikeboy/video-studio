import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowSecurityTests(unittest.TestCase):
    def test_every_external_action_uses_a_full_commit_sha(self):
        workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        self.assertTrue(workflows, "expected GitHub Actions workflows")
        checked = 0
        for path in workflows:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "uses:" not in line:
                    continue
                self.assertRegex(line, r"^\s*(?:-\s*)?uses:\s*")
                value = line.split("uses:", 1)[1].split("#", 1)[0].strip()
                if value.startswith("./"):
                    continue
                self.assertRegex(
                    value,
                    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-f]{40}$",
                    f"{path.relative_to(ROOT)}:{line_number} must pin an action to a full commit SHA",
                )
                comment = line.split("#", 1)[1].strip() if "#" in line else ""
                self.assertRegex(comment, r"^v\d+(?:\.\d+){0,2}$", f"{path}:{line_number} should retain a readable version comment")
                checked += 1
        self.assertGreater(checked, 0, "expected at least one external action reference")

    def test_workflows_use_an_explicit_ubuntu_lts_runner(self):
        workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        checked = 0
        for path in workflows:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "runs-on:" not in line:
                    continue
                self.assertRegex(line, r"^\s*runs-on:\s*ubuntu-\d{2}\.\d{2}$", f"{path.relative_to(ROOT)}:{line_number} must use an explicit Ubuntu LTS label")
                checked += 1
        self.assertGreater(checked, 0, "expected at least one explicit runner image")

    def test_dependabot_updates_github_actions_weekly(self):
        config = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("package-ecosystem: github-actions", config)
        self.assertRegex(config, r"interval:\s*weekly")

    def test_security_policy_explains_action_pinning(self):
        policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("full 40-character commit SHA", policy)
        self.assertIn("must not be auto-merged", policy)


if __name__ == "__main__":
    unittest.main()
