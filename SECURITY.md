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
