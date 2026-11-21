import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from array import array
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "video-studio" / "scripts"))
import sound_design as sd

EXAMPLE = ROOT / "examples" / "sound-design" / "cues.json"
HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
HAS_EARSHOT = importlib.util.find_spec("earshot") is not None
MEDIA = {"duration": 4.0, "fps": "30000/1001", "hasAudio": True}


def no_network(*_args, **_kwargs):
    raise AssertionError("tests must not touch the network")


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def openverse_item(item_id="0" * 8 + "-0000-0000-0000-" + "0" * 12, license="cc0", url=None,
                   duration=1500):
    return {
        "id": item_id,
        "title": "Door Knock",
        "creator": "someone",
        "license": license,
        "license_version": "1.0" if license == "cc0" else "4.0",
        "license_url": f"https://creativecommons.org/licenses/{license}/",
        "foreign_landing_url": "https://example.org/sound/1",
        "url": url or "https://cdn.example.org/1.mp3",
        "filetype": "mp3",
        "duration": duration,
        "provider": "freesound",
        "attribution": f'"Door Knock" by someone is licensed under {license}.',
    }


class FakeOpener:
    """Serves Openverse JSON for API URLs and bytes for everything else; records requests."""

    def __init__(self, results=(), item=None, payload=b"ID3fakeaudio"):
        self.results, self.item, self.payload, self.urls = list(results), item, payload, []

    def __call__(self, request, timeout=None):
        url = request.full_url
        self.urls.append(url)
        if url.startswith(sd.OPENVERSE_API + "?"):
            return FakeResponse(json.dumps({"results": self.results}).encode())
        if url.startswith(sd.OPENVERSE_API):
            return FakeResponse(json.dumps(self.item).encode())
        return FakeResponse(self.payload)


class CueListTests(unittest.TestCase):
    def setUp(self):
        guard = patch("urllib.request.urlopen", side_effect=no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_example_cue_list_is_valid(self):
        data = sd.load_cue_list(EXAMPLE)
        self.assertGreaterEqual(len(data["cues"]), 3)
        self.assertEqual({next(k for k in sd.SOURCES if k in c) for c in data["cues"]} >= {"earshot"}, True)

    def test_parse_time_accepts_seconds_and_clock_strings(self):
        self.assertEqual(sd.parse_time(1.5), 1.5)
        self.assertEqual(sd.parse_time("2.25"), 2.25)
        self.assertAlmostEqual(sd.parse_time("00:01.500"), 1.5)
        self.assertAlmostEqual(sd.parse_time("01:02:03.250"), 3723.25)
        for bad in ("-1", "soon", "00:75.0", -0.1, True):
            with self.subTest(bad=bad), self.assertRaises(sd.SoundDesignError):
                sd.parse_time(bad)

    def test_rejects_unsafe_file_paths(self):
        for path in ("../outside.wav", "/etc/passwd", "C:/media/x.wav", "a/../../b.wav"):
            data = {"schemaVersion": "1.0.0", "cues": [{"at": 0, "file": path}]}
            with self.subTest(path=path), self.assertRaisesRegex(sd.SoundDesignError, "safe relative"):
                sd.validate_cue_list(data)

    def test_rejects_ambiguous_or_incomplete_cues(self):
        cases = [
            ({"at": 0, "earshot": "pop", "file": "x.wav"}, "exactly one of earshot"),
            ({"at": 0}, "exactly one of earshot"),
            ({"at": 0, "frame": 3, "earshot": "pop"}, "exactly one of at"),
            ({"frame": -1, "earshot": "pop"}, "non-negative integer"),
            ({"at": 0, "earshot": "pop", "align": "middle"}, "start or peak"),
            ({"at": 0, "openverse": {"q": "x", "licenses": ["cc-weird"]}}, "unknown code"),
            ({"at": 0, "earshot": "pop", "gainDb": 99}, "gainDb"),
        ]
        for cue, message in cases:
            with self.subTest(cue=cue), self.assertRaisesRegex(sd.SoundDesignError, message):
                sd.validate_cue_list({"schemaVersion": "1.0.0", "cues": [cue]})

    def test_rejects_duplicate_ids_and_wrong_schema(self):
        with self.assertRaisesRegex(sd.SoundDesignError, "duplicate cue id"):
            sd.validate_cue_list({"schemaVersion": "1.0.0", "cues": [
                {"id": "a", "at": 0, "earshot": "pop"}, {"id": "a", "at": 1, "earshot": "pop"}]})
        with self.assertRaisesRegex(sd.SoundDesignError, "schemaVersion"):
            sd.validate_cue_list({"schemaVersion": "2", "cues": []})


class TimingTests(unittest.TestCase):
    def test_snaps_to_exact_ntsc_frames_and_samples(self):
        fps = sd.parse_rate("30000/1001")
        placed = sd.snap({"at": 2.0}, fps)
        self.assertEqual(placed["frame"], 60)
        self.assertEqual(Fraction(placed["time"]).limit_denominator(100000), Fraction(1001, 500))
        self.assertEqual(placed["sample"], 96096)
        self.assertEqual(placed["timecode"], "00:00:02.002")

    def test_frame_cues_are_used_as_given(self):
        placed = sd.snap({"frame": 25}, sd.parse_rate("25"))
        self.assertEqual((placed["frame"], placed["time"], placed["sample"]), (25, 1.0, 48000))

    def test_plan_skips_cues_after_the_end_and_disables_ducking_without_a_key(self):
        data = {"schemaVersion": "1.0.0",
                "cues": [{"id": "late", "at": 9, "earshot": "pop"}],
                "music": {"file": "bed.wav"}}
        resolved = sd.plan(data, {**MEDIA, "hasAudio": False})
        self.assertTrue(resolved["cues"][0]["skipped"])
        self.assertFalse(resolved["duck"]["enabled"])
        self.assertEqual(len(resolved["warnings"]), 2)
        self.assertEqual(resolved["loudness"]["integrated"], -14.0)


class FilterGraphTests(unittest.TestCase):
    def setUp(self):
        stub = patch.object(sd, "tool", side_effect=lambda name: name)
        stub.start()
        self.addCleanup(stub.stop)

    def resolved(self, **overrides):
        data = {"schemaVersion": "1.0.0", "cues": [
            {"id": "hit", "at": 2.0, "earshot": "a hit", "align": "peak"},
            {"id": "tick", "frame": 0, "file": "tick.wav", "duration": 0.25, "gainDb": -12},
        ], "music": {"file": "bed.wav", "gainDb": -20}}
        data.update(overrides)
        resolved = sd.plan(data, MEDIA)
        resolved["cues"][0].update(path="hit.wav", peakSample=4800)
        resolved["cues"][1].update(path="tick.wav")
        if resolved["music"]:
            resolved["music"]["path"] = "bed.wav"
        return resolved

    def test_places_sounds_on_samples_and_ducks_music_under_the_original(self):
        cmd = sd.build_mix_command(self.resolved(), Path("in.mp4"), Path("mix.wav"), Path("sfx.wav"))
        graph = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("adelay=delays=91296S:all=1", graph)  # 96096 minus the 4800-sample peak
        self.assertIn("atrim=start_sample=0:end_sample=12000", graph)
        self.assertIn("volume=-12.0dB", graph)
        self.assertIn("[0:a:0]", graph)
        self.assertIn("asplit=2[orig][key]", graph)
        self.assertIn("[mus0][key]sidechaincompress=threshold=0.031623:ratio=8.0", graph)
        self.assertIn("amix=inputs=4:duration=first:normalize=0", graph)
        self.assertIn("aevalsrc=0|0:s=48000:c=stereo:d=4.000000[bed]", graph)
        self.assertEqual(cmd[cmd.index("bed.wav") - 3:cmd.index("bed.wav")], ["-stream_loop", "-1", "-i"])
        self.assertIn("[sfxstem]", cmd)
        self.assertTrue(all("tick.wav" != part or cmd[i - 1] == "-i" for i, part in enumerate(cmd)))

    def test_peak_alignment_before_zero_trims_the_head(self):
        resolved = self.resolved()
        resolved["cues"][0].update(sample=1000, peakSample=4800)
        graph = sd.build_mix_command(resolved, Path("in.mp4"), Path("mix.wav"))
        self.assertIn("atrim=start_sample=3800,asetpts=N/SR/TB", graph[graph.index("-filter_complex") + 1])

    def test_without_music_there_is_no_compressor(self):
        resolved = self.resolved(music=None)
        cmd = sd.build_mix_command(resolved, Path("in.mp4"), Path("mix.wav"))
        graph = cmd[cmd.index("-filter_complex") + 1]
        self.assertNotIn("sidechaincompress", graph)
        self.assertIn("[0:a:0]", graph)

    def test_normalisation_gain_and_ceiling(self):
        target = {"integrated": -14.0, "truePeak": -1.5, "lra": 11.0}
        chain = sd.normalize_filter(target, {"input_i": -20.0}, 48000, margin_db=0.5)
        self.assertTrue(chain.startswith("volume=6.000dB,aresample=192000,alimiter=limit=0.794328"))
        self.assertTrue(chain.endswith("aresample=48000"))


class ParserTests(unittest.TestCase):
    def test_reads_loudnorm_json_from_ffmpeg_log(self):
        log = ('[Parsed_loudnorm_0 @ 0x1] \n{\n\t"input_i" : "-23.51",\n\t"input_tp" : "-4.20",\n'
               '\t"input_lra" : "3.10",\n\t"input_thresh" : "-33.9",\n\t"target_offset" : "0.4"\n}\n')
        measured = sd.parse_loudnorm(log)
        self.assertEqual(measured["input_i"], -23.51)
        self.assertEqual(measured["target_offset"], 0.4)
        with self.assertRaises(sd.SoundDesignError):
            sd.parse_loudnorm("no json here")

    def test_scene_times_and_draft_cues(self):
        log = "\n".join([
            "[Parsed_showinfo_1 @ 0x] n:   0 pts:  60060 pts_time:2.002   duration:1001",
            "[Parsed_showinfo_1 @ 0x] n:   1 pts:  63063 pts_time:2.1021  duration:1001",
            "[Parsed_showinfo_1 @ 0x] n:   2 pts: 120120 pts_time:4.004   duration:1001",
            "frame=  120 fps=0.0 q=-0.0 size=N/A time=00:00:04.00",
        ])
        times = sd.parse_scene_times(log, min_gap=0.5)
        self.assertEqual(times, [2.002, 4.004])
        draft = sd.cues_from_times(times, "a soft whoosh")
        sd.validate_cue_list(draft)
        self.assertEqual(draft["cues"][1]["id"], "cut-002")
        self.assertEqual(draft["cues"][0]["align"], "peak")


class OpenverseTests(unittest.TestCase):
    def setUp(self):
        guard = patch("urllib.request.urlopen", side_effect=no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_search_sends_licence_filter_and_rechecks_results_locally(self):
        opener = FakeOpener(results=[
            openverse_item(license="by"),                       # not allowed by default
            openverse_item(url="http://insecure.example/1.mp3"),  # not HTTPS
            openverse_item(duration=90_000),                    # too long
            openverse_item(),
        ])
        rows = sd.openverse_search("door knock", max_duration=10, opener=opener)
        self.assertEqual(len(rows), 1)
        self.assertIn("license=cc0%2Cpdm", opener.urls[0])
        self.assertIn("q=door+knock", opener.urls[0])
        self.assertTrue(opener.urls[0].startswith("https://api.openverse.org/v1/audio/?"))

    def test_network_needs_explicit_permission(self):
        with tempfile.TemporaryDirectory() as temp, \
                self.assertRaisesRegex(sd.SoundDesignError, "--allow-network"):
            sd.resolve_openverse("door knock", Path(temp), sd.DEFAULT_LICENSES, False, None,
                                 FakeOpener(results=[openverse_item()]))

    def test_cc_by_download_records_attribution_and_reuses_the_cache(self):
        item = openverse_item(license="by")
        opener = FakeOpener(results=[item])
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            path, credit = sd.resolve_openverse({"q": "door knock", "licenses": ["by"]}, work,
                                                sd.DEFAULT_LICENSES, True, None, opener)
            self.assertEqual(path.read_bytes(), b"ID3fakeaudio")
            self.assertTrue(credit["attributionRequired"])
            self.assertIn("licensed under by", credit["attribution"])
            credits = work / "credits.md"
            sd.write_credits(credits, [{"cue": "knock", **credit}])
            text = credits.read_text(encoding="utf-8")
            self.assertIn("attribution required", text)
            self.assertIn("https://example.org/sound/1", text)
            # A locked id is served from the cache without the network.
            again, _ = sd.resolve_openverse({"id": item["id"], "licenses": ["by"]}, work,
                                            sd.DEFAULT_LICENSES, False, None, FakeOpener())
            self.assertEqual(again, path)

    def test_locked_id_with_a_disallowed_licence_is_refused(self):
        item = openverse_item(license="by-nc")
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(sd.SoundDesignError, "not one of"):
            sd.resolve_openverse({"id": item["id"]}, Path(temp), sd.DEFAULT_LICENSES, True, None,
                                 FakeOpener(item=item))

    def test_empty_category_falls_back_to_an_uncategorised_search(self):
        class CategoryOpener(FakeOpener):
            def __call__(self, request, timeout=None):
                if "category=" in request.full_url:
                    self.urls.append(request.full_url)
                    return FakeResponse(b'{"results": []}')
                return super().__call__(request, timeout)

        opener = CategoryOpener(results=[openverse_item()])
        with tempfile.TemporaryDirectory() as temp:
            path, _ = sd.resolve_openverse({"q": "knock", "category": "sound_effect"}, Path(temp),
                                           sd.DEFAULT_LICENSES, True, None, opener)
            self.assertTrue(path.is_file())
        self.assertIn("category=sound_effect", opener.urls[0])
        self.assertNotIn("category=", opener.urls[1])

    def test_download_rejects_oversized_and_insecure_files(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "x.mp3"
            with patch.object(sd, "MAX_DOWNLOAD_BYTES", 4), \
                    self.assertRaisesRegex(sd.SoundDesignError, "larger than"):
                sd.download("https://cdn.example.org/x.mp3", dest, FakeOpener(payload=b"0123456789"))
            self.assertFalse(dest.exists())
            self.assertFalse(dest.with_name("x.mp3.part").exists())
            with self.assertRaisesRegex(sd.SoundDesignError, "non-HTTPS"):
                sd.download("http://cdn.example.org/x.mp3", dest, FakeOpener())

    def test_unknown_licence_codes_are_rejected(self):
        with self.assertRaises(sd.SoundDesignError):
            sd.normalize_licenses("cc0,all-rights-reserved")
        self.assertEqual(sd.normalize_licenses(None), ("cc0", "pdm"))


class CliTests(unittest.TestCase):
    def test_validate_command(self):
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertEqual(sd.main(["validate", str(EXAMPLE)]), 0)
        self.assertIn("OK", out.getvalue())

    def test_render_refuses_to_overwrite_the_source(self):
        with tempfile.TemporaryDirectory() as temp:
            video = Path(temp) / "in.mp4"
            video.write_bytes(b"x")
            with self.assertRaisesRegex(sd.SoundDesignError, "overwrite the source"):
                sd.render(EXAMPLE, video, video)


def make_test_media(folder: Path) -> Path:
    video = folder / "in.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=160x120:r=30000/1001:d=3",
        "-f", "lavfi", "-i", "sine=f=220:d=3:sample_rate=48000",
        "-af", "volume=0.25", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-shortest", str(video)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=f=1000:d=0.05:sample_rate=48000", str(folder / "click.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "anoisesrc=d=5:c=pink:a=0.2", str(folder / "bed.wav")], check=True)
    return video


def peak_time(path: Path, start: float, length: float) -> float:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(length), "-i", str(path),
                          "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True,
                         check=True).stdout
    samples = array("h")
    samples.frombytes(raw[: len(raw) // 2 * 2])
    index = max(range(len(samples)), key=lambda i: abs(samples[i]))
    return start + index / 48000


@unittest.skipUnless(HAS_FFMPEG, "FFmpeg is not installed")
class RenderIntegrationTests(unittest.TestCase):
    def test_renders_frame_accurate_mix_at_target_loudness(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            video = make_test_media(folder)
            cues = folder / "cues.json"
            cues.write_text(json.dumps({
                "schemaVersion": "1.0.0",
                "cues": [{"id": "click", "at": 1.5, "file": "click.wav", "gainDb": 0}],
                "music": {"file": "bed.wav", "gainDb": -24, "fadeIn": 0.2, "fadeOut": 0.5},
                "loudness": {"integrated": -14, "truePeak": -1.5},
            }), encoding="utf-8")
            out = folder / "exports" / "out.mov"
            report = sd.render(cues, video, out, stems=True)
            self.assertTrue(out.is_file())
            self.assertLessEqual(abs(report["loudness"]["output"] + 14), 1.0)
            self.assertLessEqual(report["loudness"]["outputTruePeak"], -1.0)
            cue = report["cues"][0]
            self.assertEqual(cue["frame"], 45)  # 1.5 s at 29.97 fps
            stem = Path(report["sfxStem"])
            self.assertAlmostEqual(peak_time(stem, 1.0, 1.0), cue["time"], delta=0.06)
            probe = sd.probe(out)
            self.assertAlmostEqual(probe["duration"], sd.probe(video)["duration"], delta=0.1)
            self.assertTrue((folder / "exports" / "out.credits.md").is_file())
            self.assertTrue((folder / "exports" / "out.sound-design.json").is_file())

    def test_detect_cuts_finds_a_hard_cut(self):
        with tempfile.TemporaryDirectory() as temp:
            video = Path(temp) / "cut.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-y",
                "-f", "lavfi", "-i", "color=c=red:s=160x120:r=25:d=1",
                "-f", "lavfi", "-i", "color=c=blue:s=160x120:r=25:d=1",
                "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)], check=True)
            times = sd.detect_cuts(video)
            self.assertEqual(len(times), 1)
            self.assertAlmostEqual(times[0], 1.0, delta=0.05)


@unittest.skipUnless(HAS_FFMPEG and HAS_EARSHOT, "earshot and FFmpeg are both required")
class EarshotIntegrationTests(unittest.TestCase):
    def test_renders_an_earshot_cue_on_its_peak(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            video = make_test_media(folder)
            cues = folder / "cues.json"
            cues.write_text(json.dumps({"schemaVersion": "1.0.0", "cues": [
                {"id": "whoosh", "at": 1.5, "earshot": {"want": "a fast whoosh", "seed": 1},
                 "align": "peak", "gainDb": 0}]}), encoding="utf-8")
            report = sd.render(cues, video, folder / "out.mov", stems=True)
            self.assertEqual(report["creditsDetail"][0]["source"], "earshot")
            self.assertAlmostEqual(peak_time(Path(report["sfxStem"]), 1.0, 1.0),
                                   report["cues"][0]["time"], delta=0.01)


if __name__ == "__main__":
    unittest.main()
