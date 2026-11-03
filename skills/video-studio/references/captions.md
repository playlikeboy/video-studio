# Speech and captions

## Pipeline
1. Extract or select the best speech audio stream.
2. Transcribe only when captions or transcript-aware editing are needed.
3. Preserve original language unless translation is requested.
4. Use word alignment where accurate word-level animation is needed.
5. Review names, technical terms, code, numbers and multilingual text.
6. Apply line-length, reading-speed and safe-zone constraints.
7. Export requested subtitle formats and/or burn captions.
8. Inspect caption timing against final video.

## Optional engines
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- WhisperX: https://github.com/m-bain/whisperX

These are optional and may require substantial model downloads and compute. Do not download large models without checking disk and compute and explaining installation.

Use a coherent type system, consistent line width, readable contrast and safe placement. Highlight only selected keywords; avoid flashing every word unless the chosen template calls for it. Select fonts that support the script and language.

Formats: SRT, WebVTT, ASS, burned-in subtitles and soft subtitles embedded in video.
