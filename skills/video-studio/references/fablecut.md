# FableCut integration

Use FableCut as an optional, local, human-in-the-loop nonlinear editor. It exposes a JSON timeline through an MCP server and a browser UI that live-updates as edits are applied.

## Discover before use

1. Confirm the FableCut MCP server is installed and available; do not install it without user approval.
2. Call `fablecut_docs` for the installed version's schemas, supported operations and recipes.
3. Call `fablecut_status`, then inspect the current project with `fablecut_get_project`.
4. Use `fablecut_frame` for visual inspection when selecting footage or reviewing the composed timeline.

Do not assume that the upstream tool list or JSON schema is unchanged. Use the installed tool descriptions as the contract.

## Editing pattern

- Prefer `fablecut_patch_project` for small, typed operations such as split, ripple delete, trim, insert, overwrite, crossfade, caption or effect updates.
- Avoid replacing the entire project with `fablecut_set_project` unless a full project rewrite is necessary and the user understands the scope.
- Respect project revision checks. On a conflict, fetch the latest project, compare the human's changes and retry only the intended patch.
- Keep the browser preview open for human review. Ask before exporting when the brief does not clearly request a final render.
- Use `fablecut_export` for the editor's export path, then verify the resulting file with FFprobe and representative frame/audio checks.

## Recent upstream capabilities

FableCut v1.18.0 (released 2026-10-27) adds a beat grid with marker, snap and re-cut operations; subject-follow reframing for 9:16, 1:1 and 4:5 sequences; and short highlight assembly from longer footage. It also makes external agent edits their own undo step and refuses an edit if the project file cannot be read immediately before saving. See the [v1.18.0 release notes](https://github.com/ronak-create/FableCut/releases/tag/v1.18.0). These are upstream capabilities: call `fablecut_docs` to confirm the installed MCP schema before use.

## Security and privacy

- Keep the server bound to loopback (`127.0.0.1`). Never expose the REST API to the public internet.
- Do not enable LAN binding unless the user explicitly asks and configures the documented allowlist.
- Ask before using URL import, downloading optional model assets, or enabling any feature that sends data outside the local machine.
- FableCut requires Node.js 18+ and a Chromium-based browser; FFmpeg is optional but recommended for fast export. Do not install dependencies automatically.
- Keep source media in the user's chosen data directory. Preserve originals and do not delete or overwrite project assets without permission.

## Choose the right tool

- Use FFmpeg / ffmpeg-skill for direct file-level operations and efficient stream-copy cuts when valid.
- Use FableCut for visible timeline editing and interactive review.
- Use HyperFrames for HTML/CSS/GSAP motion graphics.
- Use Remotion only for React-driven compositions when its current license permits the use case.
