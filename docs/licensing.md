# Licensing and third-party tools

Video Studio's own source is MIT-licensed. The MIT license applies to this repository only; it does not relicense third-party tools, model weights, fonts, music, footage, logos or generated assets.

## Integration license snapshot

Reviewed **2026-11-03** against upstream project pages. Always re-check the exact release, package, bundled assets and current terms before distribution or commercial use.

| Project | Upstream license / terms | Notes |
|---|---|---|
| [ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT | Optional external editing skill/MCP server. No source is vendored here. |
| [Kinocut](https://github.com/KyaniteLabs/kinocut) | Apache-2.0 | Tagged v1.16.5 declares Python 3.11+ and a core dependency set; optional ML extras and external FFmpeg builds have their own dependency/codec terms. No source or binary is vendored here. |
| [FableCut](https://github.com/ronak-create/FableCut) | MIT | Optional browser NLE/MCP server. Its bundled fonts and other assets may have separate licenses; the upstream repository documents its font licenses. No source or assets are vendored here. |
| [OpenChatCut](https://github.com/0xsline/OpenChatCut) | AGPL-3.0-or-later application; adapted bundled Agent Skills GPL-3.0-only; Remotion and other dependencies/assets have separate terms | Manual standalone application only. Do not copy or adapt its code, skills or assets into this MIT repository without a licensing review. No source or binaries are vendored here. |
| [WeftCut](https://github.com/WeftCut/WeftCut) | MIT application source; v0.5.6 package uses dynamically linked LGPL-2.1-or-later FFmpeg decode libraries from an LGPL-only build and a separate GPL-3.0 CLI sidecar | Manual desktop alternative only. Upstream documents separate license texts, build manifests, binary provenance and corresponding-source pointers. Inspect the exact platform asset and notices before redistribution; no source or binaries are vendored here. |
| [MakeMyClip Editor](https://github.com/MakeMyClip/editor) | MIT source; bundled ffmpeg-static binary described by upstream as GPL | The npm package declares ffmpeg-static as a dependency. Review the exact binary build and GPL notices separately; do not describe the distributed package as MIT-only. No source or binary is vendored here. |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | Apache-2.0 | Open-source HTML/CSS/GSAP renderer. Its current upstream release notes and package metadata should be checked when upgrading. |
| [Remotion](https://www.remotion.dev/docs/license/pricing) | Remotion License (source-available; not standard MIT/Apache) | The Free License covers individuals, teams/companies of up to three people, eligible non-profits and evaluation; it allows commercial use and automation. The separate Automators plan ($0.01/render, $100/month minimum) applies to Company License users; Creator seats are a separate option. Confirm the current eligibility definitions and terms for the actual organization/use case. |
| [media-analysis-skill](https://github.com/kajisho5/media-analysis-skill) | MIT | Experimental companion for deterministic local observations; no source is vendored here. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT | Model weights and any additional model assets can have separate terms. |
| [WhisperX](https://github.com/m-bain/whisperX) | BSD-2-Clause | Its dependencies and diarization models are separately licensed. The upstream README identifies pyannote models with their own CC-BY-4.0 terms and gated access requirements. |
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | BSD-3-Clause | Check optional codecs and linked libraries independently. |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) | Apache-2.0 | Third-party adapters may use different licenses and are distributed separately. |
| [Auto-Editor](https://github.com/WyattBlue/auto-editor) | Unlicense for repository source | Upstream notes that unique assets in its online/application products are under separate proprietary terms. |

## Important caveats

- **FFmpeg:** the license of a particular build depends on how it was configured and which external libraries/codecs were enabled. Builds that enable GPL components are GPL-licensed; do not assume every downloaded binary is LGPL-only.
- **WeftCut:** v0.5.6 documents two distinct FFmpeg lanes: dynamically linked LGPL-2.1-or-later shared libraries built without FFmpeg GPL/nonfree components for in-process decode and a separate GPLv3 CLI sidecar for encoding/transcoding. Verify the exact release asset, build manifest, license text and corresponding-source pointer before redistribution; do not infer the packaged application's licensing from its MIT source alone.
- **Remotion:** source availability is not an OSI open-source license. Eligible Free License users may use it commercially and for automation; Company License users must select the appropriate Creators and/or Automators plan. Read the current eligibility, definitions and pricing for the actual use case.
- **Speech models:** a permissive Python package license does not automatically grant rights to every model checkpoint, voice dataset or diarization model. Review the model card and access terms.
- **Media assets:** verify rights for music, fonts, footage, logos, stock media and generated assets. Do not bundle them just because a rendering tool can read them.
- **AGPL/GPL projects:** OpenChatCut is AGPL-3.0-or-later, and its upstream attribution notice identifies adapted Agent Skills under GPL-3.0-only. Study the architecture if useful, but do not copy or adapt its code, skills or assets into this MIT repository without an explicit licensing decision.

No third-party source code is copied into this starter. Integrations are documented as optional external tools.
