# Installation

Video Studio has a lightweight core and optional adapters. Install the existing Claude Skill first, then add only the editors and analysis tools your workflow actually needs.

## Interactive installer (recommended)

Requirements: Python 3.10+ and a local checkout. The installer uses only the Python standard library.

    git clone https://github.com/playlikeboy/video-studio.git
    cd video-studio
    python3 scripts/install.py

Choose a personal installation (available across Claude Code projects) or a project-only installation in the current directory. The installer copies only the existing skills/video-studio/ folder.

It then checks whether FFmpeg and FFprobe are available and asks separately about optional integrations. Every optional prompt defaults to No. Press Enter to keep the original Video Studio Skill-only setup. The installer does not rewrite the source Skill, remove files, install optional tools without approval or overwrite an existing installation unless you approve an update.

## Non-interactive commands

Install the core Skill with safe defaults:

    python3 scripts/install.py --yes

Preview actions without changing your machine:

    python3 scripts/install.py --dry-run

Select optional integrations explicitly:

    python3 scripts/install.py --with-tools ffmpeg-skill,hyperframes,pyscenedetect

The supported names are: ffmpeg-skill, hyperframes, fablecut, remotion, faster-whisper, whisperx, pyscenedetect, opentimelineio and auto-editor. Use --with-tools all only when you intentionally want every integration. You can also choose a project target:

    python3 scripts/install.py --scope project --project-dir /path/to/project --with-tools ffmpeg-skill

## Core media dependency: FFmpeg

FFmpeg and FFprobe power the core media workflows. The installer checks for them but never installs operating-system packages silently.

macOS (Homebrew):

    brew install ffmpeg

Debian / Ubuntu:

    sudo apt install ffmpeg

Fedora (with an FFmpeg-enabled repository configured):

    sudo dnf install ffmpeg

Windows:

    winget install ffmpeg

Verify:

    ffmpeg -version
    ffprobe -version

Build configurations may include different codecs and libraries. Review your FFmpeg build and codec licensing before redistribution.

## Optional integrations

All optional integrations are individually prompted. They are not required to use the base Skill.

| Tool | Adds | Runtime and license notes |
|---|---|---|
| ffmpeg-skill | Structured local FFmpeg tools and MCP | MIT; Node/npm |
| HyperFrames | HTML/CSS/GSAP motion graphics, preview and agent skill | Apache-2.0; Node.js 22+ and FFmpeg |
| FableCut | Local browser timeline editor and MCP | MIT; Node.js 18+ and Chromium; local server defaults to loopback |
| Remotion | React-authored video composition starter | Separate Remotion License; confirm current individual/team/company eligibility before use |
| faster-whisper | Local speech transcription | MIT; model files download on first use |
| WhisperX | Word alignment and diarization | Large PyTorch/model stack; GPU/model terms vary |
| PySceneDetect | Scene detection | BSD-3-Clause; installer uses the headless package |
| OpenTimelineIO | Timeline interchange | Review current upstream dependencies and notices |
| Auto-Editor | Silence/activity rough cuts | Homebrew, yay or official platform binary |

### What the installer does

- ffmpeg-skill: runs npx --yes ffmpeg-skill. Project installs pass the project-scope flag.
- HyperFrames: installs the CLI with npm and then installs its Claude skill. It requires Node.js 22+.
- FableCut: registers its MCP server in the user-level Claude Code configuration. It does not expose the editor to your LAN.
- Remotion: scaffolds a separate video-studio-remotion folder in your home directory and refuses to overwrite an existing folder.
- Python tools: each gets a separate virtual environment under your user data directory. WhisperX can require several gigabytes once dependencies and model weights are included.
- Auto-Editor: uses Homebrew or yay when available; otherwise it prints links to the official platform binaries.

No speech models, fonts, music, stock footage or media are downloaded by the base installer. Model weights are downloaded only when a selected speech tool is subsequently used.

## Manual Skill-only installation

You can still copy the Skill by hand.

Personal install:

    mkdir -p ~/.claude/skills
    cp -R skills/video-studio ~/.claude/skills/video-studio

Project-only install:

    mkdir -p /path/to/project/.claude/skills
    cp -R skills/video-studio /path/to/project/.claude/skills/video-studio

Validate a full repository checkout:

    npm run check
    python3 scripts/doctor.py

For current Skill discovery behavior, see the official Claude Code Skills documentation:
https://docs.anthropic.com/en/docs/claude-code/skills
