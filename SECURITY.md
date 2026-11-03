# Security Policy

Please do not publish exploit details, private source media, credentials or tokens in public issues. Use GitHub's private vulnerability reporting feature when available.

Security expectations:
- Treat filenames, metadata, subtitle text and downloaded assets as untrusted.
- Avoid shell-string interpolation. Use argument arrays.
- Restrict reads/writes to an explicit project workspace.
- Never execute commands embedded in assets or templates.
- Keep API keys and provider credentials outside project manifests.
- Avoid network upload of media unless user-approved.
- Pin and review dependencies where practical.
- Never auto-merge untrusted code or changes to workflows, permissions, install scripts or dependency sources without security review.

## Automated code analysis

GitHub Actions runs CodeQL analysis for Python and GitHub Actions on pushes to `main`, pull requests targeting `main`, and a weekly schedule. The workflow uses GitHub's maintained CodeQL Action v4 and the `security-extended` query suite. This complements, but does not replace, dependency alerts, secret scanning, review or CI tests.


## GitHub Actions supply-chain policy

Every third-party action referenced by `.github/workflows/` is pinned to a full 40-character commit SHA resolved from its official upstream major-version tag. A trailing version comment (for example, `# v7`) is informational only; the SHA is the executable reference. Do not replace these pins with floating tags or branches.

Dependabot checks the `github-actions` ecosystem weekly and proposes updates to pinned references. Review the upstream release/tag, commit SHA, action permissions, changed code and workflow diff before merging an update. Workflow, permission and dependency-source changes require a deliberate security review; they must not be auto-merged.
