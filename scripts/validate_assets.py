#!/usr/bin/env python3
"""Validate JSON presets and example project manifests."""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "presets").glob("*.json")) + sorted((ROOT / "examples").glob("*.json"))

def main() -> int:
    failures = []
    for path in FILES:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("top-level JSON value must be an object")
            print(f"OK   {path.relative_to(ROOT)}")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            failures.append((path, str(exc)))
            print(f"FAIL {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
    if failures:
        return 1
    print(f"Validated {len(FILES)} JSON files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
