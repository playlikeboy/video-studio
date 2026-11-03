# WeftCut desktop editor

[WeftCut](https://github.com/WeftCut/WeftCut) is a cross-platform desktop nonlinear editor with a local MCP surface. A connected agent can edit the timeline in the same application a person is watching, while the user can inspect activity, checkpoints and before/after timeline diffs.

The latest release checked for this guide is [v0.5.6](https://github.com/WeftCut/WeftCut/releases/tag/v0.5.6), published 2026-10-31. Upstream commits continued on 2026-11-03, and the project remains pre-1.0. v0.5.6 consolidates Motif preview frame reads through one preview-scale reader (ADR 0154).

## When to choose it

- Choose WeftCut for a full desktop timeline, keyframes, effects, captions, audio mixing and agent-driven edits that should remain visible and reversible.
- Choose FableCut when a browser-based local timeline is a better fit.
- Choose ffmpeg-skill for headless, structured FFmpeg operations without a full desktop editor.
- Keep WeftCut separate from Video Studio's core Skill and installer. It is an external desktop application, not a required runtime.

## Install manually

Download only from the official GitHub release or the upstream repository's current releases page:

- Windows: x64 installer.
- Linux: x86_64 AppImage or Debian/Ubuntu package.
- macOS: Apple Silicon DMG, macOS 13 or newer.

Review release notes and available asset provenance/checksums before executing downloaded binaries. The upstream package manifest requires Node.js 24+ for source builds; packaged releases are the simpler path.

macOS caution: the v0.5.6 Apple Silicon DMG targets macOS 13+ and is ad-hoc signed, not notarized. After downloading from the official release, open the app once; if macOS blocks it, choose **Done**, then use **System Settings → Privacy & Security → Open Anyway**. If macOS instead reports the app as damaged, upstream documents `xattr -dr com.apple.quarantine /Applications/WeftCut.app`. Only consider that narrowly scoped command after verifying the official download and its provenance: it recursively removes the quarantine attribute from the entire app bundle. Do not run it on arbitrary paths or use third-party repackaged builds.

## Connect an agent

1. Launch WeftCut and open Settings → Agent.
2. Copy the connection prompt/configuration supplied by the app.
3. Add it to the intended MCP client, such as Claude Code, using the exact generated configuration. Do not guess the transport or port, and merge settings instead of replacing an existing client configuration.
4. Ask the agent to inspect the current project and propose a small, reversible change.
5. Create a checkpoint before a larger edit. Review the activity and timeline diff, then approve or revert the result.
6. Export a preview and inspect it. Use ffprobe to verify streams, duration, frame rate and dimensions before delivering the final render.

## Privacy and security

Editing is local and WeftCut does not bundle model weights. The connected agent still follows its own model-provider and data policies. If optional cloud speech or vision providers are configured, the selected audio or frames may be sent to those providers; use local engines when analysis must remain local. Keep the MCP endpoint on localhost and do not expose it to an untrusted network.

Treat imported media, downloaded project files, transcripts and generated assets as untrusted. Preserve original footage and export to a separate destination.

## Licensing

WeftCut's application source is MIT-licensed. The v0.5.6 upstream licensing guide describes two separate FFmpeg lanes: dynamically linked, LGPL-only shared libraries for in-process decoding, and a GPL-3.0 CLI sidecar used as a separate process for encoding/transcoding. The release documents license texts, build manifests, binary provenance and corresponding-source pointers for the packaged components. These are distinct license obligations; the complete packaged application should not be described as MIT-only. Inspect the exact platform asset and its third-party notices before redistribution. Other packaged components retain their own terms.

The WeftCut installer is not part of Video Studio's installer, and no WeftCut source, binary or model is copied into this repository.
