#!/usr/bin/env python3
"""Local reference sampling. Contact sheets locate beats; they do not grade motion."""
import argparse
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--sample-fps', type=float, default=6)
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--duration', type=float)
    ap.add_argument('--max-frames', type=int, default=180)
    args = ap.parse_args()
    if not args.input.is_file():
        ap.error('input must be an existing video')
    if not math.isfinite(args.sample_fps) or not 0 < args.sample_fps <= 120:
        ap.error('sample-fps must be finite and in (0,120]')
    if not math.isfinite(args.start) or args.start < 0:
        ap.error('start must be finite and nonnegative')
    if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0):
        ap.error('duration must be finite and positive')
    if args.max_frames < 1:
        ap.error('max-frames must be positive')
    for tool in ('ffprobe', 'ffmpeg'):
        if not shutil.which(tool):
            ap.error(tool + ' is required')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                            '-of', 'json', str(args.input.resolve())],
                           check=True, capture_output=True, text=True)
    raw = json.loads(probe.stdout)
    stream = next((s for s in raw['streams'] if s.get('codec_type') == 'video'), None)
    if not stream:
        ap.error('input has no video stream')
    total = float(raw['format']['duration'])
    if args.start >= total:
        ap.error('start must be before the video end')
    duration = min(args.duration if args.duration else total, total - args.start)
    if math.ceil(duration * args.sample_fps) > args.max_frames:
        ap.error('range exceeds max-frames; reduce duration/rate or explicitly increase max-frames')
    if args.out.exists() and any(args.out.iterdir()):
        ap.error('out must be a new or empty directory to avoid mixing review runs')
    args.out.mkdir(parents=True, exist_ok=True)
    frame_dir = args.out / 'frames'
    frame_dir.mkdir()
    # Input seek is re-encoded, not stream copied. Labels describe a regular sampling grid.
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(args.start),
                    '-i', str(args.input.resolve()), '-t', str(duration), '-an',
                    '-vf', 'fps={}:start_time=0,scale=480:-2'.format(args.sample_fps),
                    '-frames:v', str(args.max_frames), str(frame_dir / 'frame-%05d.jpg')], check=True)
    files = sorted(frame_dir.glob('frame-*.jpg'))
    if not files:
        raise RuntimeError('No sampled frames were produced')
    with Image.open(files[0]) as first:
        fw, fh = first.size
    per_sheet, cols, label_h = 16, 4, 24
    sheets = []
    for page, offset in enumerate(range(0, len(files), per_sheet), 1):
        subset = files[offset:offset + per_sheet]
        rows = math.ceil(len(subset) / cols)
        sheet = Image.new('RGB', (fw * cols, (fh + label_h) * rows), '#242424')
        draw = ImageDraw.Draw(sheet)
        for j, file in enumerate(subset):
            x, y = j % cols * fw, j // cols * (fh + label_h)
            with Image.open(file) as frame:
                sheet.paste(frame, (x, y + label_h))
            stamp = args.start + (offset + j) / args.sample_fps
            draw.text((x + 6, y + 5), '{:.3f}s sample'.format(stamp), fill='white')
        name = 'sheet-{:02d}.jpg'.format(page)
        sheet.save(args.out / name, quality=90)
        sheets.append(name)
    def rate(name):
        try:
            return float(Fraction(stream.get(name, '0/1')))
        except (ValueError, ZeroDivisionError):
            return None
    result = {
        'source_name': args.input.name,
        'width': stream['width'], 'height': stream['height'],
        'duration_seconds': total, 'nominal_fps': rate('r_frame_rate'),
        'average_fps': rate('avg_frame_rate'), 'reported_frames': stream.get('nb_frames'),
        'has_audio': any(s.get('codec_type') == 'audio' for s in raw['streams']),
        'sampling': {'start': args.start, 'duration': duration, 'fps': args.sample_fps,
                     'count': len(files), 'sheets': sheets,
                     'labels': 'sampling grid; not exact source frame timestamps'},
        'acceptance': {'technical': 'sampling_complete', 'visual': 'not_reviewed', 'user': 'pending'}
    }
    (args.out / 'reference.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
