#!/usr/bin/env python3
"""Install Video Studio's existing Claude Skill; optional tools are opt-in."""
from __future__ import annotations
import argparse
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import venv
from pathlib import Path

TOOLS = {
    "ffmpeg-skill": ("Structured FFmpeg tools and MCP (MIT)", "node", None),
    "hyperframes": ("HyperFrames motion graphics and Claude skill (Apache-2.0; Node 22+)", "node22", None),
    "fablecut": ("FableCut local timeline editor and MCP (MIT; Node 18+)", "node18", None),
    "remotion": ("Remotion React video starter (review current license eligibility)", "node", None),
    "faster-whisper": ("Local speech transcription (MIT; model downloads on first use)", "python", "faster-whisper"),
    "whisperx": ("Word alignment and diarization (large PyTorch dependencies)", "python", "whisperx"),
    "pyscenedetect": ("Scene detection (BSD-3-Clause)", "python", "scenedetect-headless"),
    "opentimelineio": ("Timeline interchange", "python", "opentimelineio"),
    "auto-editor": ("Silence/activity rough-cut tool", "auto", None),
}
ALL_TOOLS = tuple(TOOLS)

def ask_yes_no(question: str, default: bool = False, input_fn=input) -> bool:
    try:
        answer = input_fn(question + (" [Y/n] " if default else " [y/N] ")).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return default if not answer else answer in {"y", "yes"}

def parse_tools(value: str | None) -> set[str]:
    if not value:
        return set()
    names = {part.strip().lower() for part in value.split(",") if part.strip()}
    if "all" in names:
        if len(names) != 1:
            raise ValueError("'all' cannot be combined with individual names")
        return set(ALL_TOOLS)
    unknown = names.difference(TOOLS)
    if unknown:
        raise ValueError("Unknown optional tool(s): " + ", ".join(sorted(unknown)))
    return names

def choose_scope(scope: str | None, yes: bool, input_fn=input) -> str:
    if scope:
        return scope
    if yes:
        return "user"
    print("Install location: 1) Personal Claude Code skills  2) This project only")
    try:
        return "project" if input_fn("Choose 1 or 2 [1]: ").strip() == "2" else "user"
    except (EOFError, KeyboardInterrupt):
        return "user"

def skill_destination(scope: str, home: Path, project_dir: Path) -> Path:
    base = project_dir if scope == "project" else home
    return base / ".claude" / "skills" / "video-studio"

def copy_skill(source: Path, destination: Path, *, update=False, dry_run=False) -> bool:
    source, destination = source.resolve(), destination.expanduser()
    if not (source / "SKILL.md").is_file():
        raise FileNotFoundError(f"Incomplete Skill bundle: {source}")
    if destination.is_symlink():
        raise ValueError(f"Refusing symlink destination: {destination}")
    if destination.exists() and not update:
        return False
    if dry_run:
        print(f"DRY RUN: copy {source} -> {destination}")
        return True
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    return True

def data_directory(home: Path) -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", str(home))) / "VideoStudio"
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support" / "VideoStudio"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", str(home / ".local/share"))) / "video-studio"
    return base / "venvs"

def venv_python(env: Path) -> Path:
    return env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

def run_command(command: list[str], dry_run=False) -> bool:
    print("  $ " + (subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)))
    if dry_run:
        return True
    try:
        result = subprocess.run(command, check=False, shell=False)
    except OSError as exc:
        print(f"  Could not start command: {exc}")
        return False
    if result.returncode:
        print(f"  Command failed with exit status {result.returncode}.")
        return False
    return True

def node_major() -> int | None:
    if not shutil.which("node"):
        return None
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=False)
        match = re.search(r"v?(\d+)", result.stdout or result.stderr)
        return int(match.group(1)) if result.returncode == 0 and match else None
    except OSError:
        return None

def install_python_tool(name: str, home: Path, dry_run=False) -> bool:
    env = data_directory(home) / name
    python = venv_python(env)
    if not python.exists():
        if dry_run:
            print(f"DRY RUN: create isolated environment {env}")
        else:
            try:
                venv.EnvBuilder(with_pip=True).create(env)
            except Exception as exc:
                print(f"  Could not create isolated Python environment: {exc}")
                return False
    package = TOOLS[name][2]
    return (run_command([str(python), "-m", "pip", "install", "--upgrade", "pip"], dry_run)
            and run_command([str(python), "-m", "pip", "install", package], dry_run))

def install_optional(name: str, scope: str, home: Path, dry_run=False) -> bool:
    label, kind, _ = TOOLS[name]
    if kind.startswith("node"):
        required = 22 if kind == "node22" else 18
        found = node_major()
        if found is None or found < required:
            print(f"  {name} needs Node.js {required}+; detected {found or 'not installed'}.")
            return False
    if name == "ffmpeg-skill":
        return run_command(["npx", "--yes", "ffmpeg-skill"] + (["--project"] if scope == "project" else []), dry_run)
    if name == "hyperframes":
        if not shutil.which("npm"):
            print("  npm was not found; install Node.js 22+ with npm.")
            return False
        return run_command(["npm", "install", "--global", "hyperframes"], dry_run) and run_command(
            ["npx", "--yes", "hyperframes", "skills", "--claude"], dry_run)
    if name == "fablecut":
        if not shutil.which("claude"):
            print("  Claude Code CLI missing. Manual command: claude mcp add -s user fablecut -- npx -y fablecut mcp")
            return False
        return run_command(["claude", "mcp", "add", "-s", "user", "fablecut", "--", "npx", "-y", "fablecut", "mcp"], dry_run)
    if name == "remotion":
        target = home / "video-studio-remotion"
        if target.exists():
            print(f"  Refusing to overwrite existing project: {target}")
            return False
        return run_command(["npx", "--yes", "create-video@latest", "--yes", "--blank", str(target)], dry_run)
    if kind == "python":
        return install_python_tool(name, home, dry_run)
    if name == "auto-editor":
        if shutil.which("auto-editor"):
            print("  Auto-Editor already exists on PATH.")
            return True
        if shutil.which("brew"):
            return run_command(["brew", "install", "auto-editor"], dry_run)
        if shutil.which("yay"):
            return run_command(["yay", "-S", "auto-editor"], dry_run)
        print("  Install the official binary: https://github.com/WyattBlue/auto-editor/releases")
        print("  Instructions: https://auto-editor.com/installing")
        return False
    return False

def ffmpeg_check():
    missing = [name for name in ("ffmpeg", "ffprobe") if not shutil.which(name)]
    if not missing:
        print("FFmpeg and FFprobe detected.")
        return
    print("Missing core media executable(s): " + ", ".join(missing))
    print("Install FFmpeg, then reopen the terminal:")
    if platform.system() == "Darwin":
        print("  brew install ffmpeg")
    elif platform.system() == "Windows":
        print("  winget install ffmpeg")
    else:
        print("  sudo apt install ffmpeg    # Debian / Ubuntu")
        print("  sudo dnf install ffmpeg    # Fedora with enabled repositories")
    print("FFmpeg is not installed automatically by this script.")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install the Video Studio Skill; optional integrations are opt-in.")
    parser.add_argument("--scope", choices=("user", "project"))
    parser.add_argument("--project-dir", type=Path, help="Target folder when --scope project is selected")
    parser.add_argument("--with-tools", help="Comma-separated optional tools, or 'all'")
    parser.add_argument("--update", action="store_true", help="Update matching Skill files after confirmation")
    parser.add_argument("--yes", action="store_true", help="Safe non-interactive defaults; skip optional tools")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing the machine")
    args = parser.parse_args(argv)
    try:
        selected = parse_tools(args.with_tools)
    except ValueError as exc:
        parser.error(str(exc))
    root = Path(__file__).resolve().parents[1]
    source, home = root / "skills" / "video-studio", Path.home()
    scope = choose_scope(args.scope, args.yes)
    project = (args.project_dir or Path.cwd()).expanduser().resolve()
    if scope == "project" and not project.is_dir():
        parser.error(f"Project directory does not exist: {project}")
    target = skill_destination(scope, home, project)
    print("Video Studio installer — the core Skill has no Python/Node package dependencies.")
    print(f"Install target: {target}")
    update = args.update
    if target.exists() and not update and not args.yes:
        update = ask_yes_no("Skill already exists. Update matching files? Unrelated files will be kept.", False)
    copied = copy_skill(source, target, update=update, dry_run=args.dry_run)
    if copied:
        print("Skill copy planned." if args.dry_run else "Skill installed.")
    elif target.exists():
        print("Existing Skill left untouched.")
    else:
        print("Skill not installed.")
    if args.with_tools is None and not args.yes:
        print("Optional integrations — every prompt defaults to No. Skip any or all.")
        for name, (label, _, _) in TOOLS.items():
            if ask_yes_no("Install " + label + "?", False):
                selected.add(name)
    if selected:
        for name in ALL_TOOLS:
            if name in selected:
                print(f"\n[{name}]")
                install_optional(name, scope, home, args.dry_run)
    else:
        print("No optional integrations selected; no extras installed.")
    ffmpeg_check()
    print("Done. The source Skill and its reference guides were not modified.")
    print("Guide: https://playlikeboy.github.io/video-studio/#installation")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
