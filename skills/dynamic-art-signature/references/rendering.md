# Renderer configuration

Use `render_signature.py inspect --image FILE` to list component IDs, areas and bounds at the intended output size. JSON paths are relative to the JSON file. Python packages: Pillow, numpy, scipy. External commands: ffmpeg, ffprobe. No API key is required by the local compositor; artwork generation uses the host's image tool separately.

Minimal configuration:

```json
{
  "image": "art.png",
  "width": 960,
  "height": 640,
  "foreground_threshold": 60,
  "upper_components": [1],
  "background": "1d1e21",
  "key_color": "202124",
  "timing": {"upper_start": 0.3, "upper_duration": 0.14, "gap": 1.02,
             "body_duration": 0.18, "terminal_duration": 0.72, "duration": 4.0}
}
```

For RGBA art with actual transparency, use its alpha for segmentation and compositing. For opaque dark art, component detection uses luma; adjust threshold and keying to preserve fine gray strokes. The dark-background fallback is not suitable for dark accents on a dark ground. Inspect keyed edges; use genuine alpha or repair the artwork when ink/background are inseparable.

`upper_components` refers to the exact inspect result. All other foreground components belong to the second gesture. The nearest foreground owner extends the matte only through background/antialias pixels, avoiding broad masks that expose other strokes. Inspect that selected IDs represent the upper flourish, not letters or dots. Physical group separation is still a design prerequisite.

For returning tails add:

```json
"tail": {
  "coordinate_size": [960,640],
  "region_polygon": [[305,640],[960,640],[960,350],[900,350],[720,390],
                     [700,425],[620,433],[480,435],[400,460],[305,500]],
  "paths": [[[706,418],[770,418],[840,350],[872,402]],
            [[872,402],[907,460],[680,451],[565,461]],
            [[565,461],[460,465],[380,473],[320,496]]],
  "brush_width": 60
}
```

These example coordinates are **Aster only**. Trace the current design. Define the complete tail region, including its upper edge, before the body reveal. The tail region must exclude body ink; ensure its path touches the body's endpoint. The renderer checks that the final pen path covers the tail's foreground. Fix the region/path instead of filling missed ink in a final global wipe.

Without `tail`, the lower pass is a forward reveal: 78% is quick, remaining 22% decelerates. It is a fallback for forward terminals, not a true font-path tracer. The tool does not automatically recover calligraphic stroke order from arbitrary art. For complicated overlaps, generate separate alpha layers or provide an explicit motion compositor.

Run `audit_video.py output.mp4` for 4-second/60fps defaults and a uniform opening. Also decode a frame in the one-second gap and verify that the lower word is absent. Inspect playback at normal speed and frame-by-frame around the tail handoff; no automated color/count test proves that handwriting looks natural.

Use `make_grid.py --out /absolute/output/grid --videos FILE1 ... FILE9 --labels NAME1 ... NAME9` for 1440×1440 MP4, cover PNG and 1080×1080 GIF. Inputs must be four-second finished videos; labels are fixed outside the art. Preserve real timings while resampling. ZIP only final assets and useful configs, not intermediate mask frames or machine-specific absolute paths.
