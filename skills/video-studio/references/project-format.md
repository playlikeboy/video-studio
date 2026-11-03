# Project format

Keep a renderer-independent project manifest so work can be resumed and audited.

Example: see `../../../../examples/project.json`.

Rules: store relative paths inside the project; never embed secrets; preserve original source timecodes; record operation and tool versions where possible; make every derived asset traceable to its source; keep generated media outside version control unless intentionally publishing a small sample with rights cleared.

OpenTimelineIO can be used as an interchange layer. It does not replace project asset provenance and design-token metadata.
