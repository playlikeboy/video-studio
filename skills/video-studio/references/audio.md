# Audio production

## Workflow
1. Inspect audio streams, sample rate, channels and duration.
2. Identify speech/music/effects layers where useful.
3. Correct sync before mixing.
4. Denoise gently; preserve natural voice texture.
5. Apply EQ and compression only where appropriate.
6. Keep speech intelligible and music below narration.
7. Check peaks, loudness and clipping.
8. Listen to the final mix.

## Operations
Noise/hum reduction, de-reverb when supported, high-pass/low-pass, EQ, compression, limiting, voice leveling, music ducking, fades, crossfades, sync correction, sound-effect placement and channel routing.

For sound effects, music beds, sidechain ducking and loudness normalisation, use the bundled `scripts/sound_design.py`. See `references/sound-design.md`. It places each sound on an exact frame and ducks music under the original audio. It normalises the mix to -14 LUFS integrated with a true-peak ceiling and writes a credits file.

## Loudness targets
- Social and streaming (YouTube, Reels, Shorts, TikTok, Spotify video): -14 LUFS integrated, true peak -1.5 dBTP or lower.
- Broadcast (EBU R128): -23 LUFS; ATSC A/85: -24 LKFS. Use them only when the deliverable asks for them.
- Lossy encoders such as AAC can overshoot the true peak. Measure the delivered file, not only the mix.

Do not remove every breath or pause. Leave natural cadence and emphasis. Use ducking rather than simply lowering music for the entire clip when music should remain expressive between speech sections. Record source and license for music, ambience, sound effects and voice assets.
