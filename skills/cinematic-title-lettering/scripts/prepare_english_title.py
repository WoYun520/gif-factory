#!/usr/bin/env python3
"""Prepare reference-guided English lettering inputs without calling an API."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style',required=True,help='EN01–EN50, original R id, or font name')
    parser.add_argument('--title',required=True)
    parser.add_argument('--scene',default='')
    parser.add_argument('--photo',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    catalog=json.loads((root/'assets/english-titles/catalog.json').read_text(encoding='utf-8'))
    key=args.style.strip().casefold()
    item=next((s for s in catalog['items'] if key in (s['id'].casefold(),s['font_id'].casefold(),s['font_name'].casefold())),None)
    if item is None:parser.error('Unknown style; use an EN id, R id, or exact font name from the catalog.')
    title=args.title.strip()
    if not title:parser.error('Title must not be blank.')
    references=[str(root/item['specimen']),str(root/item['frame'])]
    if args.photo:
        photo=args.photo.expanduser().resolve()
        if not photo.is_file():parser.error('Photo does not exist: '+str(photo))
        references.append(str(photo))
    prompt=(
        'Use case: ads-marketing. Create one English cinematic title design. '
        'Image 1 is a real font specimen: use its letter skeleton, stroke weight, joins and counters, '
        'and ignore its sample words and font labels. Image 2 is the decorative lettering reference: '
        'use its scale contrast and stroke-to-scene relationships, not its old title or photograph. '
        'Exact new title, each word once in the supplied order: '+json.dumps(title,ensure_ascii=False)+'. '
        'Base font: '+item['font_name']+'. Decoration direction: '+item['lettering_notes']+' '
        'The decoration notes describe the example; adapt their anchor letters and word groups to the NEW title. '
        'Use only the new title as visible wording. Thin handwriting stays thin; chunky print stays print. '
        'Grow decoration from actual letters rather than detached icons. Preserve clear spelling and counters. '
        'Keep every ascender, descender and flourish inside frame with breathing room. '
        'No copied example wording, Chinese text, labels, logos, credits or watermarks. '
    )
    if args.photo:
        prompt+='Image 3 is the final scene photograph. Preserve its framing, objects, lighting and material texture; change only the title and its decoration. '
    elif args.scene:
        prompt+='Make a new photorealistic scene: '+args.scene+'. One ultrawide frame, approximately 2.38:1. '
    else:
        prompt+='Create lettering only on a plain white background; no scene or extra captions. '
    prompt+='Final visible text must be exactly '+json.dumps(title,ensure_ascii=False)+'. Do not use any example title from the references or decoration notes. '
    value={'style':item['id'],'font_id':item['font_id'],'font_name':item['font_name'],'title':title,
           'base_font_file':str(root/item['font_file']),
           'imagegen_args':{'prompt':prompt,'referenced_image_paths':references,'transparent_background':False}}
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding='utf-8')
    else:print(text,end='')


if __name__=='__main__':main()
