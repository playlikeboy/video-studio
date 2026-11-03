# Editing operations

## Operation vocabulary

### Timeline
- probe, trim, cut, split, join, concatenate
- insert, reorder, duplicate, remove, ripple-delete
- speed, reverse, freeze-frame, loop
- fade, crossfade, transition, hold-frame
- extract-frame, extract-audio, extract-subclip

### Image and video
- crop, scale, pad, rotate, flip
- reframe, stabilize, deinterlace
- color-correct, apply-LUT, denoise-video
- blur, sharpen, vignette, grain
- watermark, overlay, picture-in-picture
- chroma-key, mask, track, composite

### Audio
- normalize, loudness-normalize, gain, fade
- denoise, high-pass, low-pass, EQ, compress, limit
- mix, duck, sync, loop, crossfade
- detect-silence and extract-stems when supported

### Captions and graphics
- transcribe, align, subtitle-import, subtitle-export
- burn-captions, style-captions, highlight-words
- title-card, lower-third, logo, callout, diagram, chart

## Fast-path rules

### Stream-copy
Use stream-copy when no per-frame visual filter is required, source codecs/container are compatible and keyframe boundaries are acceptable for the requested precision. Be honest: seeking/copy behavior can produce cuts at nearby keyframes rather than exact requested frames.

### Re-encode
Use when cropping/scaling/rotation changes pixels, adding transitions/compositing/captions, changing frame rate/timebase or joining incompatible streams. Avoid multiple lossy intermediate encodes; prefer a single final encode.

## Safe editing
- Use a new output path.
- Never overwrite input unless explicitly requested and the tool supports safe replacement.
- Validate timestamps and ensure start < end.
- Check source duration.
- Escape/filter values passed to shell commands; do not interpolate untrusted filenames into shell strings.
- Prefer argument arrays/subprocess APIs over shell concatenation.
