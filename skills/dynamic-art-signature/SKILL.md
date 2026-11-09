---
name: dynamic-art-signature
description: Design original handwritten artistic signatures from a name, one object and a gradient palette, then render stroke-writing MP4/GIF animations and nine-grid collections. Use for 动态签名、艺术签名、名字＋物体＋渐变、两笔快写、书法收锋 or signature-grid requests. Supports new designs and timing repairs; does not replace ordinary document signing or character-sticker workflows.
---

# 动态艺术签名

## Preserve the brief

Carry forward the exact name, object, palette and latest accepted design. Ask only for missing essentials; choose names and motifs autonomously when requested. Separate **letter design**, **movement**, and **delivery layout**. For a timing-only revision, retain the artwork. Keep sample-specific choices such as an eye inside `e` out of the universal defaults.

## Design the shared letter/object silhouette

Read [design guidance](references/design.md). Use the available image-generation tool for new raster artwork and visual edits. Make the object part of the letter anatomy and negative space. Preserve legibility and original composition; borrow a reference's integration principle rather than its exact lettering. Use flat handwritten ink with natural pressure, thick/thin contrast and tapered terminals. “质感” defaults to handwriting, not metal, bevels, glow, extrusion or rough chalk.

Design two physically independent gesture groups: an upper blade/wing/flourish and lower lettering/tail. Leave a small intentional gap where they approach. If strokes touch, repair the artwork or supply explicit independent layer masks before animation. Do not divide a completed connected logo with a horizontal wipe and call it two independent strokes.

Use [the nine examples](references/examples.md) for range, not as mandatory templates. Inspect spelling and actual geometry before rendering. A static design preview does not complete an animation request.

## Animate the accepted two-gesture rhythm

Default to a flat opaque charcoal background, 960×640, 60fps MP4, 4-second loop, 25fps GIF. Respect explicit changes.

| Event | Default |
| --- | --- |
| Initial clean hold | 0.30s |
| Upper gesture | 0.14s, accelerating and decisive |
| Gap after upper completion | 1.02s |
| Lower gesture begins | 1.46s |
| Lower main body | roughly 0.16–0.18s |
| Final tail/terminal | another 0.65–0.72s, progressively slowing |
| Final hold / loop reset | hold the result, fade ink only during last 0.30s |

Keep the background completely free of future strokes. Composite revealed ink over a clean background; do not dim the full finished artwork underneath the reveal. Never add shake, spring/recoil, particles, glow or audio by default. These were rejected during refinement. An optional effect must be explicitly requested.

Read [render configuration and safeguards](references/rendering.md). Require Python 3, Pillow, NumPy, SciPy, FFmpeg and ffprobe. Run:

```bash
python scripts/render_signature.py inspect --image assets/examples/Aster.png
python scripts/render_signature.py render --config assets/examples/Aster.json --out /absolute/output/aster
python scripts/audit_video.py /absolute/output/aster.mp4
```

Use the inspect result to select component IDs **for that exact image and threshold**. Never reuse IDs blindly on a newly generated image. The compositor supports an optional vector-defined tail region/path. Give an actual sequential path for a returning tail; a left-to-right bounding-box wipe does not model a tail that returns leftward. For a design with a single forward terminal, the simpler decelerating reveal is acceptable if playback looks handwritten. Inspect intermediate frames, not just the completed logo.

## Repair failures before expanding

- **Future ink visible:** remove the underneath finished image; verify a uniform opening and blank lower group during the gap.
- **Two strokes bleed together:** inspect connected components, assign exclusive ownership, and repair physical joins. Do not rely on a wide brush mask over intersecting artwork.
- **Tail appears twice / has a seam:** keep the entire tail out of the body pass, then reveal it continuously from the body endpoint. Use a path matching its actual curve.
- **Mechanical slow tracing:** keep the main strokes fast and confine deceleration to the terminal.
- **Static masquerading as animation:** verify actual decoded intermediate states and timing.

Inspect normal playback, the upper-only hold, the body-to-tail handoff, slow terminal and loop reset. Technical checks are necessary but do not establish visual acceptance. Repair a failed sample before batching. Preserve confirmed settings in later iterations.

## Deliver and package

Deliver MP4 and a looping GIF; supply a static cover only as a labelled supplement. For nine-grid requests, make nine distinct name/object/palette designs and compose the **decoded finished videos**, not a static collage. Use `scripts/make_grid.py` with exactly nine videos. Keep a complete collection ZIP when requested, with individual media, covers and the configuration needed to reproduce them. Avoid including private user reference screenshots in public packages.

When incorporated into GIF Factory, link this module from the root purpose router while retaining `$pixel-gif-sticker-pack` compatibility. Preserve existing sticker, poster, lenticular, film and storybook routes. Do not replace the user's whole `gif-factory` with this module.
