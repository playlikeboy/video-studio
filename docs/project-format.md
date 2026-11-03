# Project format

The canonical manifest is renderer-neutral JSON. See `skills/video-studio/references/project-format.md` and `examples/project.json`.

Project paths should be relative. Source media should remain external and unmodified by default. Derived assets must be traceable to their sources. Keep renderer-specific files in a subdirectory and record the renderer version.
