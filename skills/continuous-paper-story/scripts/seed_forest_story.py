#!/usr/bin/env python3
"""Copy the bundled runnable baseline without overwriting an existing project."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil


def seed(destination: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / 'assets' / 'forest-sharing-template'
    manifest = json.loads((root / 'assets' / 'forest-sharing-baseline.json').read_text())
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise SystemExit(f'目标目录已存在，未写入：{destination}')
    for name, expected in manifest['files'].items():
        item = source / name
        if not item.is_file() or hashlib.sha256(item.read_bytes()).hexdigest() != expected:
            raise SystemExit(f'基准素材校验失败：{name}')
    shutil.copytree(source, destination)
    print(f'已复制森林纸艺基准：{destination}')
    print('当前仍为《留一半给你》样例；先改story-plan.json与assets/sharing.js，再制作新故事。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    seed(parser.parse_args().destination)
