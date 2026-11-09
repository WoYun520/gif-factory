#!/usr/bin/env python3
"""Compose exactly nine decoded four-second videos into a labelled nine-grid."""
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--videos',nargs=9,required=True);p.add_argument('--labels',nargs=9,required=True);p.add_argument('--out',required=True);p.add_argument('--font');a=p.parse_args()
font=a.font or next((x for x in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/System/Library/Fonts/Supplemental/Arial.ttf'] if Path(x).exists()),None)
if not font:raise SystemExit('Provide a readable TTF/OTF via --font')
out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True);cmd=['ffmpeg','-hide_banner','-loglevel','error'];filters=[]
for v in a.videos:cmd+=['-i',v]
for i,title in enumerate(a.labels):
    if any(c in title for c in "':;[]\\\n"):raise SystemExit('Use simple labels without filter delimiters')
    filters.append(f"[{i}:v]fps=30,scale=480:320,pad=480:480:0:64:color=0x1d1e21,drawbox=x=1:y=1:w=478:h=478:color=0x35363b:t=1,drawtext=fontfile='{font}':text='{i+1:02}  {title}':fontsize=16:fontcolor=0x989ba5:x=24:y=432[c{i}]")
filters.append(''.join(f'[c{i}]' for i in range(9))+'xstack=inputs=9:layout=0_0|480_0|960_0|0_480|480_480|960_480|0_960|480_960|960_960[v]')
subprocess.run(cmd+['-filter_complex',';'.join(filters),'-filter_complex_threads','2','-map','[v]','-t','4','-r','30','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(out)+'.mp4'],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','3','-i',str(out)+'.mp4','-frames:v','1','-y',str(out)+'.png'],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(out)+'.mp4','-filter_complex','[0:v]fps=20,scale=1080:1080,split[a][b];[a]palettegen=max_colors=256:reserve_transparent=0[p];[b][p]paletteuse=dither=none','-loop','0','-y',str(out)+'.gif'],check=True)
print(str(out))
