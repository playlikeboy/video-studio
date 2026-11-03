# Installation

## Claude Code

Clone the repository and copy the skill into your project:

```bash
git clone https://github.com/playlikeboy/video-studio.git
cd video-studio
mkdir -p .claude/skills
cp -R skills/video-studio .claude/skills/video-studio
```

The copied folder must contain `SKILL.md` and its `references/` directory. If you want to use the starter design systems and production blueprints from another project, also copy `presets/` and `templates/` into that project's root. For personal use, copy `skills/video-studio` to your Claude Code personal skills directory; follow the current Claude Code documentation for the supported location.

## Core binaries

Install FFmpeg/FFprobe from the official distribution for your OS, then check:

```bash
ffmpeg -version
ffprobe -version
python3 scripts/doctor.py
```

FFmpeg and FFprobe are the only required media executables. The repository's validation and tests use the Python standard library and do not download models or media.

## Optional editing and motion adapters

Install these only when a project needs them and after reviewing their current license and runtime requirements:

```bash
# Structured local FFmpeg editing skill / MCP tools
npx ffmpeg-skill

# HyperFrames agent skill for HTML/CSS/GSAP motion graphics
npx skills add heygen-com/hyperframes
```

For an existing HyperFrames project, open its local preview with `npx hyperframes preview` from that project folder. Remotion is optional for React-based compositions; read [the current Remotion license](https://www.remotion.dev/docs/license/pricing) before commercial, team or automated-product use.

## Optional analysis tools

Install faster-whisper, WhisperX, PySceneDetect, OpenTimelineIO or Auto-Editor only when a workflow needs their specific capability. Speech models can be large and may have terms separate from the Python package. Check disk, memory, hardware and model licenses before downloading weights.
