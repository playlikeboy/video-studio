# Tooling and integrations

Video Studio is an orchestration skill, not a monolithic editor. Tools are selected per task.

## Core
- FFmpeg/FFprobe: media inspection, cut/trim/mux/filter/encode.
- Python standard library: manifest and diagnostics helpers.

## Optional adapters
- ffmpeg-skill: structured editing tools and MCP workflows.
- HyperFrames: HTML/CSS/GSAP motion graphics.
- Remotion: React-driven compositions.
- faster-whisper / WhisperX: speech transcription and alignment.
- PySceneDetect: shot boundary detection.
- OpenTimelineIO: editorial interchange.
- Auto-Editor: automated silence/motion editing.

## Adapter contract

An adapter declares stable identifier/version, required executable/package, capability list, supported formats, license/source, availability check, dry-run/preview support, failure behavior, and whether operations copy streams or re-encode.

Do not assume integrations are installed. Detect them and report missing optional capabilities without breaking core editing.
