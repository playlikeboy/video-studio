# Quality control

A successful process exit code does not prove a good video.

## Technical checks
- output exists and is non-zero
- full decode succeeds
- expected streams are present
- duration is within requested tolerance
- width/height/aspect ratio are correct
- frame rate and codec are correct
- audio is synchronized
- no unexpected clipping or silence
- file is playable in a standard player

## Visual checks
Inspect opening and closing, sample around important edit boundaries, inspect contact sheets, verify subject framing, text clipping/contrast/safe zones, transitions for black flashes or dropped frames, and caption accuracy/readability.

## Audio checks
Listen to representative beginning/middle/end; check speech/music balance, clipping, pops, unintended gaps and fades.

## Review loop
Preview → inspect → fix → final render → validate again. Separate machine-verified facts from subjective judgement. Report any uninspected or uncertain quality dimension honestly.
