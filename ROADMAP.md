# Roadmap

This roadmap is aspirational. Check issues and releases for actual implementation status.

## Phase 1 — Reliable foundation
- [x] Add CodeQL analysis for Python and GitHub Actions on pushes, pull requests and a weekly schedule
- [x] Pin every GitHub Action to an immutable commit SHA and keep pins current through weekly Dependabot reviews
- [x] Pin CI jobs to the explicit Ubuntu 26.04 LTS runner during the `ubuntu-latest` migration
- [x] Establish renderer-neutral project manifest example
- [x] Add starter design-system specifications
- [x] Document performance and safety principles
- [x] Add a Claude Code `SKILL.md` entry point with required frontmatter and reference routing
- [x] Make the copied Skill self-contained with bundled references and optional companion assets
- [x] Add automated structural validation for presets/manifests and safe source paths
- [ ] Add synthetic-media integration tests

## Phase 2 — Practical editing adapters
- [x] Evaluate and document Kinocut as a manual, version-pinned guardrailed MCP alternative with explicit runtime and licensing boundaries
- [x] Document optional FableCut MCP timeline-editor integration and local-server safety boundaries
- [x] Evaluate WeftCut v0.5.6 as a manual desktop-NLE alternative; document its MCP review workflow, preview-scale Motif update, macOS launch guidance and separate FFmpeg license lanes without adding an installer dependency
- [x] Evaluate and document OpenChatCut v0.2.17 as a standalone AGPL-licensed multitrack editor; keep its GPL-licensed adapted skills and dependencies outside this MIT repository
- [ ] Structured FFmpeg editing operations
- [ ] Stream-copy trim and remux helpers
- [ ] Proxy and contact-sheet workflow
- [ ] Resume-safe render cache
- [ ] Audio mixing and ducking presets
- [ ] Caption import/export and safe placement

## Phase 3 — Motion production
- [ ] HyperFrames starter compositions
- [ ] Reusable title, lower-third and caption blocks
- [ ] Tech explainer and founder story templates
- [ ] Preview/render validation scripts
- [ ] Optional Remotion adapter

## Phase 4 — AI-assisted editing
- [ ] Optional faster-whisper adapter
- [ ] Word-aligned captions
- [ ] PySceneDetect adapter
- [ ] Transcript-guided edit decision list
- [ ] Optional beat analysis and B-roll suggestions
- [ ] Evaluate a structured media-analysis-skill adapter and its overlap with ffmpeg-skill

## Phase 5 — Ecosystem and distribution
- [ ] OpenTimelineIO interchange
- [ ] More creator templates and design systems
- [ ] Compatibility matrix for agent clients
- [ ] Reusable example gallery
- [ ] Automated release and skill package validation

## Principles

Fast local-first paths; optional heavy dependencies; real editing tools instead of repeated code generation; reproducible edits; transparent licensing.
