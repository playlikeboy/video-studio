#!/usr/bin/env python3
"""Frame-accurate sound design for Video Studio.

Takes a video and a cue list, renders sound effects with earshot, optionally fetches openly
licensed music or effects from Openverse, places every sound on an exact frame, ducks music under
the video's own audio, normalises the mix to a loudness target and muxes it back without
re-encoding the picture.

Standard library only. FFmpeg/FFprobe are required for planning and rendering; earshot is needed
only for cues that ask it for a sound; the network is used only for Openverse and only when the
caller passes ``--allow-network`` (or ``allow_network=True``).

Commands::

    sound_design.py validate CUES.json
    sound_design.py detect-cuts VIDEO --sound "a soft fast whoosh" -o CUES.json
    sound_design.py search "calm piano" --category music [--licenses cc0,pdm]
    sound_design.py plan CUES.json --video VIDEO
    sound_design.py render CUES.json --video VIDEO -o exports/OUT.mp4 [--allow-network] [--stems]

Credits: earshot (https://github.com/Leonxlnx/earshot, MIT) renders the effects; the cue-to-frame
approach follows Clipwing's real-sfx skill (https://github.com/Clipwing/skills); Openverse
(https://github.com/WordPress/openverse) indexes the openly licensed media. No code or audio from
those projects is vendored here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from array import array
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "1.0.0"
SAMPLE_RATE = 48000
OPENVERSE_API = "https://api.openverse.org/v1/audio/"
USER_AGENT = "video-studio-sound-design/1.0 (+https://github.com/playlikeboy/video-studio)"
MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024
EARSHOT_INSTALL = 'pip install "earshot @ git+https://github.com/Leonxlnx/earshot"'

# Openverse licence codes. Public-domain marks need no attribution; every "by" licence does.
OPENVERSE_LICENSES = {
    "cc0", "pdm", "by", "by-sa", "by-nc", "by-nd", "by-nc-sa", "by-nc-nd", "sampling+",
    "nc-sampling+",
}
DEFAULT_LICENSES = ("cc0", "pdm")
ATTRIBUTION_FREE = {"cc0", "pdm"}
RESTRICTIVE = {"by-nc", "by-nd", "by-nc-sa", "by-nc-nd", "sampling+", "nc-sampling+"}

DEFAULT_SFX_GAIN_DB = -6.0
DEFAULT_MUSIC_GAIN_DB = -18.0
DEFAULT_DUCK = {"thresholdDb": -30.0, "ratio": 8.0, "attackMs": 20.0, "releaseMs": 350.0}
DEFAULT_LOUDNESS = {"integrated": -14.0, "truePeak": -1.5, "lra": 11.0}
SOURCES = ("earshot", "file", "openverse")


class SoundDesignError(ValueError):
    """A cue list, licence or media problem the caller can fix."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SoundDesignError(message)


# --------------------------------------------------------------------------------------------
# Cue lists
# --------------------------------------------------------------------------------------------

def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def parse_time(value: Any) -> float:
    """Seconds from a number or an ``[HH:]MM:SS[.mmm]`` string."""
    if _number(value):
        require(value >= 0, f"time must not be negative: {value}")
        return float(value)
    require(isinstance(value, str) and value.strip(), f"time must be seconds or HH:MM:SS.mmm: {value!r}")
    match = re.fullmatch(r"\s*(?:(\d+):)?(\d{1,2}):(\d{1,2}(?:\.\d+)?)\s*", value)
    if not match:
        try:
            seconds = float(value)
        except ValueError as exc:
            raise SoundDesignError(f"time must be seconds or HH:MM:SS.mmm: {value!r}") from exc
        require(math.isfinite(seconds) and seconds >= 0, f"time must be a non-negative number: {value!r}")
        return seconds
    hours, minutes, seconds = match.groups()
    require(float(seconds) < 60 and (hours is None or int(minutes) < 60), f"invalid clock time: {value!r}")
    return int(hours or 0) * 3600 + int(minutes) * 60 + float(seconds)


def safe_relative(value: Any, label: str) -> str:
    """Reject absolute paths, drive letters and ``..`` so a cue list stays inside its folder."""
    require(isinstance(value, str) and value.strip(), f"{label} must be a non-empty path")
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    require(not path.is_absolute() and ".." not in path.parts
            and not re.match(r"^[A-Za-z]:", normalized), f"{label} must be a safe relative path")
    return normalized


def _validate_openverse(spec: Any, label: str) -> None:
    if isinstance(spec, str):
        require(spec.strip() != "", f"{label} query must not be empty")
        return
    require(isinstance(spec, dict), f"{label} must be a query string or an object")
    require(isinstance(spec.get("q"), str) and spec["q"].strip() or isinstance(spec.get("id"), str),
            f"{label} needs a query (q) or a locked Openverse id")
    licenses = spec.get("licenses")
    if licenses is not None:
        require(isinstance(licenses, list) and licenses, f"{label}.licenses must be a non-empty list")
        unknown = sorted(set(licenses) - OPENVERSE_LICENSES)
        require(not unknown, f"{label}.licenses has unknown code(s): {', '.join(unknown)}")
    for key in ("minDuration", "maxDuration"):
        if key in spec:
            require(_number(spec[key]) and spec[key] > 0, f"{label}.{key} must be positive seconds")


def _validate_source(item: dict[str, Any], label: str) -> str:
    present = [key for key in SOURCES if key in item]
    require(len(present) == 1, f"{label} needs exactly one of {', '.join(SOURCES)}")
    kind = present[0]
    spec = item[kind]
    if kind == "earshot":
        if isinstance(spec, dict):
            require(isinstance(spec.get("want"), str) and spec["want"].strip()
                    or isinstance(spec.get("sound"), str) and spec["sound"].strip(),
                    f"{label}.earshot needs words (want) or a design id (sound)")
            if "seed" in spec:
                require(isinstance(spec["seed"], int) and not isinstance(spec["seed"], bool),
                        f"{label}.earshot.seed must be an integer")
            if "dur" in spec:
                require(_number(spec["dur"]) and spec["dur"] > 0, f"{label}.earshot.dur must be positive")
        else:
            require(isinstance(spec, str) and spec.strip(), f"{label}.earshot must be words or an object")
    elif kind == "file":
        safe_relative(spec, f"{label}.file")
    else:
        _validate_openverse(spec, f"{label}.openverse")
    if "gainDb" in item:
        require(_number(item["gainDb"]) and -60 <= item["gainDb"] <= 24, f"{label}.gainDb must be -60..24")
    return kind


def validate_cue_list(data: Any) -> dict[str, Any]:
    """Validate a cue list and return it. Raises SoundDesignError with a precise location."""
    require(isinstance(data, dict), "cue list must be a JSON object")
    require(data.get("schemaVersion") == SCHEMA_VERSION, f"schemaVersion must be {SCHEMA_VERSION}")
    cues = data.get("cues")
    require(isinstance(cues, list), "cues must be an array")
    ids: set[str] = set()
    for index, cue in enumerate(cues):
        label = f"cues[{index}]"
        require(isinstance(cue, dict), f"{label} must be an object")
        cue_id = cue.get("id", f"cue-{index + 1:03d}")
        require(isinstance(cue_id, str) and cue_id.strip(), f"{label}.id must be a non-empty string")
        require(cue_id not in ids, f"duplicate cue id: {cue_id}")
        ids.add(cue_id)
        has_at, has_frame = "at" in cue, "frame" in cue
        require(has_at != has_frame, f"{label} needs exactly one of at (time) or frame")
        if has_at:
            parse_time(cue["at"])
        else:
            frame = cue["frame"]
            require(isinstance(frame, int) and not isinstance(frame, bool) and frame >= 0,
                    f"{label}.frame must be a non-negative integer")
        _validate_source(cue, label)
        require(cue.get("align", "start") in {"start", "peak"}, f"{label}.align must be start or peak")
        if "duration" in cue:
            require(_number(cue["duration"]) and cue["duration"] > 0, f"{label}.duration must be positive")
    music = data.get("music")
    if music is not None:
        require(isinstance(music, dict), "music must be an object")
        _validate_source(music, "music")
        for key in ("fadeIn", "fadeOut"):
            if key in music:
                require(_number(music[key]) and music[key] >= 0, f"music.{key} must be >= 0 seconds")
        if "start" in music:
            parse_time(music["start"])
    duck = data.get("duck", {})
    require(isinstance(duck, dict), "duck must be an object")
    if "key" in duck:
        safe_relative(duck["key"], "duck.key")
    if "thresholdDb" in duck:
        require(_number(duck["thresholdDb"]) and -60 <= duck["thresholdDb"] <= 0,
                "duck.thresholdDb must be -60..0")
    if "ratio" in duck:
        require(_number(duck["ratio"]) and 1 <= duck["ratio"] <= 20, "duck.ratio must be 1..20")
    for key, high in (("attackMs", 2000), ("releaseMs", 9000)):
        if key in duck:
            require(_number(duck[key]) and 0.01 <= duck[key] <= high, f"duck.{key} must be 0.01..{high}")
    loudness = data.get("loudness", {})
    require(isinstance(loudness, dict), "loudness must be an object")
    for key, low, high in (("integrated", -70, -5), ("truePeak", -9, 0), ("lra", 1, 50)):
        if key in loudness:
            require(_number(loudness[key]) and low <= loudness[key] <= high,
                    f"loudness.{key} must be {low}..{high}")
    original = data.get("original", {})
    require(isinstance(original, dict), "original must be an object")
    if "gainDb" in original:
        require(_number(original["gainDb"]), "original.gainDb must be a number")
    return data


def load_cue_list(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SoundDesignError(f"{path}: invalid JSON: {exc}") from exc
    return validate_cue_list(data)


# --------------------------------------------------------------------------------------------
# Frames and samples
# --------------------------------------------------------------------------------------------

def parse_rate(value: str | float | Fraction) -> Fraction:
    """Exact frame rate from ``30000/1001``, ``25`` or a number."""
    if isinstance(value, Fraction):
        rate = value
    elif isinstance(value, str) and "/" in value:
        num, den = value.split("/", 1)
        require(int(den) != 0, f"invalid frame rate: {value}")
        rate = Fraction(int(num), int(den))
    else:
        rate = Fraction(str(value))
    require(rate > 0, f"frame rate must be positive: {value}")
    return rate


def snap(cue: dict[str, Any], fps: Fraction, sample_rate: int = SAMPLE_RATE) -> dict[str, Any]:
    """The frame a cue lands on, that frame's exact time and its first audio sample."""
    if "frame" in cue:
        frame = int(cue["frame"])
    else:
        frame = int(Fraction(str(parse_time(cue["at"]))) * fps + Fraction(1, 2))
    exact = Fraction(frame) / fps
    sample = int(exact * sample_rate + Fraction(1, 2))
    return {"frame": frame, "time": float(exact), "sample": sample, "timecode": timecode(exact)}


def timecode(seconds: Fraction | float) -> str:
    millis = int(Fraction(str(seconds)) * 1000 + Fraction(1, 2))
    hours, rest = divmod(millis, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    return f"{hours:02d}:{minutes:02d}:{rest // 1000:02d}.{rest % 1000:03d}"


def db_to_linear(db: float) -> float:
    return 10 ** (db / 20)


# --------------------------------------------------------------------------------------------
# FFmpeg helpers
# --------------------------------------------------------------------------------------------

Runner = Callable[..., subprocess.CompletedProcess]


def _run(cmd: list[str], runner: Runner | None = None) -> subprocess.CompletedProcess:
    runner = runner or subprocess.run
    result = runner(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        tail = "\n".join((result.stderr or "").strip().splitlines()[-8:])
        raise SoundDesignError(f"{Path(cmd[0]).name} failed ({result.returncode}): {tail}")
    return result


def tool(name: str) -> str:
    path = shutil.which(name)
    require(path is not None, f"{name} not found on PATH; install FFmpeg first")
    return path  # type: ignore[return-value]


def probe(video: Path, runner: Runner | None = None) -> dict[str, Any]:
    """Duration, exact frame rate and whether the file has audio."""
    result = _run([tool("ffprobe"), "-v", "error", "-print_format", "json", "-show_streams",
                   "-show_format", str(video)], runner)
    data = json.loads(result.stdout or "{}")
    streams = data.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    require(bool(videos), f"{video} has no video stream")
    stream = videos[0]
    rate = stream.get("r_frame_rate") or stream.get("avg_frame_rate") or "0/0"
    if rate in {"0/0", "0"}:
        rate = stream.get("avg_frame_rate", "0/0")
    duration = data.get("format", {}).get("duration") or stream.get("duration")
    require(duration is not None, f"{video}: duration unknown")
    return {
        "duration": float(duration),
        "fps": str(parse_rate(rate)),
        "hasAudio": any(s.get("codec_type") == "audio" for s in streams),
        "width": stream.get("width"),
        "height": stream.get("height"),
    }


SCENE_RE = re.compile(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)")


def parse_scene_times(stderr: str, min_gap: float = 0.5) -> list[float]:
    times: list[float] = []
    for line in stderr.splitlines():
        if "showinfo" not in line:
            continue
        match = SCENE_RE.search(line)
        if match:
            value = float(match.group(1))
            if not times or value - times[-1] >= min_gap:
                times.append(value)
    return times


def detect_cuts(video: Path, threshold: float = 0.35, min_gap: float = 0.5,
                runner: Runner | None = None) -> list[float]:
    """Times of hard cuts from FFmpeg's scene score (no extra dependency)."""
    require(0 < threshold < 1, "threshold must be between 0 and 1")
    vf = f"select='gt(scene\\,{threshold})',showinfo"
    result = _run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", str(video), "-an", "-sn",
                   "-vf", vf, "-f", "null", "-"], runner)
    return parse_scene_times(result.stderr or "", min_gap)


def cues_from_times(times: list[float], sound: str, gain_db: float = -8.0,
                    align: str = "peak") -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "cues": [
            {"id": f"cut-{i + 1:03d}", "at": round(t, 3), "earshot": sound, "gainDb": gain_db,
             "align": align}
            for i, t in enumerate(times)
        ],
    }


LOUDNORM_RE = re.compile(r"\{[^{}]*\"input_i\"[^{}]*\}", re.DOTALL)


def parse_loudnorm(stderr: str) -> dict[str, float]:
    matches = LOUDNORM_RE.findall(stderr or "")
    require(bool(matches), "could not read loudnorm measurement from FFmpeg output")
    raw = json.loads(matches[-1])
    out: dict[str, float] = {}
    for key, value in raw.items():
        try:
            out[key] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def measure_loudness(path: Path, target: dict[str, float], runner: Runner | None = None) -> dict[str, float]:
    af = (f"loudnorm=I={target['integrated']}:TP={target['truePeak']}:LRA={target['lra']}"
          ":print_format=json")
    result = _run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0",
                   "-af", af, "-f", "null", "-"], runner)
    return parse_loudnorm(result.stderr)


def normalize_filter(target: dict[str, float], measured: dict[str, float], sample_rate: int,
                     correction_db: float = 0.0, margin_db: float = 0.5) -> str:
    """Gain to the loudness target measured by loudnorm, then a 4x-oversampled peak ceiling.

    loudnorm's own second pass can overshoot the true-peak target on peaky mixes; a fixed gain
    plus a limiter running at 4x the sample rate keeps the ceiling while matching the loudness
    within a fraction of a LU (the render re-measures and corrects once if needed).
    """
    gain = target["integrated"] - measured["input_i"] + correction_db
    ceiling = max(min(db_to_linear(target["truePeak"] - margin_db), 1.0), 0.0625)
    return (f"volume={gain:.3f}dB,aresample={sample_rate * 4},"
            f"alimiter=limit={ceiling:.6f}:attack=1:release=60:level=disabled,"
            f"aresample={sample_rate}")


def peak_offset(path: Path, sample_rate: int = SAMPLE_RATE, runner: Runner | None = None) -> int:
    """Sample index of the loudest point in the first 30 s of a sound."""
    runner = runner or subprocess.run
    result = runner([tool("ffmpeg"), "-v", "error", "-i", str(path), "-t", "30", "-ac", "1",
                     "-ar", str(sample_rate), "-f", "s16le", "-"], capture_output=True, check=False)
    require(result.returncode == 0, f"could not decode {path}")
    samples = array("h")
    data = result.stdout[: len(result.stdout) // 2 * 2]
    samples.frombytes(data)
    if sys.byteorder == "big":
        samples.byteswap()
    if not samples:
        return 0
    best, index = -1, 0
    for i, value in enumerate(samples):
        magnitude = -value if value < 0 else value
        if magnitude > best:
            best, index = magnitude, i
    return index


# --------------------------------------------------------------------------------------------
# Openverse
# --------------------------------------------------------------------------------------------

Opener = Callable[..., Any]


def _get_json(url: str, opener: Opener | None = None) -> Any:
    opener = opener or urllib.request.urlopen
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with opener(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_licenses(licenses: Any) -> tuple[str, ...]:
    if licenses is None:
        return DEFAULT_LICENSES
    if isinstance(licenses, str):
        licenses = [part.strip() for part in licenses.split(",") if part.strip()]
    values = tuple(str(code).lower() for code in licenses)
    unknown = sorted(set(values) - OPENVERSE_LICENSES)
    require(bool(values) and not unknown, f"unknown licence code(s): {', '.join(unknown) or '(none)'}")
    return values


def licence_ok(item: dict[str, Any], allowed: tuple[str, ...]) -> bool:
    return str(item.get("license", "")).lower() in allowed


def openverse_search(query: str, licenses: Any = None, category: str | None = None,
                     page_size: int = 20, min_duration: float | None = None,
                     max_duration: float | None = None, opener: Opener | None = None) -> list[dict[str, Any]]:
    """Search Openverse audio; results are filtered again locally by licence and duration."""
    allowed = normalize_licenses(licenses)
    params = {"q": query, "license": ",".join(allowed), "page_size": str(page_size), "mature": "false"}
    if category:
        params["category"] = category
    data = _get_json(OPENVERSE_API + "?" + urllib.parse.urlencode(params), opener)
    results = []
    for item in data.get("results", []):
        if not licence_ok(item, allowed):
            continue
        url = str(item.get("url") or "")
        if not url.startswith("https://"):
            continue
        seconds = (item.get("duration") or 0) / 1000
        if min_duration and seconds and seconds < min_duration:
            continue
        if max_duration and seconds and seconds > max_duration:
            continue
        results.append(item)
    return results


def openverse_item(item_id: str, opener: Opener | None = None) -> dict[str, Any]:
    require(re.fullmatch(r"[0-9a-fA-F-]{36}", item_id) is not None, f"invalid Openverse id: {item_id}")
    return _get_json(f"{OPENVERSE_API}{item_id}/", opener)


def credit_for(item: dict[str, Any]) -> dict[str, Any]:
    code = str(item.get("license", "")).lower()
    return {
        "source": "openverse",
        "id": item.get("id"),
        "title": item.get("title"),
        "creator": item.get("creator"),
        "license": code,
        "licenseVersion": item.get("license_version"),
        "licenseUrl": item.get("license_url"),
        "landingUrl": item.get("foreign_landing_url"),
        "provider": item.get("provider"),
        "attribution": item.get("attribution"),
        "attributionRequired": code not in ATTRIBUTION_FREE,
    }


def download(url: str, dest: Path, opener: Opener | None = None) -> Path:
    require(url.startswith("https://"), f"refusing non-HTTPS download: {url}")
    opener = opener or urllib.request.urlopen
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".part")
    total = 0
    with opener(request, timeout=60) as response, partial.open("wb") as handle:
        while True:
            chunk = response.read(1 << 16)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                handle.close()
                partial.unlink(missing_ok=True)
                raise SoundDesignError(f"download larger than {MAX_DOWNLOAD_BYTES // 2**20} MB: {url}")
            handle.write(chunk)
    require(total > 0, f"empty download: {url}")
    partial.replace(dest)
    return dest


def resolve_openverse(spec: Any, work: Path, default_licenses: tuple[str, ...], allow_network: bool,
                      category: str | None, opener: Opener | None = None) -> tuple[Path, dict[str, Any]]:
    spec = {"q": spec} if isinstance(spec, str) else dict(spec)
    allowed = normalize_licenses(spec.get("licenses", list(default_licenses)))
    cache = work / "openverse"
    if spec.get("id"):
        meta_path = cache / f"{spec['id']}.json"
        if meta_path.is_file():
            item = json.loads(meta_path.read_text(encoding="utf-8"))
            cached = cache / item.get("_file", "")
            if item.get("_file") and cached.is_file() and licence_ok(item, allowed):
                return cached, credit_for(item)
    require(allow_network, "Openverse cue needs network access: rerun with --allow-network "
            "(only metadata and the chosen audio file are downloaded; no media is uploaded)")
    if spec.get("id"):
        item = openverse_item(spec["id"], opener)
        require(licence_ok(item, allowed), f"Openverse {spec['id']} is {item.get('license')}, "
                f"not one of {', '.join(allowed)}")
    else:
        search = {"min_duration": spec.get("minDuration"), "max_duration": spec.get("maxDuration"),
                  "opener": opener}
        wanted = spec.get("category", category)
        results = openverse_search(spec["q"], allowed, wanted, **search)
        if not results and wanted:
            # Many providers leave the category empty; retry the same licences without it.
            results = openverse_search(spec["q"], allowed, None, **search)
        index = int(spec.get("index", 0))
        require(len(results) > index, f"no Openverse result for {spec['q']!r} under {', '.join(allowed)}")
        item = results[index]
    ext = re.sub(r"[^a-z0-9]", "", str(item.get("filetype") or "mp3").lower()) or "mp3"
    file_name = f"{item['id']}.{ext}"
    path = download(str(item["url"]), cache / file_name, opener)
    item = dict(item, _file=file_name)
    (cache / f"{item['id']}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    return path, credit_for(item)


# --------------------------------------------------------------------------------------------
# earshot
# --------------------------------------------------------------------------------------------

def earshot_spec(spec: Any) -> dict[str, Any]:
    return {"want": spec} if isinstance(spec, str) else dict(spec)


def earshot_version() -> str | None:
    try:
        from importlib.metadata import version
        return version("earshot")
    except Exception:  # noqa: BLE001 - absent or broken metadata both mean "unknown"
        return None


def find_earshot_bin(binary: str | None = None) -> str | None:
    """An earshot executable: the given one, $EARSHOT_BIN, PATH, then the Video Studio installer's venv."""
    for candidate in (binary, os.environ.get("EARSHOT_BIN"), "earshot"):
        if candidate and shutil.which(candidate):
            return shutil.which(candidate)
    home = Path.home()
    venvs = [
        Path(os.environ.get("XDG_DATA_HOME", str(home / ".local/share"))) / "video-studio" / "venvs",
        home / "Library" / "Application Support" / "VideoStudio" / "venvs",
        Path(os.environ.get("LOCALAPPDATA", str(home))) / "VideoStudio" / "venvs",
    ]
    for base in venvs:
        for exe in (base / "earshot" / "bin" / "earshot", base / "earshot" / "Scripts" / "earshot.exe"):
            if exe.is_file():
                return str(exe)
    return None


def earshot_available(binary: str | None = None) -> bool:
    try:
        import earshot.make  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return find_earshot_bin(binary) is not None


def render_earshot(spec: Any, work: Path, binary: str | None = None,
                   runner: Runner | None = None) -> tuple[Path, dict[str, Any]]:
    """Render (or reuse) one earshot take; returns the WAV path and its credit."""
    spec = earshot_spec(spec)
    key = hashlib.sha256(json.dumps([spec, earshot_version()], sort_keys=True).encode()).hexdigest()[:16]
    out = work / "earshot" / f"{key}.wav"
    meta_path = out.with_suffix(".json")
    if out.is_file() and meta_path.is_file():
        return out, json.loads(meta_path.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    design = spec.get("sound")
    summary = ""
    try:
        from earshot.make import make  # type: ignore[import-not-found]
    except Exception:  # noqa: BLE001 - fall back to the CLI
        make = None
    if make is not None:
        kwargs = {k: spec[k] for k in ("sound", "seed", "dur") if k in spec}
        result = make(spec.get("want"), str(out), **kwargs)
        summary = str(result.get("summary", ""))
        design = result.get("sound") or design
        files = result.get("files") or []
        if files and Path(files[0]) != out and Path(files[0]).is_file():
            shutil.move(files[0], out)
    else:
        exe = find_earshot_bin(binary)
        require(exe is not None, f"earshot is not installed; install it with: {EARSHOT_INSTALL}")
        cmd = [exe, "make"]
        if spec.get("want"):
            cmd.append(spec["want"])
        cmd += ["-o", str(out)]
        if spec.get("sound"):
            cmd += ["--sound", spec["sound"]]
        if "seed" in spec:
            cmd += ["--seed", str(spec["seed"])]
        if "dur" in spec:
            cmd += ["--dur", str(spec["dur"])]
        summary = (_run(cmd, runner).stdout or "").strip().splitlines()[0:1]
        summary = summary[0] if summary else ""
        match = re.search(r":\s*([a-z0-9_]+/[a-z0-9_]+)\s*\(", summary)
        design = match.group(1) if match else design
    require(out.is_file(), f"earshot did not write {out}")
    credit = {
        "source": "earshot",
        "request": spec,
        "design": design,
        "summary": summary,
        "earshotVersion": earshot_version(),
        "license": "rendered output free for any use (earshot MIT; learned from public-domain recordings)",
        "attributionRequired": False,
        "landingUrl": "https://github.com/Leonxlnx/earshot",
    }
    meta_path.write_text(json.dumps(credit, indent=2), encoding="utf-8")
    return out, credit


# --------------------------------------------------------------------------------------------
# Planning and the filter graph
# --------------------------------------------------------------------------------------------

def plan(data: dict[str, Any], media: dict[str, Any], fps_override: str | None = None,
         sample_rate: int = SAMPLE_RATE) -> dict[str, Any]:
    """Resolve every cue to a frame and sample without touching the network or rendering audio."""
    validate_cue_list(data)
    fps = parse_rate(fps_override or media["fps"])
    duration = float(media["duration"])
    cues, warnings = [], []
    for index, cue in enumerate(data["cues"]):
        placed = snap(cue, fps, sample_rate)
        kind = next(k for k in SOURCES if k in cue)
        entry = {
            "id": cue.get("id", f"cue-{index + 1:03d}"),
            **placed,
            "source": kind,
            "spec": cue[kind],
            "gainDb": float(cue.get("gainDb", DEFAULT_SFX_GAIN_DB)),
            "align": cue.get("align", "start"),
        }
        if "duration" in cue:
            entry["duration"] = float(cue["duration"])
        if placed["time"] >= duration:
            warnings.append(f"{entry['id']} at {placed['timecode']} is after the end of the video; skipped")
            entry["skipped"] = True
        cues.append(entry)
    duck = {**DEFAULT_DUCK, **data.get("duck", {})}
    duck.setdefault("enabled", True)
    music = data.get("music")
    if music is not None:
        kind = next(k for k in SOURCES if k in music)
        music = {
            "source": kind,
            "spec": music[kind],
            "gainDb": float(music.get("gainDb", DEFAULT_MUSIC_GAIN_DB)),
            "fadeIn": float(music.get("fadeIn", 1.0)),
            "fadeOut": float(music.get("fadeOut", 2.0)),
            "loop": bool(music.get("loop", True)),
            "start": parse_time(music.get("start", 0)),
        }
    original = {"keep": bool(data.get("original", {}).get("keep", True)),
                "gainDb": float(data.get("original", {}).get("gainDb", 0.0))}
    if music and duck["enabled"] and not (media.get("hasAudio") and original["keep"]) and "key" not in duck:
        warnings.append("music ducking needs the video's own audio or duck.key; ducking is off")
        duck["enabled"] = False
    return {
        "fps": str(fps),
        "duration": duration,
        "sampleRate": sample_rate,
        "hasAudio": bool(media.get("hasAudio")),
        "cues": cues,
        "music": music,
        "duck": duck,
        "original": original,
        "loudness": {**DEFAULT_LOUDNESS, **data.get("loudness", {})},
        "warnings": warnings,
    }


def _fmt(sample_rate: int) -> str:
    return f"aresample={sample_rate},aformat=sample_fmts=fltp:channel_layouts=stereo"


def build_mix_command(resolved: dict[str, Any], video: Path, out_wav: Path,
                      stem_wav: Path | None = None) -> list[str]:
    """One FFmpeg call that places every sound on its sample, ducks music and sums the mix."""
    sr, dur = resolved["sampleRate"], resolved["duration"]
    inputs: list[str] = ["-i", str(video)]
    graph: list[str] = [f"aevalsrc=0|0:s={sr}:c=stereo:d={dur:.6f}[bed]"]
    mix_labels = ["[bed]"]
    next_input = 1

    original = resolved["original"]
    use_original = resolved["hasAudio"] and original["keep"]
    music = resolved.get("music")
    duck = resolved["duck"]
    duck_on = bool(music and duck.get("enabled"))
    key_label = None
    if use_original:
        chain = f"[0:a:0]{_fmt(sr)},volume={original['gainDb']}dB,apad=whole_dur={dur:.6f}"
        if duck_on and not duck.get("keyPath"):
            graph.append(chain + ",asplit=2[orig][key]")
            key_label = "[key]"
        else:
            graph.append(chain + "[orig]")
        mix_labels.append("[orig]")

    sfx_labels = []
    for cue in resolved["cues"]:
        if cue.get("skipped"):
            continue
        inputs += ["-i", str(cue["path"])]
        delay = int(cue["sample"]) - int(cue.get("peakSample", 0) if cue["align"] == "peak" else 0)
        head = 0
        if delay < 0:
            head, delay = -delay, 0
        chain = f"[{next_input}:a:0]{_fmt(sr)}"
        if head or "duration" in cue:
            end = f":end_sample={head + int(cue['duration'] * sr)}" if "duration" in cue else ""
            chain += f",atrim=start_sample={head}{end},asetpts=N/SR/TB"
        chain += f",volume={cue['gainDb']}dB,adelay=delays={delay}S:all=1"
        label = f"[s{len(sfx_labels)}]"
        graph.append(chain + label)
        sfx_labels.append(label)
        next_input += 1
    if sfx_labels:
        if stem_wav is not None:
            graph.append("".join(sfx_labels) + f"amix=inputs={len(sfx_labels)}:normalize=0"
                         ":dropout_transition=0,asplit=2[sfx][sfxstem]")
        else:
            graph.append("".join(sfx_labels) + f"amix=inputs={len(sfx_labels)}:normalize=0"
                         ":dropout_transition=0[sfx]")
        mix_labels.append("[sfx]")

    if music:
        if music["loop"]:
            inputs += ["-stream_loop", "-1"]
        inputs += ["-i", str(music["path"])]
        length = max(dur - music["start"], 0.01)
        chain = f"[{next_input}:a:0]{_fmt(sr)},atrim=0:{length:.6f},asetpts=N/SR/TB"
        if music["fadeIn"] > 0:
            chain += f",afade=t=in:d={music['fadeIn']}"
        if music["fadeOut"] > 0:
            chain += f",afade=t=out:st={max(length - music['fadeOut'], 0):.6f}:d={music['fadeOut']}"
        chain += f",volume={music['gainDb']}dB"
        if music["start"] > 0:
            chain += f",adelay=delays={round(music['start'] * sr)}S:all=1"
        next_input += 1
        if duck_on:
            if duck.get("keyPath"):
                inputs += ["-i", str(duck["keyPath"])]
                graph.append(f"[{next_input}:a:0]{_fmt(sr)},apad=whole_dur={dur:.6f}[key]")
                key_label = "[key]"
                next_input += 1
            threshold = max(min(db_to_linear(duck["thresholdDb"]), 1.0), 0.000976563)
            graph.append(chain + "[mus0]")
            graph.append(f"[mus0]{key_label}sidechaincompress=threshold={threshold:.6f}"
                         f":ratio={duck['ratio']}:attack={duck['attackMs']}:release={duck['releaseMs']}"
                         "[mus]")
        else:
            graph.append(chain + "[mus]")
        mix_labels.append("[mus]")

    graph.append("".join(mix_labels) + f"amix=inputs={len(mix_labels)}:duration=first:normalize=0"
                 f":dropout_transition=0,atrim=0:{dur:.6f}[mix]")
    cmd = [tool("ffmpeg"), "-hide_banner", "-nostats", "-y", *inputs,
           "-filter_complex", ";".join(graph),
           "-map", "[mix]", "-c:a", "pcm_s24le", "-ar", str(sr), str(out_wav)]
    if stem_wav is not None and sfx_labels:
        cmd += ["-map", "[sfxstem]", "-c:a", "pcm_s24le", "-ar", str(sr), str(stem_wav)]
    return cmd


def write_credits(path: Path, credits: list[dict[str, Any]]) -> None:
    lines = ["# Sound credits", "",
             "Generated by Video Studio sound design. Keep this file with the video; credit every",
             "item marked *attribution required* wherever the video is published.", ""]
    for credit in credits:
        where = f"`{credit.get('cue', 'music')}`"
        if credit["source"] == "openverse":
            text = credit.get("attribution") or (
                f"\"{credit.get('title')}\" by {credit.get('creator')} ({credit.get('license')})")
            need = "attribution required" if credit["attributionRequired"] else "no attribution required"
            lines.append(f"- {where}: {text} Source: {credit.get('landingUrl')} via Openverse. *{need}*")
        elif credit["source"] == "earshot":
            lines.append(f"- {where}: rendered with earshot {credit.get('earshotVersion') or ''}".rstrip()
                         + f" ({credit.get('design') or 'design chosen by words'}); "
                         "https://github.com/Leonxlnx/earshot. *no attribution required*")
        else:
            lines.append(f"- {where}: local file `{credit.get('file')}`; licence: "
                         f"{credit.get('license') or 'not recorded - verify before publishing'}")
    lines += ["", "Tools: earshot (MIT, Leon Lin), Openverse (WordPress), approach after Clipwing real-sfx."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_assets(resolved: dict[str, Any], data: dict[str, Any], base: Path, work: Path, *,
                   allow_network: bool, licenses: tuple[str, ...], earshot_bin: str | None,
                   runner: Runner | None = None, opener: Opener | None = None) -> list[dict[str, Any]]:
    """Render, fetch or locate every sound; fills in paths and returns the credits."""
    credits: list[dict[str, Any]] = []

    def locate(kind: str, spec: Any, category: str | None, cue_id: str, extra: dict[str, Any]) -> Path:
        if kind == "earshot":
            path, credit = render_earshot(spec, work, earshot_bin, runner)
        elif kind == "openverse":
            path, credit = resolve_openverse(spec, work, licenses, allow_network, category, opener)
        else:
            path = (base / safe_relative(spec, "file")).resolve()
            require(path.is_file(), f"{cue_id}: file not found: {spec}")
            credit = {"source": "file", "file": spec, "license": extra.get("license"),
                      "attributionRequired": None}
        credits.append({"cue": cue_id, **credit})
        return path

    cues_by_id = {c.get("id", f"cue-{i + 1:03d}"): c for i, c in enumerate(data["cues"])}
    for cue in resolved["cues"]:
        if cue.get("skipped"):
            continue
        cue["path"] = str(locate(cue["source"], cue["spec"], None, cue["id"], cues_by_id[cue["id"]]))
        if cue["align"] == "peak":
            cue["peakSample"] = peak_offset(Path(cue["path"]), resolved["sampleRate"], runner)
    if resolved.get("music"):
        music = resolved["music"]
        music["path"] = str(locate(music["source"], music["spec"], "music", "music", data["music"]))
    if resolved["duck"].get("key"):
        key = (base / safe_relative(resolved["duck"]["key"], "duck.key")).resolve()
        require(key.is_file(), f"duck.key not found: {resolved['duck']['key']}")
        resolved["duck"]["keyPath"] = str(key)
    return credits


def render(cue_path: Path, video: Path, output: Path, *, allow_network: bool = False,
           licenses: Any = None, stems: bool = False, overwrite: bool = False,
           fps: str | None = None, work: Path | None = None, earshot_bin: str | None = None,
           runner: Runner | None = None, opener: Opener | None = None) -> dict[str, Any]:
    video, output = video.resolve(), output.resolve()
    require(video.is_file(), f"video not found: {video}")
    require(output != video, "output must not overwrite the source video")
    require(overwrite or not output.exists(), f"{output} exists; pass --overwrite to replace it")
    data = load_cue_list(cue_path)
    allowed = normalize_licenses(licenses)
    for code in sorted(set(allowed) & RESTRICTIVE):
        print(f"warning: licence {code} restricts commercial use or adaptation; check before publishing",
              file=sys.stderr)
    media = probe(video, runner)
    resolved = plan(data, media, fps)
    work = (work or output.parent / "cache" / "sound-design" / output.stem).resolve()
    work.mkdir(parents=True, exist_ok=True)
    credits = resolve_assets(resolved, data, cue_path.resolve().parent, work,
                             allow_network=allow_network, licenses=allowed, earshot_bin=earshot_bin,
                             runner=runner, opener=opener)
    mix_wav, norm_wav = work / "mix.wav", work / "mix.norm.wav"
    stem_wav = output.with_name(output.stem + ".sfx.wav") if stems else None
    _run(build_mix_command(resolved, video, mix_wav, stem_wav), runner)

    target = resolved["loudness"]
    measured = measure_loudness(mix_wav, target, runner)
    pcm = output.suffix.lower() in {".mov", ".mkv"}
    margin = 0.3 if pcm else 1.5  # AAC overshoots the ceiling it is given by about a dB
    if math.isfinite(measured.get("input_i", float("-inf"))) and measured.get("input_i", -99) > -70:
        correction = 0.0
        for _ in range(2):
            _run([tool("ffmpeg"), "-hide_banner", "-nostats", "-y", "-i", str(mix_wav),
                  "-af", normalize_filter(target, measured, resolved["sampleRate"], correction, margin),
                  "-c:a", "pcm_s24le", str(norm_wav)], runner)
            error = target["integrated"] - measure_loudness(norm_wav, target, runner)["input_i"]
            if abs(error) <= 0.3:
                break
            correction += error  # the limiter took some loudness; push once more
    else:
        resolved["warnings"].append("mix is silent; loudness normalisation skipped")
        shutil.copyfile(mix_wav, norm_wav)

    output.parent.mkdir(parents=True, exist_ok=True)
    codec = ["-c:a", "pcm_s24le"] if pcm else [
        "-c:a", "aac", "-b:a", "256k"]
    _run([tool("ffmpeg"), "-hide_banner", "-nostats", "-y", "-i", str(video), "-i", str(norm_wav),
          "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", *codec, "-ar", str(resolved["sampleRate"]),
          "-t", f"{resolved['duration']:.6f}", "-movflags", "+faststart", str(output)], runner)

    final = measure_loudness(output, target, runner)
    credits_path = output.with_name(output.stem + ".credits.md")
    write_credits(credits_path, credits)
    report = {
        "output": str(output),
        "sfxStem": str(stem_wav) if stem_wav else None,
        "credits": str(credits_path),
        "fps": resolved["fps"],
        "duration": resolved["duration"],
        "cues": resolved["cues"],
        "music": resolved["music"],
        "duck": resolved["duck"],
        "loudness": {"target": target, "mixBefore": measured.get("input_i"),
                     "output": final.get("input_i"), "outputTruePeak": final.get("input_tp")},
        "attributionRequired": any(c.get("attributionRequired") for c in credits),
        "creditsDetail": credits,
        "warnings": resolved["warnings"],
    }
    if final.get("input_i") is not None and abs(final["input_i"] - target["integrated"]) > 1.0 \
            and measured.get("input_i", -99) > -70:
        report["warnings"].append(
            f"output loudness {final['input_i']:.1f} LUFS is more than 1 LU from the target")
    if final.get("input_tp") is not None and final["input_tp"] > target["truePeak"] + 0.5:
        report["warnings"].append(
            f"output true peak {final['input_tp']:.1f} dBTP is over the {target['truePeak']} dBTP "
            "target (lossy encoders overshoot; lower loudness.truePeak or deliver .mov/.mkv PCM)")
    output.with_name(output.stem + ".sound-design.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    return report


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="check a cue list")
    p.add_argument("cues", type=Path)

    p = sub.add_parser("plan", help="resolve cues to frames and samples (no network, no rendering)")
    p.add_argument("cues", type=Path)
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--fps", help="override the probed frame rate, e.g. 30000/1001")

    p = sub.add_parser("detect-cuts", help="draft a cue list from hard cuts")
    p.add_argument("video", type=Path)
    p.add_argument("--sound", default="a short soft whoosh", help="earshot words for each cut")
    p.add_argument("--threshold", type=float, default=0.35)
    p.add_argument("--min-gap", type=float, default=0.5)
    p.add_argument("--gain-db", type=float, default=-8.0)
    p.add_argument("-o", "--output", type=Path, help="write the cue list here (default: stdout)")

    p = sub.add_parser("search", help="search Openverse for openly licensed audio")
    p.add_argument("query")
    p.add_argument("--licenses", default=",".join(DEFAULT_LICENSES))
    p.add_argument("--category", choices=("music", "sound_effect", "podcast", "audiobook", "news",
                                          "pronunciation"))
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("render", help="render the sound design and mux it into a new video")
    p.add_argument("cues", type=Path)
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--allow-network", action="store_true", help="allow Openverse search and download")
    p.add_argument("--licenses", default=",".join(DEFAULT_LICENSES),
                   help="Openverse licence codes to accept (default cc0,pdm; add by for CC BY)")
    p.add_argument("--stems", action="store_true", help="also write the SFX bus as OUTPUT.sfx.wav")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--fps")
    p.add_argument("--work", type=Path, help="cache folder (default: OUTPUT_DIR/cache/sound-design/NAME)")
    p.add_argument("--earshot-bin", help="earshot executable when it lives in another environment")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            data = load_cue_list(args.cues)
            print(f"OK   {args.cues} ({len(data['cues'])} cue(s))")
        elif args.command == "plan":
            data = load_cue_list(args.cues)
            print(json.dumps(plan(data, probe(args.video), args.fps), indent=2))
        elif args.command == "detect-cuts":
            draft = cues_from_times(detect_cuts(args.video, args.threshold, args.min_gap),
                                    args.sound, args.gain_db)
            text = json.dumps(draft, indent=2) + "\n"
            if args.output:
                args.output.write_text(text, encoding="utf-8")
                print(f"{len(draft['cues'])} cut(s) -> {args.output}")
            else:
                print(text, end="")
        elif args.command == "search":
            rows = openverse_search(args.query, args.licenses, args.category)[: args.limit]
            print(json.dumps([{**credit_for(r), "duration": (r.get("duration") or 0) / 1000,
                               "url": r.get("url")} for r in rows], indent=2))
        else:
            report = render(args.cues, args.video, args.output, allow_network=args.allow_network,
                            licenses=args.licenses, stems=args.stems, overwrite=args.overwrite,
                            fps=args.fps, work=args.work, earshot_bin=args.earshot_bin)
            print(json.dumps({k: report[k] for k in ("output", "sfxStem", "credits", "loudness",
                                                     "attributionRequired", "warnings")}, indent=2))
    except (SoundDesignError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
