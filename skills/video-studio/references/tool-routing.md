# Tool routing and integration strategy

## Objective

Choose an available, reliable tool instead of building a one-off editing implementation. Discover installed capabilities at runtime; this document is not a guarantee that every integration is installed.

## Preferred routing

| Need | Preferred tool | Fallback |
|---|---|---|
| Probe streams | ffprobe | media inspection adapter |
| Cut/remux | FFmpeg stream-copy | structured ffmpeg-skill operation |
| Filter/composite | FFmpeg | renderer-specific pipeline |
| Batch editing tools | ffmpeg-skill adapter | direct CLI |
| HTML/CSS motion graphics | HyperFrames | Remotion/static composition |
| React-native compositions | Remotion | HyperFrames |
| Transcribe | faster-whisper | installed provider |
| Word alignment | WhisperX | transcript timestamps |
| Scene detection | PySceneDetect | FFmpeg scene filter |
| Timeline exchange | OpenTimelineIO | project JSON / EDL |

## Existing integrations to evaluate

- ffmpeg-skill: https://github.com/kajisho5/ffmpeg-skill
- HyperFrames: https://github.com/heygen-com/hyperframes
- Remotion: https://github.com/remotion-dev/remotion
- video-use: https://github.com/browser-use/video-use
- video-agent: https://github.com/agamm/video-agent
- PySceneDetect: https://github.com/Breakthrough/PySceneDetect
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- WhisperX: https://github.com/m-bain/whisperX
- OpenTimelineIO: https://github.com/AcademySoftwareFoundation/OpenTimelineIO
- Auto-Editor: https://github.com/WyattBlue/auto-editor

## Tool discovery checklist

1. Check command existence with `command -v`.
2. Check CLI version and `--help`.
3. Check MCP server/tool list and exact input schema when applicable.
4. Verify local executable and model availability.
5. Verify licensing, supported OS, maintenance state and transitive dependencies.
6. Run a tiny test on synthetic media before using a tool on user content.
7. Record capability status in a diagnostics report.

FFmpeg is the default media engine. HyperFrames is the default HTML/CSS motion engine. Remotion is optional for React compositions. Do not make both renderers mandatory. Do not install several speech models by default.

Optional AI providers must be explicit opt-ins. Keep the core useful offline. Make network transfer visible and user-controlled.
