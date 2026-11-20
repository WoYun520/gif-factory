#!/usr/bin/env python3
"""Compare the decoded video frames of an approved shot against a new master."""
import argparse
import subprocess
import sys
from pathlib import Path


def fingerprints(path, start, count):
    if not path.is_file():
        raise ValueError(f'找不到视频：{path}')
    selection = f'select=between(n\\,{start}\\,{start + count - 1})'
    result = subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path.resolve()),
        '-map', '0:v:0', '-an', '-vf', selection, '-fps_mode', 'passthrough',
        '-frames:v', str(count), '-f', 'framemd5', '-'
    ], capture_output=True, text=True, check=True)
    lines = result.stdout.splitlines()
    geometry = next(line for line in lines if line.startswith('#dimensions'))
    hashes = [line.rsplit(',', 1)[-1].strip() for line in lines if line and not line.startswith('#')]
    if len(hashes) != count:
        raise ValueError(f'{path.name} 从第 {start} 帧起只读到 {len(hashes)} 帧，期望 {count} 帧')
    return geometry, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--reference-start', type=int, default=0)
    parser.add_argument('--candidate-start', type=int, default=0)
    parser.add_argument('--frames', type=int, required=True)
    args = parser.parse_args()
    if min(args.reference_start, args.candidate_start) < 0 or args.frames < 1:
        parser.error('起始帧必须非负，帧数必须大于零')
    try:
        old_size, old = fingerprints(args.reference, args.reference_start, args.frames)
        new_size, new = fingerprints(args.candidate, args.candidate_start, args.frames)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(getattr(exc, 'stderr', None) or str(exc), file=sys.stderr)
        return 2
    if old_size != new_size:
        print(f'尺寸不同：{old_size} / {new_size}')
        return 1
    for offset, (before, after) in enumerate(zip(old, new)):
        if before != after:
            print(f'首个画面差异：参考帧 {args.reference_start + offset}，新版帧 {args.candidate_start + offset}')
            return 1
    print(f'{args.frames} 帧解码画面一致。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
