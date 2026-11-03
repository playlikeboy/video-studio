# Contributing

Thanks for helping make Video Studio better.

Good contributions include tested editing adapters, reusable presets/templates, measurable performance improvements, caption/audio workflows, docs/examples and compatibility fixes.

## Before opening a PR
1. Search existing issues and PRs.
2. Keep the change focused.
3. Document tool requirements and license.
4. Do not add large media, model files, secrets or private assets.
5. Run `python3 scripts/validate_assets.py` and `python3 -m unittest discover -s tests -v`.
6. Include before/after examples for visual changes where possible.

PRs should explain intent, behavior, tradeoffs and verification. Maintainers review security, quality, CI and licensing before merge. No PR is merged merely because it was opened.
