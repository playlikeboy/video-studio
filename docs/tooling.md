# Tooling and integrations

Video Studio is an orchestration skill, not a monolithic editor. It routes each task to the smallest installed tool that can do the job. This review snapshot was checked on **2026-11-03**; upstream versions, availability and terms can change.

## Core

- **FFmpeg / FFprobe** — media inspection, cut/trim/mux/filter/encode. No Python or Node media package is required by the core project.
- **Python standard library** — diagnostics, JSON asset validation and lightweight project checks.

## Recommended optional adapters

| Tool | Best use | Upstream license / policy | Integration guidance |
|---|---|---|---|
| [ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | Structured FFmpeg editing operations, machine-readable contracts and MCP tools | MIT | Prefer its typed tools when installed instead of duplicating them with shell strings. Its upstream README documents `npx ffmpeg-skill`, `doctor` and `contract --json`. |
| [FableCut](https://github.com/ronak-create/FableCut) | Interactive browser NLE with a JSON timeline, MCP/REST control, live preview and agent export | MIT | Optional local timeline editor. Node 18+ and Chromium are required; FFmpeg is optional but recommended. Use for human-in-the-loop timeline work, not as a mandatory media dependency. |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | Agent-authored HTML/CSS/GSAP compositions and deterministic video rendering | Apache-2.0 | Primary motion-graphics route. For Claude Code, install the official plugin with `claude plugin marketplace add heygen-com/hyperframes` and `claude plugin install hyperframes@hyperframes`; standalone agents can use `npx skills add heygen-com/hyperframes`. The installer applies the selected user/project scope to the marketplace and plugin, running project-scoped setup from the chosen project directory. Preview an existing project with `npx hyperframes preview`. |
| [Remotion](https://github.com/remotion-dev/remotion) | React-authored video compositions | Source-available Remotion License; usage-dependent | Keep optional. The free license covers individuals, teams/companies of up to three people, eligible non-profits and evaluation; it permits commercial use and automation. The separate Automators pricing applies to Company License users, not eligible Free License users. Larger organizations should review the Creators/Automators options and current terms before use. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Local speech-to-text | MIT | Optional model-backed dependency. Install only when transcription is needed; model weights are downloaded separately. |
| [WhisperX](https://github.com/m-bain/whisperX) | Word-level alignment and speaker diarization | BSD-2-Clause | Use only when word timing or diarization materially improves the edit. PyTorch, pyannote and model weights have their own runtime and license terms. |
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Shot/scene boundary detection | BSD-3-Clause | Optional analysis dependency; do not run it when simple sampling is sufficient. |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) | Timeline interchange between editorial tools | Apache-2.0 | Optional interchange layer. OTIO stores editorial structure and media references, not the media files themselves; some adapters are separately packaged. |
| [Auto-Editor](https://github.com/WyattBlue/auto-editor) | Automated silence- or motion-based rough cuts | Unlicense for repository source | Optional rough-cut tool. The upstream project notes that some application assets have separate proprietary terms; do not assume every asset is covered by the source license. |

## Routing rules

- Use FFmpeg or `ffmpeg-skill` for direct media operations. Do not rebuild a tool that already exists and is available.
- Use FableCut when the user wants a visible, interactive timeline that an agent can edit through MCP and a person can review live. Keep the server local, preserve its revision checks and verify its export with FFprobe.
- Use HyperFrames for HTML-native motion, animated titles, UI demos, diagrams and reusable graphic scenes. Use Remotion only when a React authoring model is a genuine advantage.
- Prefer faster-whisper for straightforward local transcription; add WhisperX only when word alignment or diarization is required.
- Use PySceneDetect for meaningful shot-boundary work, not as a mandatory first step.
- Use OpenTimelineIO when an external editorial application needs timeline interchange.
- Use Auto-Editor for a proposed rough cut, then review the resulting edit decisions before delivery.

Do not install optional tools or download model weights without user approval. Keep the core workflow useful offline and do not send source media to a cloud provider by default.

## Complementary analysis candidate

[media-analysis-skill](https://github.com/kajisho5/media-analysis-skill) is a separate MIT-licensed companion that measures local media facts (streams, duration, silence, loudness, integrity and scene cuts) and emits a versioned Observation JSON contract with content-addressed caching and execution budgets. Its latest checked release is [v0.1.7](https://github.com/kajisho5/media-analysis-skill/releases/tag/v0.1.7), published 2026-10-31. It does not edit or render media. There is intentional overlap with ffmpeg-skill's probe, silence, loudness and scene tools, so keep it experimental and do not install it by default until a Video Studio adapter and synthetic-media compatibility tests exist.

## Experimental editor candidate (not installed)

[MakeMyClip Editor](https://github.com/MakeMyClip/editor) is a promising local-first CLI/browser/MCP editor with a Claude Code skill and 19 deterministic editing tools. Its latest published release at this review was [v0.3.1](https://github.com/MakeMyClip/editor/releases/tag/v0.3.1), dated **2026-10-29**. The project is still pre-1.0 and declares **Node.js 24+**.

The editor source is MIT-licensed, but the published package declares ffmpeg-static as a dependency. The upstream README says its bundled FFmpeg binary is GPL because it includes codecs such as libx264/libx265. It documents a custom FFmpeg override, but that alone does not establish that installing the npm package avoids fetching the bundled binary or removes its licensing obligations. Review the exact package contents and FFmpeg build before distribution.

It overlaps substantially with ffmpeg-skill and FableCut, so it is documented as an evaluation candidate only—not an installer option or a default integration. Pin a release if testing it because the upstream tool schemas may change before 1.0. No MakeMyClip source or binary is vendored here.

## Upstream release snapshot — 2026-11-03

- [`ffmpeg-skill` v3.1.1](https://github.com/kajisho5/ffmpeg-skill/releases/tag/v3.1.1) was released on 2026-10-31 under MIT. This release includes the new static landing page and an improvement to filler-word prompting in local transcription.
- [HyperFrames v0.9.8](https://github.com/heygen-com/hyperframes/releases/tag/v0.9.8) was released on 2026-11-03 under Apache-2.0. It adds a screenshot-capture fallback when BeginFrame capture fails and allows screenshot capture to be requested directly.
- [FableCut v1.18.0](https://github.com/ronak-create/FableCut/releases/tag/v1.18.0) was released on 2026-10-27 under MIT. Recent capabilities include beat-grid analysis, beat-aligned edits, subject-follow reframing and highlight assembly.

These are review-time references, not pinned dependencies. Check upstream release notes and package contents again before installing or upgrading.

## Adapter contract

An adapter declares a stable identifier and version, required executable/package, capabilities, supported formats, upstream source and license, availability check, dry-run/preview support, failure behavior, and whether each operation copies streams or re-encodes.

Discover tools at runtime. Report missing optional capabilities without breaking core editing. Test a new adapter on synthetic media before using it on a user's footage.
