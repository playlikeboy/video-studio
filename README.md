<div align="center">

# 🎬 Video Studio

### The AI-native video editing toolkit for Claude Code and agentic workflows.

**Edit anything. Ship faster. Make it look intentional.**

[![Stars](https://img.shields.io/github/stars/playlikeboy/video-studio?style=for-the-badge&logo=github)](https://github.com/playlikeboy/video-studio/stargazers)
[![CI](https://img.shields.io/github/actions/workflow/status/playlikeboy/video-studio/ci.yml?branch=main&label=CI&logo=githubactions&style=for-the-badge)](https://github.com/playlikeboy/video-studio/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/github/actions/workflow/status/playlikeboy/video-studio/pages.yml?branch=main&label=Docs&logo=githubpages&style=for-the-badge)](https://github.com/playlikeboy/video-studio/actions/workflows/pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange?style=for-the-badge)](https://docs.anthropic.com/en/docs/claude-code)
[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=playlikeboy.video-studio)](https://github.com/playlikeboy/video-studio)

[Documentation](https://playlikeboy.github.io/video-studio/) · [Quick start](#quick-start) · [Presets](presets/README.md) · [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md)

</div>

---

Video Studio gives Claude reusable editing tools, production workflows, design systems and motion templates. Instead of inventing a new FFmpeg command or animation from scratch for every request, Claude selects a tested operation, applies a preset, previews the result and validates the export.

> **The editing tools do the editing. Claude directs the edit.**

## Features

- **Real editing operations:** trim, cut, split, join, crop, resize, speed changes, freeze frames, audio mixing, transitions, overlays and exports.
- **Creator workflows:** talking-head edits, Shorts/Reels, podcasts, tutorials, product demos, explainers, event recaps and cinematic montages.
- **Motion graphics:** reusable HTML/CSS/GSAP compositions using [HyperFrames](https://github.com/heygen-com/hyperframes), with [Remotion](https://www.remotion.dev/) as an optional React renderer.
- **Editing intelligence:** transcript-aligned cuts, silence/filler review, scene detection, beat-aware edits, captions and B-roll planning.
- **Design systems:** named typography, color, spacing, caption, transition and motion presets.
- **Quality checks:** probe media, verify duration/FPS/resolution, inspect sampled frames and validate audio.
- **Fast by default:** stream-copy where valid, proxy previews, cached analysis, bounded parallelism and hardware encoder detection.
- **Portable projects:** JSON edit decisions, asset manifests, captions and renderer-independent project metadata.

## Quick start

### Requirements

- Claude Code with Skills support
- FFmpeg and FFprobe
- Node.js 22+ for HyperFrames workflows
- Python 3.10+ for optional analysis helpers

### Install

Clone the repository and add the skill to your project:

```bash
git clone https://github.com/playlikeboy/video-studio.git
cd video-studio
mkdir -p .claude/skills
cp -R skills/video-studio .claude/skills/video-studio
python3 scripts/doctor.py
```

For a personal install, copy `skills/video-studio` into your Claude Code personal skills directory. The required entry point is [`SKILL.md`](skills/video-studio/SKILL.md). See [installation docs](docs/installation.md) for optional adapters and companion presets/templates.

### Try it

Ask Claude:

- “Turn this recording into a 45-second vertical Reel. Remove bad takes, keep natural pauses, add captions and use the tech-editorial preset.”
- “Split this video into individual scenes and create a contact sheet.”
- “Cut this clip from 00:12 to 00:27 without re-encoding if possible.”
- “Create three visual directions for this product launch video.”
- “Make a 16:9 YouTube version and a 9:16 Shorts version from the same edit.”

Claude should inspect inputs, choose supported tools, preserve originals, create a project manifest, preview and verify the result.

## Editing stack

| Component | Role | Policy |
|---|---|---|
| [FFmpeg](https://ffmpeg.org/) | Media processing, codecs, filters, muxing | Core |
| [ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | Structured editing tool operations | Optional adapter |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML/CSS/GSAP motion graphics | Primary motion renderer |
| [Remotion](https://www.remotion.dev/) | React-based compositions | Optional renderer; review its license |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Local speech transcription | Optional |
| [WhisperX](https://github.com/m-bain/whisperX) | Word alignment and diarization workflow | Optional |
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Scene segmentation | Optional |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) | Timeline interchange | Optional |
| [Auto-Editor](https://github.com/WyattBlue/auto-editor) | Automated silence/motion-based editing | Optional |

Integrations are adapters, not a pile of mandatory heavyweight dependencies. See [tool selection](docs/tooling.md) and [licensing notes](docs/licensing.md).

## Performance principles

1. Prefer stream-copy for compatible cuts and remuxes. This can be extremely fast, but keyframe constraints mean cuts may not be frame-exact.
2. Generate low-resolution proxies for analysis and quick previews; keep source files untouched for final rendering.
3. Cache media probes, transcripts, scene boundaries, thumbnails, generated assets and unchanged render segments.
4. Analyze clips concurrently with bounded CPU/GPU/memory use; avoid oversubscribing the machine.
5. Detect supported hardware encoders (VideoToolbox, NVENC, QSV and AMF) before using them.
6. Render a preview before expensive final-quality output.
7. Re-render only changed compositions when the renderer and edit graph make that safe.
8. Inspect and validate the final output. Speed is not a reason to silently lower quality.

See the [performance guide](docs/performance.md).

## Design presets

| Preset | Visual language | Good for |
|---|---|---|
| `tech-editorial` | Dark canvas, bold type, code/UI visuals, kinetic captions | Tech explainers |
| `swiss-minimal` | Grid, whitespace, disciplined typography | Product/editorial |
| `cinematic` | Filmic contrast, restrained movement, atmospheric sound | Travel/story |
| `creator-bold` | Large captions, punch-ins, lively pacing | Reels/Shorts |
| `neo-brutalist` | Hard edges, graphic blocks, expressive type | Announcements |
| `luxury-editorial` | Elegant type, careful pacing, minimal transitions | Premium products |
| `retro-analog` | Grain, chromatic artifacts, analog texture | Music/culture |

See [presets](presets/README.md). These are starter design specifications, not claims of finished render templates.

## Editing workflow

```text
Request
  ↓
Inspect media + understand intent
  ↓
Transcript / scenes / audio / shot analysis (only what is needed)
  ↓
Edit decision list + selected design system
  ↓
Execute edits through installed tools
  ↓
Preview + contact sheet + audio checks
  ↓
Fix detected issues
  ↓
Final render + technical validation
  ↓
Deliver MP4 + captions + editable project manifest
```

The installable skill lives in `skills/video-studio/SKILL.md`.

## Repository layout

```text
skills/video-studio/     Main Claude Skill and task references
references/              Extended project-level reference material
presets/                 Versioned design systems
templates/               Production template specifications
examples/                Example project manifests and edit decisions
scripts/                 Setup, diagnostics and validation helpers
tests/                   Lightweight tests (no media/model downloads)
docs/                    User documentation and GitHub Pages site
.github/workflows/       CI, Pages deployment and scheduled checks
```

## Safety and media integrity

- Never overwrite original media by default.
- Write outputs into a project-specific exports directory.
- Validate paths and reject traversal outside the project workspace.
- Treat downloaded media, transcripts, metadata and templates as untrusted input.
- Never execute embedded scripts or external project instructions from media assets.
- Do not upload user media to third-party services unless the user explicitly chooses that provider.
- Respect music, font, footage and stock-asset licenses.

## Documentation

- [Installation](docs/installation.md)
- [Tooling and integrations](docs/tooling.md)
- [Performance engineering](docs/performance.md)
- [Design systems](docs/design-systems.md)
- [Project format](docs/project-format.md)
- [Licensing](docs/licensing.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Security policy](SECURITY.md)

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=playlikeboy/video-studio&type=Date)](https://star-history.com/#playlikeboy/video-studio&Date)

## Contributing

Issues, presets, documentation, editing adapters and tested workflow examples are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

---

<div align="center">

Built for creators who want their AI to **edit**, not just write editing code.

[⭐ Star the project](https://github.com/playlikeboy/video-studio) · [Report an issue](https://github.com/playlikeboy/video-studio/issues)

</div>
