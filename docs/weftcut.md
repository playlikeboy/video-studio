# WeftCut desktop editor

[WeftCut](https://github.com/WeftCut/WeftCut) is a cross-platform desktop nonlinear editor with a local MCP surface. A connected agent can edit the timeline in the same application a person is watching, while the user can inspect activity, checkpoints and before/after timeline diffs.

The latest release checked for this guide is [v0.5.4](https://github.com/WeftCut/WeftCut/releases/tag/v0.5.4), published 2026-10-27. The project is actively developed but remains pre-1.0.

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

macOS caution: the upstream release notes describe the Apple Silicon build as ad-hoc signed and not notarized. Review the current upstream macOS guidance and make an informed Gatekeeper decision. Avoid third-party repackaged builds or blindly running shell commands copied from unrelated posts.

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

WeftCut's application source is MIT-licensed. Packaged installers additionally contain FFmpeg shared libraries for in-process decoding under LGPL-2.1-or-later and a separate GPL-3.0 command-line sidecar for encoding/transcoding. See the upstream licensing explanation and third-party notices. Other packaged components retain their own terms.

The WeftCut installer is not part of Video Studio's installer, and no WeftCut source, binary or model is copied into this repository.
