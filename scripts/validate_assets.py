#!/usr/bin/env python3
"""Validate Video Studio presets, project manifests, and the Claude Skill entry point."""
from __future__ import annotations

import json
import math
from collections import Counter
from html.parser import HTMLParser
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRESET_FILES = sorted((ROOT / "presets").glob("*.json"))
PROJECT_FILES = sorted((ROOT / "examples").glob("*.json"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def positive_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value > 0
    return isinstance(value, float) and math.isfinite(value) and value > 0


def non_negative_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= 0
    return isinstance(value, float) and math.isfinite(value) and value >= 0


def validate_preset(path: Path, data: dict[str, Any]) -> None:
    require(data.get("name") == path.stem, "name must match the preset filename")
    require(isinstance(data.get("version"), str) and data["version"], "version must be a non-empty string")
    canvas = data.get("canvas")
    require(isinstance(canvas, dict), "canvas must be an object")
    for field in ("width", "height", "fps"):
        require(positive_number(canvas.get(field)), f"canvas.{field} must be a positive finite number")
    for field in ("colors", "typography", "layout", "motion", "captions", "audio", "assets"):
        require(isinstance(data.get(field), dict), f"{field} must be an object")
    require(isinstance(data.get("transitions"), list), "transitions must be an array")


def validate_project(data: dict[str, Any]) -> None:
    require(data.get("schemaVersion") == "1.0.0", "schemaVersion must be 1.0.0")
    require(isinstance(data.get("name"), str) and data["name"].strip(), "name must be a non-empty string")
    canvas = data.get("canvas")
    require(isinstance(canvas, dict), "canvas must be an object")
    for field in ("width", "height", "fps"):
        require(positive_number(canvas.get(field)), f"canvas.{field} must be a positive finite number")

    sources = data.get("sources")
    require(isinstance(sources, list), "sources must be an array")
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        require(isinstance(source, dict), f"sources[{index}] must be an object")
        source_id = source.get("id")
        require(isinstance(source_id, str) and source_id.strip(), f"sources[{index}].id must be a non-empty string")
        require(source_id not in source_ids, f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        source_path = source.get("path")
        require(isinstance(source_path, str) and source_path.strip(), f"sources[{index}].path must be a non-empty string")
        normalized = source_path.replace("\\", "/")
        path = PurePosixPath(normalized)
        require(not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:/", normalized), f"sources[{index}].path must be a safe relative path")

    tracks = data.get("tracks")
    require(isinstance(tracks, list), "tracks must be an array")
    track_ids: set[str] = set()
    for track_index, track in enumerate(tracks):
        require(isinstance(track, dict), f"tracks[{track_index}] must be an object")
        track_id = track.get("id")
        require(isinstance(track_id, str) and track_id.strip(), f"tracks[{track_index}].id must be a non-empty string")
        require(track_id not in track_ids, f"duplicate track id: {track_id}")
        track_ids.add(track_id)
        require(isinstance(track.get("type"), str) and track["type"], f"tracks[{track_index}].type must be a non-empty string")
        clips = track.get("clips", [])
        require(isinstance(clips, list), f"tracks[{track_index}].clips must be an array")
        for clip_index, clip in enumerate(clips):
            label = f"tracks[{track_index}].clips[{clip_index}]"
            require(isinstance(clip, dict), f"{label} must be an object")
            if "sourceId" in clip:
                source_ref = clip["sourceId"]
                require(isinstance(source_ref, str) and source_ref in source_ids, f"{label}.sourceId references an unknown source")
            require(non_negative_number(clip.get("start")), f"{label}.start must be a non-negative finite number")
            require(positive_number(clip.get("end")), f"{label}.end must be a positive finite number")
            require(clip["end"] > clip["start"], f"{label}.end must be greater than start")
            require(non_negative_number(clip.get("timelineStart", 0)), f"{label}.timelineStart must be non-negative")
            require(positive_number(clip.get("speed", 1)), f"{label}.speed must be positive")

    design = data.get("design")
    require(isinstance(design, dict) and isinstance(design.get("preset"), str) and design["preset"], "design.preset must be a non-empty string")
    renderer = data.get("renderer")
    require(isinstance(renderer, dict) and isinstance(renderer.get("name"), str) and renderer["name"], "renderer.name must be a non-empty string")
    for field in ("captions", "audio", "exports"):
        require(isinstance(data.get(field), list), f"{field} must be an array")


def validate_skill(path: Path) -> None:
    require(path.is_file(), "skills/video-studio/SKILL.md is missing")
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    require(lines and lines[0].strip() == "---", "SKILL.md must start with YAML frontmatter")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter is not closed") from exc
    frontmatter = "\n".join(lines[1:closing])
    name = re.search(r"^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", frontmatter, re.MULTILINE)
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    require(name is not None and name.group(1) == "video-studio", "frontmatter name must be video-studio")
    require(description is not None and 20 <= len(description.group(1).strip()) <= 1024, "frontmatter description must be 20–1024 characters")
    require(len(lines) > closing + 1 and any(line.strip() for line in lines[closing + 1:]), "SKILL.md body must not be empty")


class DocsSiteParser(HTMLParser):
    """Collect the small set of structural facts needed for a static Pages smoke test."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.fragments: list[str] = []
        self.h1_count = 0
        self.main_count = 0
        self.has_description = False
        self.in_title = False
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.ids.append(element_id)
        href = attributes.get("href", "") or ""
        if tag == "a" and href.startswith("#") and len(href) > 1:
            self.fragments.append(href[1:])
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.main_count += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta" and (attributes.get("name") or "").lower() == "description":
            self.has_description = bool((attributes.get("content") or "").strip())

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data.strip())


def validate_docs_site(path: Path) -> None:
    """Fail CI on missing page metadata, duplicate IDs or broken local anchors."""
    parser = DocsSiteParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    duplicates = sorted(identifier for identifier, count in Counter(parser.ids).items() if count > 1)
    missing = sorted(set(parser.fragments).difference(parser.ids))
    require(bool("".join(parser.title_parts).strip()), "docs site must have a non-empty title")
    require(parser.has_description, "docs site must have a non-empty meta description")
    require(parser.main_count == 1, "docs site must have exactly one main landmark")
    require(parser.h1_count == 1, "docs site must have exactly one H1 heading")
    require(not duplicates, "docs site has duplicate id(s): " + ", ".join(duplicates))
    require(not missing, "docs site has internal anchor(s) without a matching id: " + ", ".join(missing))


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def main() -> int:
    failures: list[tuple[str, str]] = []
    checked = 0
    for path in PRESET_FILES:
        try:
            validate_preset(path, load_object(path))
            print(f"OK   {path.relative_to(ROOT)}")
            checked += 1
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            failures.append((str(path.relative_to(ROOT)), str(exc)))
            print(f"FAIL {path.relative_to(ROOT)}: {exc}", file=sys.stderr)

    for path in PROJECT_FILES:
        try:
            validate_project(load_object(path))
            print(f"OK   {path.relative_to(ROOT)}")
            checked += 1
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            failures.append((str(path.relative_to(ROOT)), str(exc)))
            print(f"FAIL {path.relative_to(ROOT)}: {exc}", file=sys.stderr)

    skill_path = ROOT / "skills" / "video-studio" / "SKILL.md"
    try:
        validate_skill(skill_path)
        print(f"OK   {skill_path.relative_to(ROOT)}")
        checked += 1
    except (OSError, ValueError) as exc:
        failures.append((str(skill_path.relative_to(ROOT)), str(exc)))
        print(f"FAIL {skill_path.relative_to(ROOT)}: {exc}", file=sys.stderr)

    site_path = ROOT / "docs" / "index.html"
    try:
        validate_docs_site(site_path)
        print(f"OK   {site_path.relative_to(ROOT)}")
        checked += 1
    except (OSError, ValueError) as exc:
        failures.append((str(site_path.relative_to(ROOT)), str(exc)))
        print(f"FAIL {site_path.relative_to(ROOT)}: {exc}", file=sys.stderr)

    if not PRESET_FILES:
        failures.append(("presets/", "no preset JSON files found"))
    if not PROJECT_FILES:
        failures.append(("examples/", "no project JSON files found"))

    if failures:
        print(f"{len(failures)} validation error(s); {checked} asset(s) passed.", file=sys.stderr)
        return 1
    print(f"Validated {checked} assets and the Claude Skill entry point.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
