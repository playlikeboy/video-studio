# Licensing boundaries

Video Studio's own source is MIT-licensed. That license applies to this repository only; it does not relicense third-party tools, model weights, fonts, music, footage, logos or generated assets.

## Integration snapshot

| Tool | Upstream license / terms | Review before use |
|---|---|---|
| FFmpeg | LGPL or GPL depending on build configuration and enabled components | Inspect the exact binary's build configuration and linked libraries. |
| ffmpeg-skill | MIT | Optional external skill/MCP server; no source is vendored here. |
| FableCut | MIT | Bundled fonts and other assets can have separate terms; review upstream asset notices. |
| HyperFrames | Apache-2.0 | Keep upstream notices when redistributing its code or assets. |
| Remotion | Source-available Remotion License | Eligibility and pricing depend on team size and use case; automated video products may need a paid plan. |
| faster-whisper | MIT | Model weights and additional model assets have their own terms. |
| WhisperX | BSD-2-Clause | Dependencies and diarization models are separately licensed; check model cards and access requirements. |
| PySceneDetect | BSD-3-Clause | Check optional codecs and linked libraries independently. |
| OpenTimelineIO | Apache-2.0 | Third-party adapters may use different licenses. |
| Auto-Editor | Unlicense for repository source | Some application assets have separate proprietary terms. |

## Rules

- Review the exact upstream release, package contents and current terms before installing, upgrading or redistributing.
- A permissive Python/JavaScript package license does not automatically cover model checkpoints, fonts, music, footage or other downloaded assets.
- FFmpeg builds that enable GPL components are GPL-licensed; do not assume every binary is LGPL-only.
- Do not copy AGPL-licensed source into this MIT project without an explicit licensing decision. OpenMontage is an example of an AGPL-3.0 project whose architecture may be studied without copying its code.
- Do not install optional tools or download model weights without user approval.

This is an operational summary, not legal advice. The full repository license matrix is in `docs/licensing.md` when the Video Studio source checkout is available.
