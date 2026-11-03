# Tooling and integrations

Video Studio is an orchestration skill, not a monolithic editor. It routes each task to the smallest installed tool that can do the job. This review snapshot was checked on **2026-11-03**; upstream versions, availability and terms can change.

## Core

- **FFmpeg / FFprobe** — media inspection, cut/trim/mux/filter/encode. No Python or Node media package is required by the core project.
- **Python standard library** — diagnostics, JSON asset validation and lightweight project checks.

## Recommended optional adapters

| Tool | Best use | Upstream license / policy | Integration guidance |
|---|---|---|---|
| [ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | Structured FFmpeg editing operations, machine-readable contracts and MCP tools | MIT | Prefer its typed tools when installed instead of duplicating them with shell strings. Its upstream README documents `npx ffmpeg-skill`, `doctor` and `contract --json`. |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | Agent-authored HTML/CSS/GSAP compositions and deterministic video rendering | Apache-2.0 | Primary motion-graphics route. The maintained skill can be added with `npx skills add heygen-com/hyperframes`; preview an existing project with `npx hyperframes preview`. |
| [Remotion](https://github.com/remotion-dev/remotion) | React-authored video compositions | Source-available Remotion License; usage-dependent | Keep optional. The current terms provide a free license for individuals and companies of up to three people; larger companies and automated video products may need paid licensing. Check current terms before commercial or product use. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Local speech-to-text | MIT | Optional model-backed dependency. Install only when transcription is needed; model weights are downloaded separately. |
| [WhisperX](https://github.com/m-bain/whisperX) | Word-level alignment and speaker diarization | BSD-2-Clause | Use only when word timing or diarization materially improves the edit. PyTorch, pyannote and model weights have their own runtime and license terms. |
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Shot/scene boundary detection | BSD-3-Clause | Optional analysis dependency; do not run it when simple sampling is sufficient. |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) | Timeline interchange between editorial tools | Apache-2.0 | Optional interchange layer. OTIO stores editorial structure and media references, not the media files themselves; some adapters are separately packaged. |
| [Auto-Editor](https://github.com/WyattBlue/auto-editor) | Automated silence- or motion-based rough cuts | Unlicense for repository source | Optional rough-cut tool. The upstream project notes that some application assets have separate proprietary terms; do not assume every asset is covered by the source license. |

## Routing rules

- Use FFmpeg or `ffmpeg-skill` for actual media operations. Do not rebuild a tool that already exists and is available.
- Use HyperFrames for HTML-native motion, animated titles, UI demos, diagrams and reusable graphic scenes. Use Remotion only when a React authoring model is a genuine advantage.
- Prefer faster-whisper for straightforward local transcription; add WhisperX only when word alignment or diarization is required.
- Use PySceneDetect for meaningful shot-boundary work, not as a mandatory first step.
- Use OpenTimelineIO when an external editorial application needs timeline interchange.
- Use Auto-Editor for a proposed rough cut, then review the resulting edit decisions before delivery.

Do not install optional tools or download model weights without user approval. Keep the core workflow useful offline and do not send source media to a cloud provider by default.

## Adapter contract

An adapter declares a stable identifier and version, required executable/package, capabilities, supported formats, upstream source and license, availability check, dry-run/preview support, failure behavior, and whether each operation copies streams or re-encodes.

Discover tools at runtime. Report missing optional capabilities without breaking core editing. Test a new adapter on synthetic media before using it on a user's footage.
