#!/usr/bin/env python3
"""Report core and optional Video Studio tool availability."""
from __future__ import annotations
import json
import platform
import shutil
import subprocess

TOOLS = {
    "ffmpeg": ("ffmpeg", ["-version"]),
    "ffprobe": ("ffprobe", ["-version"]),
    "node": ("node", ["--version"]),
    "npm": ("npm", ["--version"]),
    "python": (shutil.which("python3") or "python", ["--version"]),
    "hyperframes": ("hyperframes", ["--version"]),
    "remotion": ("remotion", ["--version"]),
    "whisperx": ("whisperx", ["--help"]),
    "faster-whisper": ("faster-whisper", ["--help"]),
    "scenedetect": ("scenedetect", ["version"]),
    "auto-editor": ("auto-editor", ["--version"]),
}

def version(binary: str, args: list[str]) -> str | None:
    path = shutil.which(binary)
    if not path:
        return None
    try:
        proc = subprocess.run([path, *args], capture_output=True, text=True, timeout=8, check=False)
        lines = (proc.stdout or proc.stderr).strip().splitlines()
        return lines[0][:180] if lines else f"available (exit {proc.returncode})"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"detected; version check failed: {exc}"

def main() -> int:
    results = {name: {"available": shutil.which(binary) is not None, "version": version(binary, args)} for name, (binary, args) in TOOLS.items()}
    print(json.dumps({"platform": platform.platform(), "tools": results}, indent=2))
    return 0 if results["ffmpeg"]["available"] and results["ffprobe"]["available"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
