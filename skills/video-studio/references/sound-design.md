# Sound design

Use the bundled `scripts/sound_design.py` (in this Skill's folder) to give an edit its sound
effects, an optional music bed, ducking and a loudness-normalised master. It needs Python 3.10+,
FFmpeg and FFprobe. It uses only the standard library. earshot is needed only for cues that ask
it for a sound. The network is used only for Openverse cues, and only when you pass
`--allow-network`.

## What it does

1. Probes the video for its duration, exact frame rate (for example `30000/1001`) and audio.
2. Snaps every cue to a frame, then converts that frame to an exact 48 kHz sample. NTSC rates
   do not drift. `align: "peak"` puts the loudest moment of the sound on the frame instead of
   its first sample, so a whoosh or hit lands on the cut.
3. Gets each sound from one of three sources:
   - **earshot** renders a new take from words on the CPU.
   - **file** uses a local recording, given as a path relative to the cue list.
   - **openverse** searches openly licensed audio and downloads one result.
4. Keeps the video's own audio (voice and music). It adds the effects on top and sidechain-ducks
   the music bed under the original audio, or under a separate voice stem given in `duck.key`.
5. Measures loudness with FFmpeg `loudnorm` (EBU R128) and applies the gain that reaches the
   target (default -14 LUFS integrated). A 4x-oversampled limiter holds the true-peak ceiling.
   Then it measures again, and corrects once if needed.
6. Muxes the new audio into a **new** file. The video stream is copied, not re-encoded. Then it
   measures the delivered file.

Each output gets four files beside it:

- `OUT.sound-design.json`: the resolved frames, samples, sources, loudness before and after,
  and warnings.
- `OUT.credits.md`: one line per sound with its licence.
- `OUT.sfx.wav`: the effects bus on its own. Written only with `--stems`.
- `cache/sound-design/OUT/`: renders and downloads, reused on the next run.

## Commands

```bash
S=.claude/skills/video-studio/scripts        # or wherever this Skill is installed
python3 $S/sound_design.py detect-cuts footage/edit.mp4 --sound "a short soft whoosh" -o sound/cues.json
python3 $S/sound_design.py validate sound/cues.json
python3 $S/sound_design.py plan sound/cues.json --video footage/edit.mp4          # frames + samples, no rendering
python3 $S/sound_design.py search "calm ambient piano" --category music          # licence, attribution, duration
python3 $S/sound_design.py render sound/cues.json --video footage/edit.mp4 -o exports/edit_sound.mp4 --stems
python3 $S/sound_design.py render sound/cues.json --video footage/edit.mp4 -o exports/edit_sound.mp4 \
    --allow-network --licenses cc0,pdm          # only when the cue list has Openverse sources
```

The tool finds earshot in this order: the in-process Python package, `--earshot-bin`,
`$EARSHOT_BIN`, `earshot` on PATH, then the isolated environment that
`scripts/install.py --with-tools earshot` creates. If earshot is missing, the error names the
install command.

## Cue list

```json
{
  "schemaVersion": "1.0.0",
  "cues": [
    {"id": "hook", "at": 0.0, "earshot": "a fast airy whoosh", "gainDb": -6},
    {"id": "title", "frame": 42, "earshot": {"want": "a heavy soft thump", "sound": "title/bag", "seed": 1}, "align": "peak"},
    {"id": "tap", "at": "00:00:03.200", "file": "sfx/tap.wav", "duration": 0.3, "license": "CC0-1.0"},
    {"id": "shutter", "at": 5.5, "openverse": {"q": "camera shutter", "maxDuration": 3}}
  ],
  "music": {"openverse": {"q": "calm ambient piano", "category": "music"}, "gainDb": -18, "fadeIn": 1, "fadeOut": 2, "loop": true},
  "duck": {"thresholdDb": -30, "ratio": 8, "attackMs": 20, "releaseMs": 350},
  "original": {"keep": true, "gainDb": 0},
  "loudness": {"integrated": -14, "truePeak": -1.5, "lra": 11}
}
```

- Give each cue `at` (seconds or `[HH:]MM:SS.mmm`) or `frame`, never both.
- Give each cue exactly one source: `earshot`, `file` or `openverse`.
- `earshot` takes words, or `{want, sound, seed, dur}`. `sound` locks a design id from
  `earshot sounds`. `seed` gives another take of the same request.
- `openverse` takes a query, or `{q, licenses, category, minDuration, maxDuration, index, id}`.
  After you choose a result, lock it with `id`. The next render is then reproducible, and a
  cached download needs no network.
- `gainDb` sets the cue level. The default is -6 dB for effects and -18 dB for music. The final
  loudness pass sets the overall level, so `gainDb` only balances the sounds against each other.
- `duck.key` takes a relative path to a voice stem. Use it when the original audio is music,
  not speech.
- File paths must be relative to the cue list's folder. Absolute paths and `..` are rejected.
- The repository checkout has a full example at `examples/sound-design/cues.json`.

## Find the moments

Use the best source you have:

1. **Times the edit already knows.** Use the project manifest, the timeline in a FableCut or
   HyperFrames project, caption timings or the EDL. These times are exact. Prefer them.
2. **Hard cuts.** `detect-cuts` uses FFmpeg's scene score and needs no other dependency. Its
   draft uses `align: "peak"` and one sound for every cut. Edit the draft: not every cut needs a
   sound.
3. **Your own review.** Look at frames around a moment, for example with a contact sheet. Write
   the frame where the motion **starts**, not the still frame after it.

Do not put a sound on every cut. Leave silence where the picture is calm. Use one family of
sounds per film. Keep effects quieter than dialogue.

## Licences and credits

- Openverse accepts only `cc0` and `pdm` by default. These need no attribution.
- Add CC BY only on purpose, for example `--licenses cc0,pdm,by` or `licenses` in the cue. The
  render then sets `attributionRequired: true` in the report. The credits file holds each
  creator's attribution text from Openverse. Publish it with the video.
- Every search result is filtered by licence again after the API returns it. A locked `id` with
  a licence outside the allowed set is refused.
- NC, ND and sampling licences print a warning. Do not use them for commercial work, or where
  the mix would count as an adaptation the licence forbids, unless the user confirms it.
- earshot renders are free for any use and need no credit. The credits file still names the
  design for each one.
- A local `file` has no known licence until you record it in the cue (`"license": "..."`). The
  credits file flags every local file without one.
- Downloads use HTTPS only. Each download has a 64 MB limit. Nothing is uploaded. Treat
  downloaded audio as untrusted media.

## Check before delivery

- Read the report. The output must be within 1 LU of the target, and the true peak must be at
  or under the ceiling. AAC can overshoot the ceiling by about a dB. A warning says when it
  does. Deliver `.mov` or `.mkv` (PCM audio) when the true peak must be exact.
- With `--stems`, check that the effect peaks sit on the cue times in `OUT.sfx.wav`.
- Listen to the start, the end, every ducked passage and the loudest cue. If you cannot listen,
  say what was measured and what still needs a human to hear it. Do not claim the mix "sounds
  good". earshot's `describe` and `timeline` commands (the `listen` extra) can describe a mix in
  words. They do not replace a listener.
- Never overwrite the source. The tool refuses `-o` equal to the input, and refuses an existing
  output without `--overwrite`.

## Credits

- [earshot](https://github.com/Leonxlnx/earshot) by Leon Lin (MIT). It renders sound effects
  on the CPU from a catalogue learned from public-domain recordings. Install it from GitHub:
  `pip install "earshot @ git+https://github.com/Leonxlnx/earshot"`. The `earshot` name on
  PyPI belongs to another project.
- [Clipwing real-sfx](https://github.com/Clipwing/skills/tree/main/skills/real-sfx). Its
  approach shaped this tool: cue lists, frame-exact placement, keeping music and voice, a
  separate SFX track and peak alignment. It places real recordings from the user's own
  library. Use it when the user has such a library. No Clipwing code or audio is included here.
- [Openverse](https://github.com/WordPress/openverse) (WordPress). It is a search engine for
  openly licensed media, and its public API returns the licence and attribution for each item.
  Each item keeps its own licence.
