# Installation

## Claude Code

Clone the repository and copy the skill into your project:

```bash
git clone https://github.com/playlikeboy/video-studio.git
cd video-studio
mkdir -p .claude/skills
cp -R skills/video-studio .claude/skills/video-studio
```

For personal use, copy `skills/video-studio` to your Claude Code personal skills directory. See the current Claude Code documentation for supported skill discovery paths.

## Core binaries

Install FFmpeg/FFprobe from the official distribution for your OS, then check:

```bash
ffmpeg -version
ffprobe -version
python3 scripts/doctor.py
```

## Optional renderers and analysis

HyperFrames and Remotion are optional. Follow their current official setup instructions and review licenses before commercial use. Install speech/scene tools only when needed; model downloads can be large, so check disk, memory and hardware first.
