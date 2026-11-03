# HyperFrames integration

HyperFrames is the preferred renderer for HTML/CSS/GSAP motion graphics.

Repository: https://github.com/heygen-com/hyperframes

Use cases: kinetic typography, animated captions/lower-thirds, product UI mockups, code/browser demos, charts, diagrams, transitions and explainer sequences.

## Agent workflow
1. Check HyperFrames installation and version.
2. Read installed skill/reference documentation and CLI help.
3. Inspect available blocks/catalog before inventing a component.
4. Select one composition template and one design system.
5. Keep timeline and asset references in the project.
6. Run native preview/check commands.
7. Render a low-resolution test.
8. Inspect frames and timing.
9. Render final output and validate with FFprobe.

## Performance
Prefer simple DOM/CSS/GSAP elements over expensive WebGL when visual quality is comparable. Avoid unnecessary filters, full-screen blur and huge textures. Reuse static assets and compositions. Keep render dimensions/FPS at delivery requirements only for final export. Use proxy preview settings during iteration.

Do not assume a particular CLI command or block API from memory. Read the installed version's skill files and help output.
## Upstream release snapshot

HyperFrames v0.9.7 was released on 2026-11-03. Recent fixes improve preview/export frame alignment, WebGL motion-blur playback, media fallback and concurrent export isolation. Review the [v0.9.7 release notes](https://github.com/heygen-com/hyperframes/releases/tag/v0.9.7) and the installed skill/CLI help before relying on a specific option.

