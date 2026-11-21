# Video Studio Claude Skill

Copy this entire directory into `.claude/skills/video-studio/` in a project or into your personal Claude Code skills directory. `SKILL.md` is the required entry point, and all task-specific reference guides are bundled in `references/`.

The bundled `scripts/sound_design.py` handles sound design: SFX on exact frames, Openverse music, ducking and -14 LUFS loudness. It uses only the Python standard library and FFmpeg. See `references/sound-design.md`.

The Skill is self-contained after copying: it does not require the repository-level `docs/` or `scripts/` directories at runtime. The repository-level `presets/` and `templates/` directories are optional companion assets. When installing into another project, copy those folders to that project's root only if you want the starter design systems and production blueprints available there.
