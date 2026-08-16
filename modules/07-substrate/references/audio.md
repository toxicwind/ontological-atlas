# Audio analysis & separation reference

## demucs (CPU sandbox: 2 cores, 4GB)

- Model choice: `htdemucs` (default, fast), `htdemucs_ft` (fine-tuned, ~4x slower, better), `mdx_extra` (alternative). Models download once to `TORCH_HOME=/mnt/agents/output/av/torch_cache` (persistent).
- Command shape: `python3 av/stems.py track.mp3 htdemucs` → `av/stems/htdemucs/<track>/{bass,drums,other,vocals}.wav` at 44.1k stereo.
- Two-stem rescue mode: if a full run OOMs/fails, stems.py auto-retries `--two-stems vocals`.
- RAM guard: chunked demucs on CPU peaks ~1.5GB; do not run two separations concurrently.

## librosa profile fields (ana.py)

- `bpm` — global tempo via beat tracking; riddim/dubstep typically 140–150.
- `rms_mean`/`rms_max` — short-time RMS; loudness proxy (use luf.py for real LUFS).
- `centroid_hz` — brightness; sub-heavy riddim sits low (often <1.5kHz mean).
- `harmonic_rms` vs `percussive_rms` — HPSS split; riddim is percussive-dominant with strong harmonic bass layer.
- `onset_mean` — transient density.

## Loudness (luf.py via ffmpeg ebur128)

- Streaming targets: integrated ≈ -14 LUFS (Spotify), -9 to -6 LUFS common for self-released riddim masters. True peak ≤ -1 dBTP.
- LRA < 4 LU on riddim is normal (heavily compressed); >10 LU means very dynamic.

## .als internals (als.py)

- .als = gzip'd XML. `dec` pretty-prints; `sum` extracts: Live version (Creator), tempo (Manual), track names, device classes, plugin names (regex list covers Serum 2, ShaperBox, OTT, Multipass, FabFilter, Kontakt — extend regex in als.py as needed).
- Warp markers, clip gain, macro mappings are plain XML attributes — grep the decompiled XML directly.
