# Performance engineering

## Goals

Make common edits fast without reducing output quality or making false speed claims.

## Strategy
- Stream-copy for compatible trims/remuxes. Document keyframe precision limitations.
- Proxy generation for fast visual review.
- Cache media probe results by file fingerprint.
- Cache transcripts by source fingerprint, model and configuration.
- Cache scene analysis and contact sheets.
- Use bounded concurrency and avoid CPU/GPU oversubscription.
- Detect hardware encoders before use.
- Avoid repeated intermediate transcoding.
- Render low-resolution proof before high-quality output.
- Reuse rendered segments when the composition graph makes that safe.

## Encoder selection

Inspect the actual FFmpeg build and available encoders. On macOS, check VideoToolbox; on NVIDIA systems, check NVENC; on Intel/AMD systems, check QSV/AMF paths. Keep a tested software fallback.

Hardware encoder presets and quality controls vary. Validate output visually and technically. Do not claim acceleration is active unless the selected encoder was actually used.
