---
name: pixel-gif-sticker-pack
description: Turn an authorized character illustration, mascot, or rendered 3D reference into a pack of individually animated chat sticker GIFs, with a playable preview and verified ZIP. Use for single packs and large themed series with distinct expressions and gestures.
---

# Animated chat sticker packs

Carry forward the latest reference, required count, format, language, and visual constraints. For a GLB, render a front or three-quarter reference with the face and identifying details visible. If the user supplied a drawing, preserve the recognizable silhouette, facial features, palette, and signature accessories. Use only imagery the user provided or authorized for the task.

## Design and generate

- For a large pack, plan categories first and give each sticker a chat line, a visible pose or prop, and an animated beat. Review neighboring concepts for semantic duplicates. An identical pose with new text alone is insufficient.
- Use the image generation tool for new pose art. Ask for one transparent sprite atlas at a time, usually a 4 × 4 sheet with wide gutters and no lettering. Give exact reading order, stable framing and identity anchors. Keep lettering in composition, where it can be verified.
- Inspect each atlas at full size. Count actual occupied cells, map each cell to its visible pose, and correct a mismatched caption or regenerate an unusable sprite. Watch for swapped cells, clipped hair or hands, and artifacts across gutters. A 100-sticker pack needs 100 accepted entries.
- For tiny chat previews, prefer strong readable facial expressions, a short caption and one clear moving accent. Let each motion settle naturally into the next loop. Keep the original source and generated atlases outside the shareable ZIP unless requested.

## Articulated actions

When the user asks a character to wave, give a thumbs-up, shrug, pump a fist, make a heart, or otherwise move a limb, use [the keyframe workflow](references/keyframes.md) and `scripts/export_keyframes.py`. Generate consecutive poses of the same character and compose them with shared alignment. Keep photographic and anime rendering styles as requested. Whole-sprite deformation alone does not fulfill a request for articulated motion.

For subtle idle movement or a large pack of distinct static poses, the existing motion-preset exporter remains appropriate. Keyframe GIFs may have visible pose transitions or identity drift; inspect them and describe material limits. Use a video or rigged compositor only when needed for genuinely smooth continuous motion, preserving the user's chosen provider and method.

## Automatic clear rendering

The bundled exporter now defaults to **hd**: it renders directly from original atlas crops into 512 × 512 frames with LANCZOS resizing and BICUBIC continuous deformation. Use this default for photographic people, realistic pets and detailed illustration. A user invoking this Skill does not need to request a separate clarity fix or edit a compositor.

- Preserve the accepted face, expression, caption and pose while exporting. For a named person with an ambiguous name, resolve the identity from the user's handle or reference before generating it.
- Use `--render-style pixel` (or manifest `"render_style": "pixel"`) only when the user explicitly wants pixel art or the reference is intentionally pixel-based. That mode preserves the original 320 × 320 pixel pipeline. The CLI flag overrides the manifest.
- HD previews default to a clean grid without headings and are assembled from decoded final GIFs; `--preview-layout chapters` opts into category headings. Follow any explicit user choice about preview titles.
- If a face still looks blurry, inspect the original crop and decoded output at the same display size. Read [the clarity guide](references/clarity.md) for source-resolution limits and before/after validation. Enlarging an already pixelated export cannot recover lost details.

## Compose and verify

For a repeatable workflow, use [the atlas exporter](scripts/export_pack.py) with Python 3 and Pillow. It uses FFmpeg for MP4 playback. Run `python3 scripts/export_pack.py --help` and read [the manifest format](references/manifest.md) for cell overrides and motion presets. Choose a local font that covers the requested captions. Use another compositor when the brief requires actual skeletal or frame-by-frame character animation.

Deliver one transparent looping GIF per entry, grouped in a ZIP. Default to clear 512 × 512 GIFs and roughly two seconds per loop; use 320 × 320 only for the intentional pixel path. Respect explicit target-platform size limits with an appropriate compositor or final downsampling, then re-verify the result. A separate MP4 assembled from the decoded GIFs makes playback inspectable even in a chat surface that shows a still. A static contact sheet can help compare designs when clearly identified as a still.

Verify exact count and unique captions, visible movement, frame timing, loop flag, alpha, safe margins, ZIP integrity and MP4 decoding. Inspect each category visually. Report actual deliverables and any limits that affect use. A local playback check does not establish compatibility with a specific messaging platform.
