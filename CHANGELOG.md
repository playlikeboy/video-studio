# Changelog

## Unreleased
- Fix FableCut MCP registration to honor the selected user or project scope, with regression coverage for both commands and manual fallback guidance.
- Document MakeMyClip Editor as an experimental local-first candidate, including its Node 24+ requirement, pre-1.0 status and bundled GPL FFmpeg binary caveat.
- Harden Skill installation against symlinked destination ancestors and symlinks inside existing installs.
- Report optional integration installation failures with a non-zero exit status instead of silently claiming success.
- Fix HyperFrames installation to use the official Claude Code plugin marketplace flow, honor the selected project directory/scope, and refresh the upstream release snapshot to v0.9.8.
- Use Claude Code's idempotent marketplace registration instead of assuming scope metadata in CLI JSON output.
- Clarify Remotion Free License versus Company License / Automators eligibility and add Windows PowerShell install commands.
- Document media-analysis-skill v0.1.7 as an experimental MIT companion rather than an untested default dependency.
- Add a cross-platform interactive installer with individual opt-in prompts for optional editing and analysis tools.
- Add an integrations picker, copyable commands and OS-specific FFmpeg setup guidance to the Pages site.
- Expand installation docs with safe non-interactive setup, isolated Python environments and third-party licensing boundaries.
- Add scheduled and pull-request CodeQL static analysis for Python and GitHub Actions.
- Make the copied Claude Skill self-contained by moving operational guidance to bundled references and clarifying optional repository-level companion assets.
- Add a regression test that prevents repository-relative paths from breaking downstream Skill installations.
- Refresh the upstream integration snapshot to ffmpeg-skill v3.1.1, HyperFrames v0.9.7 and FableCut v1.18.0, with verified release notes and license boundaries.
- Document FableCut's latest beat-grid, subject-follow reframe and highlight capabilities.
- Keep the hourly repository integrity workflow aligned with CI by running unit tests and Python compilation.

## 0.1.0
- Add optional FableCut local MCP timeline-editor guidance, including loopback, media-import and model-download safety boundaries.
- Add a regression test that verifies every reference guide linked by the Claude Skill exists.
- Add the Claude Code `SKILL.md` entry point and validate its frontmatter.
- Add structural validation for presets and project manifests, with regression tests for unsafe paths and unknown source references.
- Add Python-version CI, GitHub Pages deployment and weekly GitHub Actions dependency updates.
- Complete the MIT license text and document current third-party integration license boundaries.
- Add the initial Video Studio Claude Skill architecture.
- Document editing, renderer, audio, caption and quality-control workflows.
- Add seven starter design-system presets and four creator-oriented template specifications.
- Add the GitHub Pages documentation site and project governance.
