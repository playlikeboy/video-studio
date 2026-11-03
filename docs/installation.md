# Installation

## Claude Code

Clone the repository and copy the Skill into your project:

```bash
git clone https://github.com/playlikeboy/video-studio.git
cd video-studio
mkdir -p .claude/skills
cp -R skills/video-studio .claude/skills/video-studio
```

The copied Skill is self-contained: `SKILL.md` and all task-specific guides travel together in `references/`. It does not need the repository-level `docs/` or `scripts/` directories at runtime.

For a personal install, copy `skills/video-studio` to your Claude Code personal skills directory; follow the current Claude Code documentation for the supported location.

### Optional companion assets

The repository-level `presets/` and `templates/` directories are optional. If you want those starter design systems and production blueprints in another project, copy them to that project's root. The Skill remains usable without them.

## Core binaries

Install FFmpeg/FFprobe from the official distribution for your operating system, then check:

```bash
ffmpeg -version
ffprobe -version
```

From a full Video Studio repository checkout, run the optional environment diagnostic:

```bash
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

For an existing HyperFrames project, open its local preview with `npx hyperframes preview` from that project folder. Remotion is optional for React-based compositions; read its current license and pricing before commercial, team or automated-product use.

## Optional interactive timeline editor: FableCut

FableCut provides a local browser timeline that agents can control through MCP. With user approval, register the upstream server in Claude Code:

```bash
claude mcp add -s user fablecut -- npx -y fablecut mcp
```

Start the browser editor when needed:

```bash
npx -y fablecut
```

It requires Node.js 18+ and a Chromium-based browser. FFmpeg is optional but recommended for faster export and remuxing. The server binds to loopback by default; do not expose it publicly. See [the FableCut integration guide](fablecut.md) for project-revision, remote-media and model-download boundaries.

## Optional analysis tools

Install faster-whisper, WhisperX, PySceneDetect, OpenTimelineIO or Auto-Editor only when a workflow needs their specific capability. Speech models can be large and may have terms separate from their Python package. Check disk, memory, hardware and model licenses before downloading weights.
