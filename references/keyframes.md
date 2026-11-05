# Articulated GIF actions

Use this workflow when the requested gesture changes arms, hands or another body part. `export_pack.py` moves and deforms a single pose; `export_keyframes.py` sequences distinct, generated poses. Both produce transparent 512px GIFs by default, but only the latter depicts a limb changing pose.

## Generate and inspect consecutive poses

- Plan a short gesture with 3–8 key poses. For example: hand low → forearm halfway up → thumb at chest → thumb beside cheek. A return sequence can reuse cells in reverse order. Keep lettering out of generated art.
- Put one character's consecutive poses in one row of an equal-grid transparent atlas. Specify fixed head center, camera, lighting, scale, clothes and torso baseline. Change the intended limb or expression only. Each frame must include complete hair, hats, elbows and fingers, with clear gutters.
- Use the reference image for photographic identity; retain anime styling for illustrated characters. Inspect every cell. Regenerate clipped limbs or missing headroom, and ask the image tool to restore genuine transparency if a background was baked in. A transparency request alone is not proof of alpha-zero pixels.
- Keep cells in a shared coordinate system. Do not independently crop and fit each pose: a moving hand can change the bounding box and make the head jump or zoom. The exporter takes the union of the pose bounds, then applies one common fit to all frames.
- Inspect a full loop for identity drift and hand anatomy. Distinct frames alone do not prove a coherent gesture. This is key-pose animation, not optical-flow interpolation or guaranteed video-smooth motion. Prefer a small accepted sample before expanding a large action pack.

## Manifest and export

Use a separate keyframe manifest with the familiar `title`, `count` and `groups` fields. Paths are relative to the manifest; cells are zero-based. Frame order is time order and repeated cells are allowed.

```json
{
  "title": "点赞小样",
  "count": 1,
  "groups": [{
    "name": "点赞",
    "atlas": "thumbs-up.png",
    "grid": [4, 1],
    "entries": [{
      "name": "人物-稳了",
      "text": "稳了",
      "frames": [
        {"cell": [0, 0], "duration": 320},
        {"cell": [1, 0], "duration": 120},
        {"cell": [2, 0], "duration": 120},
        {"cell": [3, 0], "duration": 320},
        {"cell": [2, 0], "duration": 120},
        {"cell": [1, 0], "duration": 120}
      ]
    }]
  }]
}
```

```sh
python3 scripts/export_keyframes.py actions.json build --font /path/to/font.ttf --preview
```

`duration` is milliseconds, defaults to 120, and must be a positive multiple of 20. The example loops in 1.12 seconds. Optional entry `ink` changes caption color. `name` controls the filename; it does not change the visible caption. A frame can override `crop: [left, top, right, bottom]`, but crops must retain the grid cell dimensions (within one pixel) and common alignment. Use another compositor for differently framed or differently sized source images. Optional top-level `credits` is written into the ZIP as a source/production note.

The compositor uses source-resolution LANCZOS sampling, one shared crop and scale, 512 × 512 output, native-size captions and a shared GIF palette. It does not apply the single-pose squash or motion presets. It writes categorized GIFs, an offline gallery and a verified ZIP; `--preview` adds a header-free MP4 assembled from decoded GIFs with their actual timing. Previews paginate at 16 stickers and play each page for three cycles of its longest loop.

Verification covers exact count, distinct files, visible frame changes, transparency, safe margins, loop timing and ZIP contents. Visually check actual playback too, including the return to the first pose. Do not claim that the single-pose exporter's `frames` input exists; use this separate script for keyframe manifests.
