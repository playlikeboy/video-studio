# OpenChatCut — standalone agent-native video editor

> Review snapshot checked 2026-11-03. Upstream versions, tool contracts, release assets and license notices can change.

[OpenChatCut repository](https://github.com/0xsline/OpenChatCut) · [v0.2.17 release](https://github.com/0xsline/OpenChatCut/releases/tag/v0.2.17) · [upstream README](https://github.com/0xsline/OpenChatCut#using-openchatcut-with-codex--claude-code)

## Why evaluate it

[OpenChatCut](https://github.com/0xsline/OpenChatCut) is a separate local-first editor with a multitrack timeline, agent workspace, MCP interface, reusable Agent Skills and Remotion-based rendering. It is a better fit when someone wants a complete visual editing application that both a person and an agent can operate—not just a headless FFmpeg operation.

The latest official release inspected for this guide is **v0.2.17**, published 2026-10-15. The inspected upstream main branch had commits through 2026-10-21. The project describes itself as active development; treat its project format, MCP tools and installer as evolving. Prefer a tagged release when evaluating it.

This is a manual, standalone alternative. It is not a Video Studio adapter, package dependency or installer option. Keep the Video Studio workflow lightweight and choose OpenChatCut only when its full editor is useful.

## Requirements and source setup

For a source checkout, upstream specifies **Node.js 24.x and npm**. The repository's `.nvmrc` selects the supported Node major. Follow the upstream installation guide for current desktop installers and platform-specific prerequisites.

```bash
git clone https://github.com/0xsline/OpenChatCut.git
cd OpenChatCut
npm install
cp .env.example .env.local
npm run dev
```

Open the local editor at `http://localhost:5199`. On Linux x64, upstream notes that `npm install` may download the optional ONNX Runtime CUDA provider. For a CPU-only source install, its README documents:

```bash
ONNXRUNTIME_NODE_INSTALL=skip npm install
```

Only configure model-provider or media-service credentials for capabilities you actually intend to use. Local timeline editing does not require you to configure every generation or transcription provider.

## Connect an agent

The upstream repository includes a local MCP configuration. Its Streamable HTTP endpoint is:

```text
http://localhost:5199/api/external-mcp/mcp
```

Keep this endpoint on loopback. Do not bind it to a public interface, reverse-proxy it onto an untrusted network, or expose it through a tunnel without a separate authentication and access-control review.

For Claude Code, register the local HTTP server after the editor is running:

```bash
claude mcp add --transport http openchatcut \
  http://localhost:5199/api/external-mcp/mcp
```

For Codex, add this to its MCP configuration:

```toml
[mcp_servers.openchatcut]
url = "http://localhost:5199/api/external-mcp/mcp"
```

The upstream project also documents a single Agent Skill installation:

```bash
npx skills add 0xsline/OpenChatCut
```

This installs OpenChatCut's own skill/router, which registers the local MCP connection and loads its 26 specialized skills on demand; it does not install or replace Video Studio. Follow the upstream agent setup guide and inspect any proposed MCP configuration before merging it into an existing agent config.

## Use the reviewable edit-session workflow

For external MCP editing, OpenChatCut documents this sequence:

1. Call `begin_edit_session` and retain the returned `editSessionId`.
2. Pass that ID to every project read/edit tool participating in the session.
3. Keep `approvalMode: "manual"` for normal work.
4. Call `review_edit_session` when the draft is ready, then inspect the preview and proposed timeline changes in the open project before approving or rejecting them.

In `manual` mode, review, preview, select and approve or reject the proposal inside the open OpenChatCut project. In `auto` mode, `review_edit_session` applies the complete draft immediately and bypasses that editor approval. Both modes commit applied operations atomically as one undo step; keep `manual` as the default. Only draft-safe project read/edit tools are exposed in edit sessions. Generation, export, project deletion and other immediate side-effect tools remain unavailable because a rejected proposal could not roll them back. Re-check the current upstream tool contract before relying on these boundaries.

## Local media and privacy

- The desktop app's agent local-media tools are enabled by default. If `AGENT_IMPORT_ROOTS` is empty, they have default unrestricted directory access, including mounted media drives; do not assume the desktop file picker scopes MCP access.
- Restrict both desktop and browser access by setting comma-separated `AGENT_IMPORT_ROOTS` entries to only the directories needed. Explicit restrictions apply to both browsing and import.
- For source checkouts, set the variable in `.env.local`. Packaged builds read their configuration from the per-user OpenChatCut data directory: `~/Library/Application Support/OpenChatCut/` on macOS, `%APPDATA%\OpenChatCut\` on Windows, and `$XDG_CONFIG_HOME/OpenChatCut/` (normally `~/.config/OpenChatCut/`) on Linux. Restart the application after editing the file.
- A browser session requires a non-empty allowlist and must run on the same machine as the editor. Open it at `http://localhost` or `http://127.0.0.1` (a secure browser context), or use HTTPS; plain HTTP through a LAN IP/reverse proxy disables browser capabilities the editor needs.
- Keep `localhost` or `127.0.0.1` for the local editor and MCP endpoint; do not expose either to an untrusted network.
- Projects and media are local by default, but configured model, online-media, generation or transcription providers may receive the prompts, media or derived data sent to them. Review each provider before enabling it.
- Upstream notes that its current macOS desktop packages are not signed or notarized. Inspect release assets and checksums, review the current macOS instructions, and do not disable Gatekeeper globally to run an unfamiliar build.

## License and redistribution boundary

The application declares **AGPL-3.0-or-later**. Its `src/agent/skills/NOTICE.md` separately says the bundled/adapted Agent Skills are derived from `ChatCut-Inc/agent-plugin` under **GPL-3.0-only**. Remotion has its own license and eligibility/pricing terms; bundled fonts, assets, binaries and other dependencies also retain their respective licenses.

This guide documents a separate application only. No OpenChatCut source, adapted skills, assets, binaries or models are copied into Video Studio. Do not vendor or adapt those files into this MIT-licensed repository without a deliberate licensing review. Before distributing a combined product or modified network service, review the applicable AGPL/GPL obligations and all third-party notices with qualified counsel.

## Sources checked

- [v0.2.17 release (2026-10-15)](https://github.com/0xsline/OpenChatCut/releases/tag/v0.2.17)
- [Repository README and MCP setup](https://github.com/0xsline/OpenChatCut#using-openchatcut-with-codex--claude-code)
- [Application license](https://github.com/0xsline/OpenChatCut/blob/main/LICENSE)
- [Agent Skills attribution notice](https://github.com/0xsline/OpenChatCut/blob/main/src/agent/skills/NOTICE.md)

